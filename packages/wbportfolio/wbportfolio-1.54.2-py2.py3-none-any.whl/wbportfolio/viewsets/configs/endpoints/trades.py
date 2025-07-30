from contextlib import suppress

from django.shortcuts import get_object_or_404
from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbportfolio.models import TradeProposal


class TradeEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:trade-list", args=[], request=self.request)

    # def get_instance_endpoint(self, **kwargs):
    #     try:
    #         if self.request.user.has_perm("wbportfolio.administrate_trade"):
    #             obj = self.view.get_object()
    #             return reverse("wbportfolio:trade-detail", args=[obj.id], request=self.request)
    #     except AssertionError:
    #         pass
    #     return reverse("wbportfolio:trade-list", request=self.request)

    def get_create_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None


class TradeInstrumentEndpointConfig(TradeEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:instrument-trade-list", args=[self.view.kwargs["instrument_id"]], request=self.request
        )


class TradePortfolioEndpointConfig(TradeEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:portfolio-trade-list", args=[self.view.kwargs["portfolio_id"]], request=self.request
        )


class CustodianDistributionInstrumentEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:instrument-custodiandistribution-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class TradeProposalEndpointConfig(EndpointViewConfig):
    def get_delete_endpoint(self, **kwargs):
        if pk := self.view.kwargs.get("pk", None):
            trade_proposal = get_object_or_404(TradeProposal, pk=pk)
            if trade_proposal.status == TradeProposal.Status.DRAFT:
                return super().get_endpoint()
        return None


class TradeProposalPortfolioEndpointConfig(TradeProposalEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:portfolio-tradeproposal-list", args=[self.view.kwargs["portfolio_id"]], request=self.request
        )


class TradeTradeProposalEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if trade_proposal_id := self.view.kwargs.get("trade_proposal_id", None):
            trade_proposal = TradeProposal.objects.get(id=trade_proposal_id)
            if trade_proposal.status == TradeProposal.Status.DRAFT:
                return reverse(
                    "wbportfolio:tradeproposal-trade-list",
                    args=[self.view.kwargs["trade_proposal_id"]],
                    request=self.request,
                )
        return None

    def get_delete_endpoint(self, **kwargs):
        with suppress(AttributeError, AssertionError):
            trade = self.view.get_object()
            if trade._effective_weight:  # we make sure trade with a valid effective position cannot be deleted
                return None
        return super().get_delete_endpoint(**kwargs)


class SubscriptionRedemptionEndpointConfig(TradeEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:subscriptionredemption-list", args=[], request=self.request)
