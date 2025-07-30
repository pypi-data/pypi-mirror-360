from datetime import timedelta
from decimal import Decimal

from rest_framework import serializers
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.metadata.configs.display.list_display import BaseTreeGroupLevelOption
from wbfdm.models import Instrument
from wbfdm.serializers import InvestableInstrumentRepresentationSerializer
from wbfdm.serializers.instruments.instruments import (
    CompanyRepresentationSerializer,
    InvestableUniverseRepresentationSerializer,
    SecurityRepresentationSerializer,
)

from wbportfolio.models import PortfolioRole, Trade, TradeProposal
from wbportfolio.models.transactions.claim import Claim
from wbportfolio.serializers.custodians import CustodianRepresentationSerializer
from wbportfolio.serializers.registers import RegisterRepresentationSerializer

from .. import PortfolioRepresentationSerializer


class CopyClaimRepresentationSerializer(wb_serializers.RepresentationSerializer):
    claimant = wb_serializers.StringRelatedField()
    product = wb_serializers.StringRelatedField()
    account = wb_serializers.StringRelatedField()
    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:claim-detail")

    class Meta:
        model = Claim
        fields = (
            "id",
            "shares",
            "claimant",
            "bank",
            "product",
            "account",
            "_detail",
        )


class TradeProposalRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:tradeproposal-detail")

    class Meta:
        model = TradeProposal
        fields = ("id", "trade_date", "status", "_detail")


class TradeRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:trade-detail")
    diff_shares = wb_serializers.DecimalField(max_digits=15, decimal_places=4, read_only=True)
    total_value = wb_serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True, required=False)

    class Meta:
        model = Trade
        fields = (
            "id",
            "transaction_date",
            "total_value",
            "_detail",
            "claimed_shares",
            "diff_shares",
            "bank",
            "shares",
        )


class TradeClaimRepresentationSerializer(TradeRepresentationSerializer):
    def get_filter_params(self, request):
        claim_id = request.parser_context["view"].kwargs.get("pk", None)
        arg = {"marked_for_deletion": False}
        if claim_id:
            claim = Claim.objects.get(id=claim_id)
            arg.update(
                {
                    "underlying_instrument": claim.product.id,
                    "transaction_date__gte": claim.date - timedelta(days=Trade.TRADE_WINDOW_INTERVAL),
                    "transaction_date__lte": claim.date + timedelta(days=Trade.TRADE_WINDOW_INTERVAL),
                }
            )
            if claim.shares:
                if claim.shares > 0:
                    arg["shares__gte"] = claim.shares
                else:
                    arg["shares__lte"] = claim.shares
            return arg
        return {}


class TradeModelSerializer(wb_serializers.ModelSerializer):
    _portfolio = PortfolioRepresentationSerializer(source="portfolio")
    _underlying_instrument = InvestableUniverseRepresentationSerializer(source="underlying_instrument")
    _currency = CurrencyRepresentationSerializer(source="currency")

    marked_for_deletion = wb_serializers.BooleanField(required=False, read_only=True)
    marked_as_internal = wb_serializers.BooleanField()

    approved_claimed_shares = wb_serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, read_only=True, default=Decimal(0.0)
    )
    pending_claimed_shares = wb_serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, read_only=True, default=Decimal(0.0)
    )
    completely_claimed = wb_serializers.BooleanField(required=False, read_only=True, default=Decimal(0.0))
    completely_claimed_if_approved = wb_serializers.BooleanField(required=False, read_only=True, default=Decimal(0.0))

    total_value = wb_serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True, required=False)
    total_value_fx_portfolio = wb_serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True, required=False
    )
    total_value_gross = wb_serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True, required=False)
    total_value_gross_fx_portfolio = wb_serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True, required=False
    )
    external_id = wb_serializers.CharField(required=False, read_only=True)
    value_date = wb_serializers.DateField(required=False, read_only=True)
    total_value_usd = wb_serializers.FloatField(default=0, read_only=True, label="Total Value ($)")
    total_value_gross_usd = wb_serializers.FloatField(default=0, read_only=True, label="Total Value Gross ($)")

    # We commented it because people needs to filter with lookup equals onto these fields
    # shares = wb_serializers.DecimalField(max_digits=16, decimal_places=2)
    # price = wb_serializers.DecimalField(max_digits=16, decimal_places=2)

    _register = RegisterRepresentationSerializer(source="register")
    claims = wb_serializers.PrimaryKeyRelatedField(queryset=Claim.objects.all(), label="Claims", many=True)
    _claims = CopyClaimRepresentationSerializer(source="claims", many=True)
    _custodian = CustodianRepresentationSerializer(source="custodian")
    _internal_trade = TradeRepresentationSerializer(
        source="internal_trade",
        filter_params={"only_internal_trade": True},
        optional_get_parameters={"underlying_instrument": "underlying_instrument", "transaction_date": "pivot_date"},
        depends_on=[{"field": "marked_as_internal", "options": {"activates_on": [True]}}],
    )

    @wb_serializers.register_only_instance_resource()
    def import_source_file_url(self, instance, request, user, *args, **kwargs):
        if PortfolioRole.is_portfolio_manager(user.profile, instance.underlying_instrument):
            if instance.import_source:
                return {"import_source": instance.import_source.file.url}
        return {}

    @wb_serializers.register_resource()
    def claims_list(self, instance, request, user):
        if instance.is_claimable:
            return {
                "claims": reverse(
                    "wbportfolio:trade-claim-list",
                    args=[instance.id],
                    request=request,
                )
            }
        return {}

    class Meta:
        model = Trade
        decorators = {
            "total_value": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
            "total_value_gross": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
            "total_value_usd": wb_serializers.decorator(decorator_type="text", position="left", value="{{$}}"),
            "total_value_gross_usd": wb_serializers.decorator(decorator_type="text", position="left", value="{{$}}"),
            "total_value_fx_portfolio": wb_serializers.decorator(
                position="left", value="{{_portfolio.currency_symbol}}"
            ),
            "total_value_gross_fx_portfolio": wb_serializers.decorator(
                position="left", value="{{_portfolio.currency_symbol}}"
            ),
            # "total_value_fx_portfolio": wb_serializers.decorator(decorator_type="text", position="left", value="{{_portfolio.currency_symbol}}}"),
            # "total_value_gross_fx_portfolio": wb_serializers.decorator(decorator_type="text", position="left", value="{{_portfolio.currency_symbol}}"),
        }
        read_only_fields = (
            "id",
            "shares",
            "price",
            "transaction_subtype",
            "approved_claimed_shares",
            "pending_claimed_shares",
            "claimed_shares",
            "completely_claimed",
            "completely_claimed_if_approved",
            "register",
            "_register",
            "pending",
            "bank",
            "marked_for_deletion",
            "_claims",
            "claims",
            "portfolio",
            "_portfolio",
            "underlying_instrument",
            "_underlying_instrument",
            "transaction_date",
            "book_date",
            "value_date",
            "currency",
            "_currency",
            "currency_fx_rate",
            "total_value",
            "total_value_fx_portfolio",
            "total_value_gross",
            "total_value_gross_fx_portfolio",
            "external_id",
            "total_value_usd",
            "total_value_gross_usd",
            "_additional_resources",
        )

        fields = (
            "id",
            "shares",
            "price",
            "transaction_subtype",
            "approved_claimed_shares",
            "pending_claimed_shares",
            "claimed_shares",
            "completely_claimed",
            "completely_claimed_if_approved",
            "register",
            "_register",
            "pending",
            "bank",
            "marked_for_deletion",
            "_claims",
            "claims",
            "portfolio",
            "_portfolio",
            "underlying_instrument",
            "_underlying_instrument",
            "transaction_date",
            "book_date",
            "value_date",
            "currency",
            "_currency",
            "currency_fx_rate",
            "total_value",
            "total_value_fx_portfolio",
            "total_value_gross",
            "total_value_gross_fx_portfolio",
            "external_id",
            "comment",
            "total_value_usd",
            "total_value_gross_usd",
            "_custodian",
            "custodian",
            "marked_as_internal",
            "internal_trade",
            "_internal_trade",
            "_additional_resources",
        )


class GetSecurityDefault:
    requires_context = True

    def __call__(self, serializer_instance):
        try:
            instance = serializer_instance.view.get_object()
            return instance.underlying_instrument.parent or instance.underlying_instrument
        except Exception:
            return None


class GetCompanyDefault:
    requires_context = True

    def __call__(self, serializer_instance):
        try:
            instance = serializer_instance.view.get_object()
            security = instance.underlying_instrument.parent or instance.underlying_instrument
            return security.parent or security
        except Exception:
            return None


class TradeTradeProposalModelSerializer(TradeModelSerializer):
    underlying_instrument_isin = wb_serializers.CharField(read_only=True)
    underlying_instrument_ticker = wb_serializers.CharField(read_only=True)
    underlying_instrument_refinitiv_identifier_code = wb_serializers.CharField(read_only=True)
    underlying_instrument_instrument_type = wb_serializers.CharField(read_only=True)

    company = wb_serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.filter(level=0),
        required=False,
        read_only=lambda view: not view.new_mode,
        default=GetCompanyDefault(),
    )
    _company = CompanyRepresentationSerializer(source="company", required=False)

    security = wb_serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.filter(is_security=True),
        required=False,
        read_only=lambda view: not view.new_mode,
        default=GetSecurityDefault(),
    )
    _security = SecurityRepresentationSerializer(
        source="security",
        optional_get_parameters={"company": "parent"},
        depends_on=[{"field": "company", "options": {}}],
        required=False,
    )
    underlying_instrument = wb_serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.all(), label="Quote", read_only=lambda view: not view.new_mode
    )
    _underlying_instrument = InvestableInstrumentRepresentationSerializer(
        source="underlying_instrument",
        optional_get_parameters={"security": "parent"},
        depends_on=[{"field": "security", "options": {}}],
        tree_config=BaseTreeGroupLevelOption(clear_filter=True, filter_key="parent"),
    )

    status = wb_serializers.ChoiceField(default=Trade.Status.DRAFT, choices=Trade.Status.choices)
    weighting = wb_serializers.DecimalField(max_digits=7, decimal_places=6)
    target_weight = wb_serializers.DecimalField(max_digits=7, decimal_places=6, required=False, default=0)
    effective_weight = wb_serializers.DecimalField(read_only=True, max_digits=7, decimal_places=6, default=0)
    effective_shares = wb_serializers.DecimalField(read_only=True, max_digits=16, decimal_places=6, default=0)
    target_shares = wb_serializers.DecimalField(read_only=True, max_digits=16, decimal_places=6, default=0)

    total_value_fx_portfolio = wb_serializers.DecimalField(read_only=True, max_digits=16, decimal_places=2, default=0)
    effective_total_value_fx_portfolio = wb_serializers.DecimalField(
        read_only=True, max_digits=16, decimal_places=2, default=0
    )
    target_total_value_fx_portfolio = wb_serializers.DecimalField(
        read_only=True, max_digits=16, decimal_places=2, default=0
    )

    portfolio_currency = wb_serializers.CharField(read_only=True)

    def validate(self, data):
        data.pop("company", None)
        data.pop("security", None)
        if self.instance and "underlying_instrument" in data:
            raise serializers.ValidationError(
                {
                    "underlying_instrument": "You cannot modify the underlying instrument other than creating a new entry"
                }
            )
        effective_weight = self.instance._effective_weight if self.instance else Decimal(0.0)
        weighting = data.get("weighting", self.instance.weighting if self.instance else Decimal(0.0))
        if (target_weight := data.pop("target_weight", None)) is not None:
            weighting = target_weight - effective_weight
        if (target_weight := data.pop("target_weight", None)) is not None:
            weighting = target_weight - effective_weight
        if weighting >= 0:
            data["transaction_subtype"] = "BUY"
        else:
            data["transaction_subtype"] = "SELL"
        data["weighting"] = weighting
        return super().validate(data)

    class Meta:
        model = Trade
        percent_fields = ["effective_weight", "target_weight", "weighting"]
        decorators = {
            "total_value_fx_portfolio": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{portfolio_currency}}"
            ),
            "effective_total_value_fx_portfolio": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{portfolio_currency}}"
            ),
            "target_total_value_fx_portfolio": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{portfolio_currency}}"
            ),
        }
        read_only_fields = (
            "transaction_subtype",
            "shares",
            "effective_shares",
            "target_shares",
            "total_value_fx_portfolio",
            "effective_total_value_fx_portfolio",
            "target_total_value_fx_portfolio",
        )
        fields = (
            "id",
            "shares",
            "underlying_instrument_isin",
            "underlying_instrument_ticker",
            "underlying_instrument_refinitiv_identifier_code",
            "underlying_instrument_instrument_type",
            "company",
            "_company",
            "security",
            "_security",
            "underlying_instrument",
            "_underlying_instrument",
            "transaction_subtype",
            "status",
            "comment",
            "effective_weight",
            "target_weight",
            "weighting",
            "trade_proposal",
            "order",
            "effective_shares",
            "target_shares",
            "total_value_fx_portfolio",
            "effective_total_value_fx_portfolio",
            "target_total_value_fx_portfolio",
            "portfolio_currency",
        )


class ReadOnlyTradeTradeProposalModelSerializer(TradeTradeProposalModelSerializer):
    class Meta(TradeTradeProposalModelSerializer.Meta):
        read_only_fields = TradeTradeProposalModelSerializer.Meta.fields
