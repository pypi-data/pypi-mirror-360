from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display import create_simple_display


class NormalizeSerializer(wb_serializers.Serializer):
    total_cash_weight = wb_serializers.FloatField(default=0, precision=4, percent=True)


class TradeProposalButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.DropDownButton(
                label="Tools",
                buttons=(
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbportfolio:tradeproposal",),
                        key="replay",
                        icon=WBIcon.SYNCHRONIZE.icon,
                        label="Replay Trades",
                        description_fields="""
                        <p>Replay Trades. It will recompute all assets positions until next trade proposal day (or today otherwise) </p>
                        """,
                        action_label="Replay Trade",
                        title="Replay Trade",
                    ),
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbportfolio:tradeproposal",),
                        key="reset",
                        icon=WBIcon.REGENERATE.icon,
                        label="Reset Trades",
                        description_fields="""
                            <p>Delete and recreate initial trades to from its associated model portfolio</p>
                            """,
                        action_label="Reset Trades",
                        title="Reset Trades",
                    ),
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbportfolio:tradeproposal",),
                        key="normalize",
                        icon=WBIcon.EDIT.icon,
                        label="Normalize Trades",
                        description_fields="""
                            <p>Make sure all trades normalize to a total target weight of (100 - {{total_cash_weight}})%</p>
                            """,
                        action_label="Normalize Trades",
                        title="Normalize Trades",
                        serializer=NormalizeSerializer,
                        instance_display=create_simple_display([["total_cash_weight"]]),
                    ),
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbportfolio:tradeproposal",),
                        key="deleteall",
                        icon=WBIcon.DELETE.icon,
                        label="Delete All Trades",
                        description_fields="""
                    <p>Delete all trades from this trade proposal?</p>
                    """,
                        action_label="Delete All Trades",
                        title="Delete All Trades",
                    ),
                ),
            ),
        }

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()
