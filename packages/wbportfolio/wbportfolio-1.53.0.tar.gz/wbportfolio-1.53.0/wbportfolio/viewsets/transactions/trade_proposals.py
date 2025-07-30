from contextlib import suppress
from datetime import date
from decimal import Decimal

from django.contrib.messages import info, warning
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from pandas._libs.tslibs.offsets import BDay
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcompliance.viewsets.risk_management.mixins import RiskCheckViewSetMixin
from wbcore import serializers as wb_serializers
from wbcore import viewsets
from wbcore.metadata.configs.display.instance_display import (
    Display,
    create_simple_display,
)
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.utils.views import CloneMixin

from wbportfolio.models import AssetPosition, TradeProposal
from wbportfolio.models.transactions.trade_proposals import (
    replay_as_task,
)
from wbportfolio.serializers import (
    ReadOnlyTradeProposalModelSerializer,
    TradeProposalModelSerializer,
    TradeProposalRepresentationSerializer,
)

from ..configs import (
    TradeProposalButtonConfig,
    TradeProposalDisplayConfig,
    TradeProposalEndpointConfig,
    TradeProposalPortfolioEndpointConfig,
)
from ..mixins import UserPortfolioRequestPermissionMixin


class TradeProposalRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    IDENTIFIER = "wbportfolio:trade"
    queryset = TradeProposal.objects.all()
    serializer_class = TradeProposalRepresentationSerializer


class TradeProposalModelViewSet(CloneMixin, RiskCheckViewSetMixin, InternalUserPermissionMixin, viewsets.ModelViewSet):
    ordering_fields = ("trade_date",)
    ordering = ("-trade_date",)
    search_fields = ("comment",)
    filterset_fields = {"trade_date": ["exact", "gte", "lte"], "status": ["exact"]}

    queryset = TradeProposal.objects.select_related("rebalancing_model", "portfolio")
    serializer_class = TradeProposalModelSerializer
    display_config_class = TradeProposalDisplayConfig
    button_config_class = TradeProposalButtonConfig
    endpoint_config_class = TradeProposalEndpointConfig

    def get_serializer_class(self):
        if self.new_mode or (
            "pk" in self.kwargs and (obj := self.get_object()) and obj.status == TradeProposal.Status.DRAFT
        ):
            return TradeProposalModelSerializer
        return ReadOnlyTradeProposalModelSerializer

    # 2 methods to parametrize the clone button functionality
    def get_clone_button_serializer_class(self, instance):
        class CloneSerializer(wb_serializers.Serializer):
            clone_date = wb_serializers.DateField(
                default=(instance.trade_date + BDay(1)).date(), label="Trade Date"
            )  # we need to change the field name from the trade proposa fields, otherwise fontend conflicts
            clone_comment = wb_serializers.TextField(label="Comment")

        return CloneSerializer

    def get_clone_button_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["clone_comment"],
                ["clone_date"],
            ]
        )

    def add_messages(self, request, instance=None, **kwargs):
        if instance and instance.status == TradeProposal.Status.SUBMIT:
            if not instance.portfolio.is_manageable:
                info(request, "This trade proposal cannot be approved the portfolio is considered unmanaged.")
            if instance.has_non_successful_checks:
                warning(
                    request,
                    "This trade proposal cannot be approved because there is unsuccessful pre-trade checks. Please rectify accordingly and resubmit a valid trade proposal",
                )

    @classmethod
    def _get_risk_checks_button_title(cls) -> str:
        return "Pre-Trade Checks"

    @action(detail=True, methods=["PATCH"])
    def reset(self, request, pk=None):
        trade_proposal = get_object_or_404(TradeProposal, pk=pk)
        if trade_proposal.status == TradeProposal.Status.DRAFT:
            trade_proposal.trades.all().delete()
            trade_proposal.reset_trades()
            return Response({"send": True})
        return Response({"status": "Trade proposal is not Draft"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"])
    def normalize(self, request, pk=None):
        trade_proposal = get_object_or_404(TradeProposal, pk=pk)
        total_cash_weight = Decimal(request.data.get("total_cash_weight", Decimal("0.0")))
        if trade_proposal.status == TradeProposal.Status.DRAFT:
            trade_proposal.normalize_trades(total_target_weight=Decimal("1.0") - total_cash_weight)
            return Response({"send": True})
        return Response({"status": "Trade proposal is not Draft"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"])
    def replay(self, request, pk=None):
        trade_proposal = get_object_or_404(TradeProposal, pk=pk)
        if trade_proposal.portfolio.is_manageable:
            replay_as_task.delay(trade_proposal.id, user_id=self.request.user.id)
            return Response({"send": True})
        return Response({"status": "Trade proposal is not Draft"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"])
    def deleteall(self, request, pk=None):
        trade_proposal = get_object_or_404(TradeProposal, pk=pk)
        if trade_proposal.status == TradeProposal.Status.DRAFT:
            trade_proposal.trades.all().delete()
            return Response({"send": True})
        return Response({"status": "Trade proposal is not Draft"}, status=status.HTTP_400_BAD_REQUEST)


class TradeProposalPortfolioModelViewSet(UserPortfolioRequestPermissionMixin, TradeProposalModelViewSet):
    endpoint_config_class = TradeProposalPortfolioEndpointConfig

    @cached_property
    def default_trade_date(self) -> date | None:
        with suppress(AssetPosition.DoesNotExist):
            return (self.portfolio.assets.latest("date").date + BDay(1)).date()

    def get_queryset(self):
        return TradeProposal.objects.filter(portfolio=self.kwargs["portfolio_id"])
