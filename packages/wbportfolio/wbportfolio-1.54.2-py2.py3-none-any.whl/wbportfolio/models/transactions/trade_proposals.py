import logging
import math
from contextlib import suppress
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, TypeVar

from celery import shared_task
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from pandas._libs.tslibs.offsets import BDay
from wbcompliance.models.risk_management.mixins import RiskCheckMixin
from wbcore.contrib.authentication.models import User
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton
from wbcore.models import WBModel
from wbcore.utils.models import CloneMixin
from wbfdm.models import InstrumentPrice
from wbfdm.models.instruments.instruments import Cash, Instrument

from wbportfolio.models.roles import PortfolioRole
from wbportfolio.pms.trading import TradingService
from wbportfolio.pms.typing import Portfolio as PortfolioDTO
from wbportfolio.pms.typing import TradeBatch as TradeBatchDTO

from ..asset import AssetPosition, AssetPositionIterator
from .trades import Trade

logger = logging.getLogger("pms")

SelfTradeProposal = TypeVar("SelfTradeProposal", bound="TradeProposal")


class TradeProposal(CloneMixin, RiskCheckMixin, WBModel):
    trade_date = models.DateField(verbose_name="Trading Date")

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMIT = "SUBMIT", "Submit"
        APPROVED = "APPROVED", "Approved"
        DENIED = "DENIED", "Denied"
        FAILED = "FAILED", "Failed"

    comment = models.TextField(default="", verbose_name="Trade Comment", blank=True)
    status = FSMField(default=Status.DRAFT, choices=Status.choices, verbose_name="Status")
    rebalancing_model = models.ForeignKey(
        "wbportfolio.RebalancingModel",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="trade_proposals",
        verbose_name="Rebalancing Model",
        help_text="Rebalancing Model that generates the target portfolio",
    )
    portfolio = models.ForeignKey(
        "wbportfolio.Portfolio", related_name="trade_proposals", on_delete=models.PROTECT, verbose_name="Portfolio"
    )
    creator = models.ForeignKey(
        "directory.Person",
        blank=True,
        null=True,
        related_name="trade_proposals",
        on_delete=models.PROTECT,
        verbose_name="Owner",
    )

    class Meta:
        verbose_name = "Trade Proposal"
        verbose_name_plural = "Trade Proposals"
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "trade_date"],
                name="unique_trade_proposal",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.trade_date and self.portfolio.assets.exists():
            self.trade_date = (self.portfolio.assets.latest("date").date + BDay(1)).date()

        # if a trade proposal is created before the existing earliest trade proposal, we automatically shift the linked instruments inception date to allow automatic NAV computation since the new inception date
        if not self.portfolio.trade_proposals.filter(trade_date__lt=self.trade_date).exists():
            new_inception_date = (self.trade_date + BDay(1)).date()
            self.portfolio.instruments.filter(inception_date__gt=new_inception_date).update(
                inception_date=new_inception_date
            )
        super().save(*args, **kwargs)

    @property
    def check_evaluation_date(self):
        return self.trade_date

    @property
    def checked_object(self) -> Any:
        return self.portfolio

    @cached_property
    def portfolio_total_asset_value(self) -> Decimal:
        return self.portfolio.get_total_asset_value(self.last_effective_date)

    @cached_property
    def validated_trading_service(self) -> TradingService:
        """
        This property holds the validated trading services and cache it.This property expect to be set only if is_valid return True
        """
        target_portfolio = self._build_dto().convert_to_portfolio()

        return TradingService(
            self.trade_date,
            effective_portfolio=self._get_default_effective_portfolio(),
            target_portfolio=target_portfolio,
            total_target_weight=target_portfolio.total_weight,
        )

    @cached_property
    def last_effective_date(self) -> date:
        try:
            return self.portfolio.assets.filter(date__lt=self.trade_date).latest("date").date
        except AssetPosition.DoesNotExist:
            return (self.trade_date - BDay(1)).date()

    @property
    def previous_trade_proposal(self) -> SelfTradeProposal | None:
        future_proposals = TradeProposal.objects.filter(portfolio=self.portfolio).filter(
            trade_date__lt=self.trade_date, status=TradeProposal.Status.APPROVED
        )
        if future_proposals.exists():
            return future_proposals.latest("trade_date")
        return None

    @property
    def next_trade_proposal(self) -> SelfTradeProposal | None:
        future_proposals = TradeProposal.objects.filter(portfolio=self.portfolio).filter(
            trade_date__gt=self.trade_date, status=TradeProposal.Status.APPROVED
        )
        if future_proposals.exists():
            return future_proposals.earliest("trade_date")
        return None

    @property
    def base_assets(self) -> dict[int, Decimal]:
        """
        Return a dictionary representation (instrument_id: target weight) of this trade proposal
        Returns:
            A dictionary representation

        """
        return {
            v["underlying_instrument"]: v["target_weight"]
            for v in self.trades.all()
            .annotate_base_info()
            .filter(status=Trade.Status.EXECUTED)
            .values("underlying_instrument", "target_weight")
        }

    def __str__(self) -> str:
        return f"{self.portfolio.name}: {self.trade_date} ({self.status})"

    def _build_dto(self) -> TradeBatchDTO:
        """
        Data Transfer Object
        Returns:
            DTO trade object
        """
        return TradeBatchDTO(tuple([trade._build_dto() for trade in self.trades.all()]))

    # Start tools methods
    def _clone(self, **kwargs) -> SelfTradeProposal:
        """
        Method to clone self as a new trade proposal. It will automatically shift the trade date if a proposal already exists
        Args:
            **kwargs: The keyword arguments
        Returns:
            The cloned trade proposal
        """
        trade_date = kwargs.get("clone_date", self.trade_date)

        # Find the next valid trade date
        while TradeProposal.objects.filter(portfolio=self.portfolio, trade_date=trade_date).exists():
            trade_date += timedelta(days=1)

        trade_proposal_clone = TradeProposal.objects.create(
            trade_date=trade_date,
            comment=kwargs.get("clone_comment", self.comment),
            status=TradeProposal.Status.DRAFT,
            rebalancing_model=self.rebalancing_model,
            portfolio=self.portfolio,
            creator=self.creator,
        )
        for trade in self.trades.all():
            trade.id = None
            trade.trade_proposal = trade_proposal_clone
            trade.save()

        return trade_proposal_clone

    def normalize_trades(self, total_target_weight: Decimal = Decimal("1.0")):
        """
        Call the trading service with the existing trades and normalize them in order to obtain a total sum target weight of 100%
        The existing trade will be modified directly with the given normalization factor
        """
        service = TradingService(
            self.trade_date,
            effective_portfolio=self._get_default_effective_portfolio(),
            target_portfolio=self._build_dto().convert_to_portfolio(),
            total_target_weight=total_target_weight,
        )
        leftovers_trades = self.trades.all()
        for underlying_instrument_id, trade_dto in service.trades_batch.trades_map.items():
            with suppress(Trade.DoesNotExist):
                trade = self.trades.get(underlying_instrument_id=underlying_instrument_id)
                trade.weighting = round(trade_dto.delta_weight, 6)
                trade.save()
                leftovers_trades = leftovers_trades.exclude(id=trade.id)
        leftovers_trades.delete()
        t_weight = self.trades.all().annotate_base_info().aggregate(models.Sum("target_weight"))[
            "target_weight__sum"
        ] or Decimal("0.0")
        # we handle quantization error due to the decimal max digits. In that case, we take the biggest trade (highest weight) and we remove the quantization error
        if quantize_error := (t_weight - total_target_weight):
            biggest_trade = self.trades.latest("weighting")
            biggest_trade.weighting -= quantize_error
            biggest_trade.save()

    def _get_default_target_portfolio(self, **kwargs) -> PortfolioDTO:
        if self.rebalancing_model:
            params = {}
            if rebalancer := getattr(self.portfolio, "automatic_rebalancer", None):
                params.update(rebalancer.parameters)
            params.update(kwargs)
            return self.rebalancing_model.get_target_portfolio(
                self.portfolio, self.trade_date, self.last_effective_date, **params
            )
        if self.trades.exists():
            return self._build_dto().convert_to_portfolio()
        # Return the current portfolio by default
        return self._get_default_effective_portfolio()

    def _get_default_effective_portfolio(self):
        return self.portfolio._build_dto(self.last_effective_date)

    def reset_trades(
        self,
        target_portfolio: PortfolioDTO | None = None,
        validate_trade: bool = True,
        total_target_weight: Decimal = Decimal("1.0"),
    ):
        """
        Will delete all existing trades and recreate them from the method `create_or_update_trades`
        """
        # delete all existing trades
        last_effective_date = self.last_effective_date
        # Get effective and target portfolio
        if not target_portfolio:
            target_portfolio = self._get_default_target_portfolio()
        if target_portfolio:
            service = TradingService(
                self.trade_date,
                effective_portfolio=self._get_default_effective_portfolio(),
                target_portfolio=target_portfolio,
                total_target_weight=total_target_weight,
            )
            if validate_trade:
                service.is_valid()
                trades = service.validated_trades
            else:
                trades = service.trades_batch.trades_map.values()
            for trade_dto in trades:
                instrument = Instrument.objects.get(id=trade_dto.underlying_instrument)
                currency_fx_rate = instrument.currency.convert(
                    last_effective_date, self.portfolio.currency, exact_lookup=True
                )
                # we cannot do a bulk-create because Trade is a multi table inheritance
                weighting = round(trade_dto.delta_weight, 6)
                drift_factor = trade_dto.drift_factor
                try:
                    trade = self.trades.get(underlying_instrument=instrument)
                    trade.weighting = weighting
                    trade.currency_fx_rate = currency_fx_rate
                    trade.status = Trade.Status.DRAFT
                    trade.drift_factor = drift_factor
                except Trade.DoesNotExist:
                    trade = Trade(
                        underlying_instrument=instrument,
                        currency=instrument.currency,
                        value_date=last_effective_date,
                        transaction_date=self.trade_date,
                        trade_proposal=self,
                        portfolio=self.portfolio,
                        weighting=weighting,
                        drift_factor=drift_factor,
                        status=Trade.Status.DRAFT,
                        currency_fx_rate=currency_fx_rate,
                    )
                trade.price = trade.get_price()
                # if we cannot automatically find a price, we consider the stock is invalid and we sell it
                if trade.price is None:
                    trade.price = Decimal("0.0")
                    trade.weighting = -trade_dto.effective_weight
                trade.save()

    def replay(self):
        last_trade_proposal = self
        last_trade_proposal_created = False
        while last_trade_proposal and last_trade_proposal.status == TradeProposal.Status.APPROVED:
            if not last_trade_proposal_created:
                logger.info(f"Replaying trade proposal {last_trade_proposal}")
                last_trade_proposal.portfolio.assets.filter(
                    date=last_trade_proposal.trade_date
                ).delete()  # we delete the existing position and we reapply the trade proposal
                if last_trade_proposal.status == TradeProposal.Status.APPROVED:
                    logger.info("Reverting trade proposal ...")
                    last_trade_proposal.revert()
                if last_trade_proposal.status == TradeProposal.Status.DRAFT:
                    if self.rebalancing_model:  # if there is no position (for any reason) or we the trade proposal has a rebalancer model attached (trades are computed based on an aglo), we reapply this trade proposal
                        logger.info(f"Resetting trades from rebalancer model {self.rebalancing_model} ...")
                        with suppress(
                            ValidationError
                        ):  # we silent any validation error while setting proposal, because if this happens, we assume the current trade proposal state if valid and we continue to batch compute
                            self.reset_trades()
                    logger.info("Submitting trade proposal ...")
                    last_trade_proposal.submit()
                if last_trade_proposal.status == TradeProposal.Status.SUBMIT:
                    logger.info("Approving trade proposal ...")
                    last_trade_proposal.approve(replay=False)
                last_trade_proposal.save()
            next_trade_proposal = last_trade_proposal.next_trade_proposal

            next_trade_date = (
                next_trade_proposal.trade_date - timedelta(days=1) if next_trade_proposal else date.today()
            )
            positions, overriding_trade_proposal = self.portfolio.drift_weights(
                last_trade_proposal.trade_date, next_trade_date
            )
            self.portfolio.assets.filter(
                date__gt=last_trade_proposal.trade_date, date__lte=next_trade_date, is_estimated=False
            ).update(
                is_estimated=True
            )  # ensure that we reset non estimated position leftover to estimated between trade proposal during replay
            self.portfolio.bulk_create_positions(
                positions, delete_leftovers=True, compute_metrics=False, evaluate_rebalancer=False
            )
            if overriding_trade_proposal:
                last_trade_proposal_created = True
                last_trade_proposal = overriding_trade_proposal
            else:
                last_trade_proposal_created = False
                last_trade_proposal = next_trade_proposal

    def get_estimated_shares(self, weight: Decimal, underlying_quote: Instrument, quote_price: Decimal) -> Decimal:
        """
        Estimates the number of shares for a trade based on the given weight and underlying quote.

        This method calculates the estimated shares by dividing the trade's total value in the portfolio's currency by the price of the underlying quote in the same currency. It handles currency conversion and suppresses any ValueError that might occur during the price retrieval.

        Args:
            weight (Decimal): The weight of the trade.
            underlying_quote (Instrument): The underlying instrument for the trade.

        Returns:
            Decimal | None: The estimated number of shares or None if the calculation fails.
        """
        # Retrieve the price of the underlying quote on the trade date TODO: this is very slow and probably due to the to_date argument to the dl which slowdown drastically the query

        # Calculate the trade's total value in the portfolio's currency
        trade_total_value_fx_portfolio = self.portfolio_total_asset_value * weight

        # Convert the quote price to the portfolio's currency
        price_fx_portfolio = quote_price * underlying_quote.currency.convert(
            self.trade_date, self.portfolio.currency, exact_lookup=False
        )

        # If the price is valid, calculate and return the estimated shares
        if price_fx_portfolio:
            return trade_total_value_fx_portfolio / price_fx_portfolio

    def get_round_lot_size(self, shares: Decimal, underlying_quote: Instrument) -> Decimal:
        if (round_lot_size := underlying_quote.round_lot_size) != 1 and (
            not underlying_quote.exchange or underlying_quote.exchange.apply_round_lot_size
        ):
            if shares > 0:
                shares = math.ceil(shares / round_lot_size) * round_lot_size
            elif abs(shares) > round_lot_size:
                shares = math.floor(shares / round_lot_size) * round_lot_size
        return shares

    def get_estimated_target_cash(self, currency: Currency) -> AssetPosition:
        """
        Estimates the target cash weight and shares for a trade proposal.

        This method calculates the target cash weight by summing the weights of cash trades and adding any leftover weight from non-cash trades. It then estimates the target shares for this cash component if the portfolio is not only weighting-based.

        Args:
            currency (Currency): The currency for the target currency component

        Returns:
            tuple[Decimal, Decimal]: A tuple containing the target cash weight and the estimated target shares.
        """
        # Retrieve trades with base information
        trades = self.trades.all().annotate_base_info()

        # Calculate the target cash weight from cash trades
        target_cash_weight = trades.filter(
            underlying_instrument__is_cash=True, underlying_instrument__currency=currency
        ).aggregate(s=models.Sum("target_weight"))["s"] or Decimal(0)
        # if the specified currency match the portfolio's currency, we include the weight leftover to this cash compoenent
        if currency == self.portfolio.currency:
            # Calculate the total target weight of all trades
            total_target_weight = trades.aggregate(s=models.Sum("target_weight"))["s"] or Decimal(0)

            # Add any leftover weight as cash
            target_cash_weight += Decimal(1) - total_target_weight

        # Initialize target shares to zero
        total_target_shares = Decimal(0)

        # If the portfolio is not only weighting-based, estimate the target shares for the cash component
        if not self.portfolio.only_weighting:
            # Get or create a cash component for the portfolio's currency
            cash_component = Cash.objects.get_or_create(
                currency=currency, defaults={"is_cash": True, "name": currency.title}
            )[0]

            # Estimate the target shares for the cash component
            with suppress(ValueError):
                total_target_shares = self.get_estimated_shares(target_cash_weight, cash_component, Decimal("1.0"))

        cash_component = Cash.objects.get_or_create(
            currency=self.portfolio.currency, defaults={"name": self.portfolio.currency.title}
        )[0]
        # otherwise, we create a new position
        underlying_quote_price = InstrumentPrice.objects.get_or_create(
            instrument=cash_component,
            date=self.trade_date,
            calculated=False,
            defaults={"net_value": Decimal(1)},
        )[0]
        return AssetPosition(
            underlying_quote=cash_component,
            portfolio_created=None,
            portfolio=self.portfolio,
            date=self.trade_date,
            weighting=target_cash_weight,
            initial_price=underlying_quote_price.net_value,
            initial_shares=total_target_shares,
            asset_valuation_date=self.trade_date,
            underlying_quote_price=underlying_quote_price,
            currency=cash_component.currency,
            is_estimated=False,
        )

    # Start FSM logics

    @transition(
        field=status,
        source=Status.DRAFT,
        target=Status.SUBMIT,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        ),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:tradeproposal",),
                icon=WBIcon.SEND.icon,
                key="submit",
                label="Submit",
                action_label="Submit",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def submit(self, by=None, description=None, **kwargs):
        trades = []
        trades_validation_warnings = []
        for trade in self.trades.all():
            trade_warnings = trade.submit(
                by=by, description=description, portfolio_total_asset_value=self.portfolio_total_asset_value, **kwargs
            )
            if trade_warnings:
                trades_validation_warnings.extend(trade_warnings)
            trades.append(trade)

        Trade.objects.bulk_update(trades, ["status", "shares", "weighting"])

        # If we estimate cash on this trade proposal, we make sure to create the corresponding cash component
        estimated_cash_position = self.get_estimated_target_cash(self.portfolio.currency)
        target_portfolio = self.validated_trading_service.trades_batch.convert_to_portfolio(
            estimated_cash_position._build_dto()
        )
        self.evaluate_active_rules(self.trade_date, target_portfolio, asynchronously=True)
        return trades_validation_warnings

    def can_submit(self):
        errors = dict()
        errors_list = []
        if self.trades.exists() and self.trades.exclude(status=Trade.Status.DRAFT).exists():
            errors_list.append(_("All trades need to be draft before submitting"))
        service = self.validated_trading_service
        try:
            service.is_valid(ignore_error=True)
            # if service.trades_batch.total_abs_delta_weight == 0:
            #     errors_list.append(
            #         "There is no change detected in this trade proposal. Please submit at last one valid trade"
            #     )
            if len(service.validated_trades) == 0:
                errors_list.append(_("There is no valid trade on this proposal"))
            if service.errors:
                errors_list.extend(service.errors)
            if errors_list:
                errors["non_field_errors"] = errors_list
        except ValidationError:
            errors["non_field_errors"] = service.errors
            with suppress(KeyError):
                del self.__dict__["validated_trading_service"]
        return errors

    @property
    def can_be_approved_or_denied(self):
        return not self.has_non_successful_checks and self.portfolio.is_manageable

    @transition(
        field=status,
        source=Status.SUBMIT,
        target=Status.APPROVED,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and instance.can_be_approved_or_denied,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:tradeproposal",),
                icon=WBIcon.APPROVE.icon,
                key="approve",
                label="Approve",
                action_label="Approve",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def approve(self, by=None, description=None, replay: bool = True, **kwargs):
        # We validate trade which will create or update the initial asset positions
        if not self.portfolio.can_be_rebalanced:
            raise ValueError("Non-Rebalanceable portfolio cannot be traded manually.")
        trades = []
        assets = []
        warnings = []
        # We do not want to create the estimated cash position if there is not trades in the trade proposal (shouldn't be possible anyway)
        estimated_cash_position = self.get_estimated_target_cash(self.portfolio.currency)

        for trade in self.trades.all():
            with suppress(ValueError):
                asset = trade.get_asset()
                # we add the corresponding asset only if it is not the cache position (already included in estimated_cash_position)
                if asset.underlying_quote != estimated_cash_position.underlying_quote:
                    assets.append(asset)
            trade.status = Trade.Status.EXECUTED
            trades.append(trade)

        # if there is cash leftover, we create an extra asset position to hold the cash component
        if estimated_cash_position.weighting and len(trades) > 0:
            warnings.append(
                f"We created automatically a cash position of weight {estimated_cash_position.weighting:.2%}"
            )
            estimated_cash_position.pre_save()
            assets.append(estimated_cash_position)

        Trade.objects.bulk_update(trades, ["status"])
        self.portfolio.bulk_create_positions(
            AssetPositionIterator(self.portfolio).add(assets), evaluate_rebalancer=False, force_save=True
        )
        if replay and self.portfolio.is_manageable:
            replay_as_task.delay(self.id, user_id=by.id if by else None)
        return warnings

    def can_approve(self):
        errors = dict()
        if not self.portfolio.can_be_rebalanced:
            errors["non_field_errors"] = [_("The portfolio does not allow manual rebalanced")]
        if self.trades.exclude(status=Trade.Status.SUBMIT).exists():
            errors["non_field_errors"] = [
                _("At least one trade needs to be submitted to be able to approve this proposal")
            ]
        if not self.portfolio.can_be_rebalanced:
            errors["portfolio"] = [
                [_("The portfolio needs to be a model portfolio in order to approve this trade proposal manually")]
            ]
        if self.has_non_successful_checks:
            errors["non_field_errors"] = [_("The pre trades rules did not passed successfully")]
        return errors

    @transition(
        field=status,
        source=Status.SUBMIT,
        target=Status.DENIED,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and instance.can_be_approved_or_denied,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:tradeproposal",),
                icon=WBIcon.DENY.icon,
                key="deny",
                label="Deny",
                action_label="Deny",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def deny(self, by=None, description=None, **kwargs):
        self.trades.all().delete()
        with suppress(KeyError):
            del self.__dict__["validated_trading_service"]

    def can_deny(self):
        errors = dict()
        if self.trades.exclude(status=Trade.Status.SUBMIT).exists():
            errors["non_field_errors"] = [
                _("At least one trade needs to be submitted to be able to deny this proposal")
            ]
        return errors

    @transition(
        field=status,
        source=Status.SUBMIT,
        target=Status.DRAFT,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and instance.has_all_check_completed
        or not instance.checks.exists(),  # we wait for all checks to succeed before proposing the back to draft transition
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:tradeproposal",),
                icon=WBIcon.UNDO.icon,
                key="backtodraft",
                label="Back to Draft",
                action_label="backtodraft",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def backtodraft(self, **kwargs):
        with suppress(KeyError):
            del self.__dict__["validated_trading_service"]
        self.trades.update(status=Trade.Status.DRAFT)
        self.checks.delete()

    def can_backtodraft(self):
        pass

    @transition(
        field=status,
        source=Status.APPROVED,
        target=Status.DRAFT,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        ),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:tradeproposal",),
                icon=WBIcon.REGENERATE.icon,
                key="revert",
                label="Revert",
                action_label="revert",
                description_fields="<p>Unapply trades and move everything back to draft (i.e. The underlying asset positions will change like the trades were never applied)</p>",
            )
        },
    )
    def revert(self, **kwargs):
        with suppress(KeyError):
            del self.__dict__["validated_trading_service"]
        trades = []
        self.portfolio.assets.filter(
            date=self.trade_date, is_estimated=False
        ).delete()  # we delete the existing portfolio as it has been reverted
        for trade in self.trades.all():
            trade.status = Trade.Status.DRAFT
            trades.append(trade)
        Trade.objects.bulk_update(trades, ["status"])

    def can_revert(self):
        errors = dict()
        if not self.portfolio.can_be_rebalanced:
            errors["portfolio"] = [
                _("The portfolio needs to be a model portfolio in order to revert this trade proposal manually")
            ]
        return errors

    # End FSM logics

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbportfolio:tradeproposal"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbportfolio:tradeproposalrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{_portfolio.name}} ({{trade_date}})"


@shared_task(queue="portfolio")
def replay_as_task(trade_proposal_id, user_id: int | None = None):
    trade_proposal = TradeProposal.objects.get(id=trade_proposal_id)
    trade_proposal.replay()
    if user_id:
        user = User.objects.get(id=user_id)
        send_notification(
            code="wbportfolio.portfolio.replay_done",
            title="Trade Proposal Replay Completed",
            body=f'We’ve successfully replayed your trade proposal for "{trade_proposal.portfolio}" from {trade_proposal.trade_date:%Y-%m-%d}. You can now review its updated composition.',
            user=user,
            reverse_name="wbportfolio:portfolio-detail",
            reverse_args=[trade_proposal.portfolio.id],
        )
