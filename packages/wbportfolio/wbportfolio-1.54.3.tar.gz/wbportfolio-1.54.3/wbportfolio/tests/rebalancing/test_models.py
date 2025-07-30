from decimal import Decimal

import pytest
from pandas._libs.tslibs.offsets import BDay
from wbfdm.models import InstrumentPrice

from wbportfolio.factories import PortfolioFactory, TradeFactory, TradeProposalFactory
from wbportfolio.models import PortfolioPortfolioThroughModel, Trade, TradeProposal


@pytest.mark.django_db
class TestEquallyWeightedRebalancing:
    @pytest.fixture()
    def model(self, portfolio, weekday):
        from wbportfolio.rebalancing.models import EquallyWeightedRebalancing

        return EquallyWeightedRebalancing(portfolio, (weekday + BDay(1)).date(), weekday)

    def test_is_valid(self, portfolio, weekday, model, asset_position_factory, instrument_price_factory):
        assert not model.is_valid()
        a = asset_position_factory.create(portfolio=model.portfolio, date=model.last_effective_date)
        assert not model.is_valid()
        instrument_price_factory.create(instrument=a.underlying_quote, date=model.trade_date)
        assert model.is_valid()

    def test_get_target_portfolio(self, portfolio, weekday, model, asset_position_factory):
        a1 = asset_position_factory(weighting=0.7, portfolio=portfolio, date=model.last_effective_date)
        a2 = asset_position_factory(weighting=0.3, portfolio=portfolio, date=model.last_effective_date)
        target_portfolio = model.get_target_portfolio()
        target_positions = target_portfolio.positions_map
        assert target_positions[a1.underlying_instrument.id].weighting == Decimal(0.5)
        assert target_positions[a2.underlying_instrument.id].weighting == Decimal(0.5)


@pytest.mark.django_db
class TestModelPortfolioRebalancing:
    @pytest.fixture()
    def model(self, portfolio, weekday):
        from wbportfolio.rebalancing.models import ModelPortfolioRebalancing

        PortfolioPortfolioThroughModel.objects.create(
            portfolio=portfolio,
            dependency_portfolio=PortfolioFactory.create(),
            type=PortfolioPortfolioThroughModel.Type.MODEL,
        )
        return ModelPortfolioRebalancing(portfolio, (weekday + BDay(1)).date(), weekday)

    def test_is_valid(self, portfolio, weekday, model, asset_position_factory, instrument_price_factory):
        assert not model.is_valid()
        asset_position_factory.create(portfolio=model.portfolio, date=model.last_effective_date)
        assert not model.is_valid()

        a = asset_position_factory.create(portfolio=model.model_portfolio, date=model.last_effective_date)
        assert not model.is_valid()
        instrument_price_factory.create(instrument=a.underlying_quote, date=model.trade_date)
        assert model.is_valid()

    def test_get_target_portfolio(self, portfolio, weekday, model, asset_position_factory):
        asset_position_factory(portfolio=portfolio, date=model.last_effective_date)  # noise
        asset_position_factory(portfolio=portfolio, date=model.last_effective_date)  # noise
        a1 = asset_position_factory(weighting=0.8, portfolio=portfolio.model_portfolio, date=model.last_effective_date)
        a2 = asset_position_factory(weighting=0.2, portfolio=portfolio.model_portfolio, date=model.last_effective_date)
        target_portfolio = model.get_target_portfolio()
        target_positions = target_portfolio.positions_map
        assert target_positions[a1.underlying_instrument.id].weighting == Decimal("0.800000")
        assert target_positions[a2.underlying_instrument.id].weighting == Decimal("0.200000")


@pytest.mark.django_db
class TestCompositeRebalancing:
    @pytest.fixture()
    def model(self, portfolio, weekday):
        from wbportfolio.rebalancing.models import CompositeRebalancing

        return CompositeRebalancing(portfolio, (weekday + BDay(1)).date(), weekday)

    def test_is_valid(self, portfolio, weekday, model, asset_position_factory, instrument_price_factory):
        assert not model.is_valid()

        trade_proposal = TradeProposalFactory.create(
            portfolio=model.portfolio, trade_date=model.last_effective_date, status=TradeProposal.Status.APPROVED
        )
        t1 = TradeFactory.create(
            portfolio=model.portfolio,
            transaction_date=model.last_effective_date,
            transaction_subtype=Trade.Type.BUY,
            trade_proposal=trade_proposal,
            weighting=Decimal(0.7),
            status=Trade.Status.EXECUTED,
        )
        TradeFactory.create(
            portfolio=model.portfolio,
            transaction_date=model.last_effective_date,
            transaction_subtype=Trade.Type.BUY,
            trade_proposal=trade_proposal,
            weighting=Decimal(0.3),
            status=Trade.Status.EXECUTED,
        )
        assert not model.is_valid()
        instrument_price_factory.create(instrument=t1.underlying_instrument, date=model.trade_date)
        assert model.is_valid()

    def test_get_target_portfolio(self, portfolio, weekday, model, asset_position_factory):
        trade_proposal = TradeProposalFactory.create(
            portfolio=model.portfolio, trade_date=model.last_effective_date, status=TradeProposal.Status.APPROVED
        )
        asset_position_factory(portfolio=portfolio, date=model.last_effective_date)  # noise
        asset_position_factory(portfolio=portfolio, date=model.last_effective_date)  # noise
        t1 = TradeFactory.create(
            portfolio=model.portfolio,
            transaction_date=model.last_effective_date,
            transaction_subtype=Trade.Type.BUY,
            trade_proposal=trade_proposal,
            weighting=Decimal(0.8),
            status=Trade.Status.EXECUTED,
        )
        t2 = TradeFactory.create(
            portfolio=model.portfolio,
            transaction_date=model.last_effective_date,
            transaction_subtype=Trade.Type.BUY,
            trade_proposal=trade_proposal,
            weighting=Decimal(0.2),
            status=Trade.Status.EXECUTED,
        )
        target_portfolio = model.get_target_portfolio()
        target_positions = target_portfolio.positions_map
        assert target_positions[t1.underlying_instrument.id].weighting == Decimal("0.800000")
        assert target_positions[t2.underlying_instrument.id].weighting == Decimal("0.200000")


@pytest.mark.django_db
class TestMarketCapitalizationRebalancing:
    @pytest.fixture()
    def model(self, portfolio, weekday, instrument_factory, instrument_price_factory):
        from wbportfolio.rebalancing.models import MarketCapitalizationRebalancing

        last_effective_date = (weekday - BDay(1)).date()

        i1 = instrument_factory(inception_date=weekday)
        i2 = instrument_factory(inception_date=weekday)
        instrument_price_factory.create(instrument=i1, date=weekday)
        instrument_price_factory.create(instrument=i2, date=weekday)
        return MarketCapitalizationRebalancing(portfolio, weekday, last_effective_date, instrument_ids=[i1.id, i2.id])

    def test_is_valid(self, portfolio, weekday, model, instrument_factory, instrument_price_factory):
        assert model.is_valid()
        i2 = model.market_cap_df.index[1]
        model.market_cap_df.loc[i2] = None  # some value
        assert not model.is_valid()

    def test_get_target_portfolio(self, portfolio, weekday, model, asset_position_factory):
        i1 = model.market_cap_df.index[0]
        i2 = model.market_cap_df.index[1]
        mkt12 = InstrumentPrice.objects.get(instrument_id=i1, date=weekday).market_capitalization
        mkt21 = InstrumentPrice.objects.get(instrument_id=i2, date=weekday).market_capitalization

        target_portfolio = model.get_target_portfolio()
        target_positions = target_portfolio.positions_map
        assert target_positions[i1].weighting == mkt12 / (mkt12 + mkt21)
        assert target_positions[i2].weighting == mkt21 / (mkt12 + mkt21)
