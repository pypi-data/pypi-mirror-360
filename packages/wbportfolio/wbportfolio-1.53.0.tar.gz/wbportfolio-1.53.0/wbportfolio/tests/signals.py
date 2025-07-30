from django.dispatch import receiver
from wbcore.contrib.currency.factories import CurrencyFXRatesFactory
from wbcore.contrib.directory.factories import CompanyFactory
from wbcore.test.signals import custom_update_kwargs, get_custom_factory
from wbfdm.factories import InstrumentPriceFactory

from wbportfolio.factories import (
    CustomerTradeFactory,
    ProductFactory,
    ProductPortfolioRoleFactory,
    TradeProposalFactory,
)
from wbportfolio.viewsets import (
    AssetPositionInstrumentModelViewSet,
    AssetPositionUnderlyingInstrumentChartViewSet,
    AUMProductChartView,
    ClaimEntryModelViewSet,
    CustodianDistributionInstrumentChartViewSet,
    CustomerDistributionInstrumentChartViewSet,
    DistributionChartViewSet,
    DistributionTableViewSet,
    NominalProductChartView,
    PortfolioRoleInstrumentModelViewSet,
    ProductCustomerModelViewSet,
    ProductPerformanceFeesModelViewSet,
    SubscriptionRedemptionInstrumentModelViewSet,
    SubscriptionRedemptionModelViewSet,
    TradeInstrumentModelViewSet,
    TradeProposalPortfolioModelViewSet,
    TradeTradeProposalModelViewSet,
)

# =================================================================================================================
#                                              CUSTOM FACTORY
# =================================================================================================================


@receiver(get_custom_factory, sender=SubscriptionRedemptionModelViewSet)
@receiver(get_custom_factory, sender=SubscriptionRedemptionInstrumentModelViewSet)
def receive_factory_subscription_redemption_instrument(sender, *args, **kwargs):
    return CustomerTradeFactory


@receiver(get_custom_factory, sender=PortfolioRoleInstrumentModelViewSet)
def receive_factory_product_portfolio_role(sender, *args, **kwargs):
    return ProductPortfolioRoleFactory


# =================================================================================================================
#                                              UPDATE DATA
# =================================================================================================================


# =================================================================================================================
#                                              UPDATE KWARGS
# =================================================================================================================
@receiver(custom_update_kwargs, sender=TradeTradeProposalModelViewSet)
def receive_kwargs_trade_trade_proposal_product(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        trade_proposal = TradeProposalFactory.create()
        obj.trade_proposal = trade_proposal
        obj.save()
        return {"trade_proposal_id": trade_proposal.id}
    return {}


@receiver(custom_update_kwargs, sender=TradeProposalPortfolioModelViewSet)
def receive_kwargs_trade_trade_proposal_portfolio(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        return {"portfolio_id": obj.portfolio.id}
    return {}


@receiver(custom_update_kwargs, sender=TradeInstrumentModelViewSet)
@receiver(custom_update_kwargs, sender=AssetPositionInstrumentModelViewSet)
@receiver(custom_update_kwargs, sender=SubscriptionRedemptionInstrumentModelViewSet)
@receiver(custom_update_kwargs, sender=AssetPositionUnderlyingInstrumentChartViewSet)
def receive_kwargs_instrument(sender, *args, **kwargs):
    if kwargs.get("underlying_instrument_id"):
        return {"instrument_id": kwargs.get("underlying_instrument_id")}
    return {}


@receiver(custom_update_kwargs, sender=ProductCustomerModelViewSet)
def receive_kwargs_product_customer_instrument(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        InstrumentPriceFactory.create(instrument=obj, calculated=False)
        obj.update_last_valuation_date()
    return {}


@receiver(custom_update_kwargs, sender=PortfolioRoleInstrumentModelViewSet)
def receive_kwargs_portfolio_role_instrument(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        return {"instrument_id": obj.instrument.id}
    return {}


@receiver(custom_update_kwargs, sender=DistributionChartViewSet)
@receiver(custom_update_kwargs, sender=DistributionTableViewSet)
def receive_kwargs_distribution_chart_instrument_id(sender, *args, **kwargs):
    if instrument_id := kwargs.get("underlying_instrument_id"):
        return {"instrument_id": instrument_id}
    return {}


@receiver(custom_update_kwargs, sender=ProductPerformanceFeesModelViewSet)
def receive_kwargs_product_performance_fees(sender, *args, **kwargs):
    CurrencyFXRatesFactory()
    return {}


@receiver(custom_update_kwargs, sender=CustodianDistributionInstrumentChartViewSet)
def receive_kwargs_custodian_distribution_instrument(sender, *args, **kwargs):
    if instrument_id := kwargs.get("underlying_instrument_id"):
        return {"instrument_id": instrument_id}
    return {}


@receiver(custom_update_kwargs, sender=NominalProductChartView)
@receiver(custom_update_kwargs, sender=AUMProductChartView)
def receive_kwargs_aum_product(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        product = ProductFactory()
        obj.instrument = product
        obj.save()
        return {"product_id": product.id}
    return {}


@receiver(custom_update_kwargs, sender=ClaimEntryModelViewSet)
def receive_kwargs_claim_entry(sender, *args, **kwargs):
    if claim := kwargs.get("obj_factory"):
        owner = CompanyFactory.create()
        claim.account.owner = owner
        claim.account.save()
        return {"entry_id": owner.id}
    return {}


@receiver(custom_update_kwargs, sender=CustomerDistributionInstrumentChartViewSet)
def receive_kwargs_customer_distribution(sender, *args, **kwargs):
    if trade := kwargs.get("obj_factory"):
        return {"instrument_id": trade.underlying_instrument.id}
    return {}
