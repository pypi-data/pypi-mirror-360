from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbportfolio.models import TradeProposal


class TradeProposalPortfolioEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:portfolio-tradeproposal-list", args=[self.view.kwargs["portfolio_id"]], request=self.request
        )

    def get_delete_endpoint(self, **kwargs):
        if trade_proposal_id := self.view.kwargs.get("pk", None):
            trade_proposal = TradeProposal.objects.get(id=trade_proposal_id)
            if trade_proposal.status == TradeProposal.Status.DRAFT:
                return reverse("wbportfolio:tradeproposal-list", args=[], request=self.request)
        return None
