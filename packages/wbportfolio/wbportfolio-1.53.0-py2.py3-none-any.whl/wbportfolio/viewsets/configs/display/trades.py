from typing import Optional

from django.shortcuts import get_object_or_404
from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.icons import WBIcon
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbportfolio.models import Trade, TradeProposal

NEGATIVE_RED_FORMATTING = [
    dp.FormattingRule(
        style={
            "color": WBColor.RED_DARK.value,
            "fontWeight": "bold",
        },
        condition=("<", 0),
    )
]

SHARE_FORMATTING = dp.Formatting(
    column="shares",
    formatting_rules=[
        dp.FormattingRule(
            style={
                "color": WBColor.RED_DARK.value,
                # "fontWeight": "bold",
            },
            condition=("<", 0),
        )
    ],
)

TRADE_STATUS_LEGENDS = dp.Legend(
    key="status",
    items=[
        dp.LegendItem(
            icon=WBColor.RED_LIGHT.value,
            label=Trade.Status.FAILED.label,
            value=Trade.Status.FAILED.value,
        ),
        dp.LegendItem(
            icon=WBColor.BLUE_LIGHT.value,
            label=Trade.Status.DRAFT.label,
            value=Trade.Status.DRAFT.value,
        ),
        dp.LegendItem(
            icon=WBColor.YELLOW_LIGHT.value,
            label=Trade.Status.SUBMIT.label,
            value=Trade.Status.SUBMIT.value,
        ),
        dp.LegendItem(
            icon=WBColor.GREEN_LIGHT.value,
            label=Trade.Status.EXECUTED.label,
            value=Trade.Status.EXECUTED.value,
        ),
        dp.LegendItem(
            icon=WBColor.GREEN.value,
            label=Trade.Status.CONFIRMED.label,
            value=Trade.Status.CONFIRMED.value,
        ),
    ],
)

TRADE_STATUS_FORMATTING = dp.Formatting(
    column="status",
    formatting_rules=[
        dp.FormattingRule(
            style={"backgroundColor": WBColor.RED_LIGHT.value},
            condition=("==", Trade.Status.FAILED.value),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
            condition=("==", Trade.Status.DRAFT.value),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
            condition=("==", Trade.Status.SUBMIT.value),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
            condition=("==", Trade.Status.EXECUTED.value),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.GREEN.value},
            condition=("==", Trade.Status.CONFIRMED.value),
        ),
    ],
)


class TradeDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="transaction_subtype", label="Type", width=Unit.PIXEL(100)),
                dp.Field(key="transaction_date", label="Trade Date", width=Unit.PIXEL(150)),
                dp.Field(key="underlying_instrument", label="Instrument", width=Unit.PIXEL(250)),
                dp.Field(
                    label="Value",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="shares", label="Shares", width=Unit.PIXEL(100)),
                        dp.Field(key="price", label="Price", width=Unit.PIXEL(100)),
                        dp.Field(key="total_value", label="Value", width=Unit.PIXEL(125)),
                        dp.Field(key="total_value_usd", label="Value ($)", width=Unit.PIXEL(125), show="open"),
                    ],
                ),
                dp.Field(
                    label="Bank",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="bank", label="Counterparty", width=Unit.PIXEL(150)),
                        dp.Field(key="custodian", label="Custodian", width=Unit.PIXEL(150), show="open"),
                        dp.Field(key="register", label="Register", width=Unit.PIXEL(200), show="open"),
                    ],
                ),
                dp.Field(
                    label="Information",
                    open_by_default=False,
                    key=None,
                    children=list(
                        filter(
                            lambda x: not (x.key == "portfolio" and "portfolio_id" in self.view.kwargs),
                            [
                                dp.Field(key="currency", label="Currency", width=Unit.PIXEL(100)),
                                dp.Field(key="portfolio", label="Portfolio", width=Unit.PIXEL(250), show="open"),
                                dp.Field(
                                    key="marked_for_deletion",
                                    label="Marked for Deletion",
                                    width=Unit.PIXEL(150),
                                    show="open",
                                ),
                                dp.Field(key="pending", label="Pending", width=Unit.PIXEL(150), show="open"),
                            ],
                        )
                    ),
                ),
            ],
            legends=[TRADE_STATUS_LEGENDS],
            formatting=[SHARE_FORMATTING, TRADE_STATUS_FORMATTING],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["transaction_date", "value_date", "."],
                [repeat_field(3, "underlying_instrument")],
                ["shares", "price", "bank"],
                ["external_id", "marked_for_deletion", "register"],
                [repeat_field(3, "comment")],
            ]
        )


class SubscriptionRedemptionDisplayConfig(TradeDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="transaction_subtype", label="Type", width=Unit.PIXEL(100)),
                dp.Field(key="transaction_date", label="Trade Date", width=Unit.PIXEL(150)),
                dp.Field(key="underlying_instrument", label="Product", width=Unit.PIXEL(250)),
                dp.Field(
                    label="Value",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="shares", label="Shares", width=Unit.PIXEL(100)),
                        dp.Field(key="price", label="Price", width=Unit.PIXEL(100)),
                        dp.Field(key="total_value", label="Value", width=Unit.PIXEL(125)),
                        dp.Field(key="total_value_usd", label="Value ($)", width=Unit.PIXEL(125), show="open"),
                    ],
                ),
                dp.Field(
                    label="Customer",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="claimed_shares", label="Claimed Shares", width=Unit.PIXEL(150)),
                        dp.Field(key="claims", label="Claims", width=Unit.PIXEL(150), show="open"),
                        dp.Field(key="comment", label="Comment", width=Unit.PIXEL(200)),
                    ],
                ),
                dp.Field(
                    label="Bank",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="bank", label="Bank", width=Unit.PIXEL(150)),
                        dp.Field(key="custodian", label="Custodian", width=Unit.PIXEL(150), show="open"),
                        dp.Field(key="register", label="Register", width=Unit.PIXEL(200), show="open"),
                    ],
                ),
                dp.Field(
                    label="Information",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="currency", label="Currency", width=Unit.PIXEL(100), show="open"),
                        dp.Field(key="portfolio", label="Portfolio", width=Unit.PIXEL(250), show="open"),
                        dp.Field(key="marked_for_deletion", label="Marked for Deletion", width=Unit.PIXEL(150)),
                        dp.Field(key="pending", label="Pending", width=Unit.PIXEL(150), show="open"),
                        dp.Field(key="marked_as_internal", label="Internal", width=Unit.PIXEL(150), show="open"),
                        dp.Field(key="internal_trade", label="Internal Trade", width=Unit.PIXEL(150), show="open"),
                    ],
                ),
            ],
            legends=[
                dp.Legend(
                    key="completely_claimed",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label="Completely Claimed",
                            value=True,
                        )
                    ],
                ),
                dp.Legend(
                    key="completely_claimed_if_approved",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label="Completely Claimed if approved",
                            value=True,
                        )
                    ],
                ),
                dp.Legend(
                    key="pending",
                    items=[
                        dp.LegendItem(icon=WBIcon.FOLDERS_ADD.icon, label="Pending", value=True),
                    ],
                ),
                dp.Legend(
                    key="marked_for_deletion",
                    items=[
                        dp.LegendItem(icon=WBIcon.DELETE.icon, label="To Be Deleted", value=True),
                    ],
                ),
            ],
            formatting=[
                SHARE_FORMATTING,
                dp.Formatting(
                    column="completely_claimed",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", True),
                        )
                    ],
                ),
                dp.Formatting(
                    column="completely_claimed_if_approved",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", True),
                        )
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["transaction_date", "value_date", "."],
                [repeat_field(3, "underlying_instrument")],
                ["shares", "price", "bank"],
                ["external_id", "marked_for_deletion", "register"],
                [repeat_field(3, "comment")],
                ["marked_as_internal", repeat_field(2, "internal_trade")],
            ]
        )


class TradePortfolioDisplayConfig(TradeDisplayConfig):
    pass


class TradeTradeProposalDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        trade_proposal = get_object_or_404(TradeProposal, pk=self.view.kwargs.get("trade_proposal_id", None))
        fields = [
            dp.Field(
                label="Instrument",
                open_by_default=True,
                key=None,
                children=[
                    dp.Field(key="underlying_instrument", label="Name", width=Unit.PIXEL(250)),
                    dp.Field(key="underlying_instrument_isin", label="ISIN", width=Unit.PIXEL(125)),
                    dp.Field(key="underlying_instrument_ticker", label="Ticker", width=Unit.PIXEL(100)),
                    dp.Field(
                        key="underlying_instrument_refinitiv_identifier_code", label="RIC", width=Unit.PIXEL(100)
                    ),
                    dp.Field(key="underlying_instrument_instrument_type", label="Asset Class", width=Unit.PIXEL(125)),
                ],
            ),
            dp.Field(
                label="Weight",
                open_by_default=False,
                key=None,
                children=[
                    dp.Field(key="effective_weight", label="Effective Weight", show="open", width=Unit.PIXEL(150)),
                    dp.Field(key="target_weight", label="Target Weight", show="open", width=Unit.PIXEL(150)),
                    dp.Field(
                        key="weighting",
                        label="Delta Weight",
                        formatting_rules=[
                            dp.FormattingRule(
                                style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
                                condition=("<", 0),
                            ),
                            dp.FormattingRule(
                                style={"color": WBColor.GREEN_DARK.value, "fontWeight": "bold"},
                                condition=(">", 0),
                            ),
                        ],
                        width=Unit.PIXEL(150),
                    ),
                ],
            ),
        ]
        if not trade_proposal.portfolio.only_weighting:
            fields.append(
                dp.Field(
                    label="Shares",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="effective_shares", label="Effective Shares", show="open", width=Unit.PIXEL(150)),
                        dp.Field(key="target_shares", label="Target Shares", show="open", width=Unit.PIXEL(150)),
                        dp.Field(
                            key="shares",
                            label="Shares",
                            formatting_rules=[
                                dp.FormattingRule(
                                    style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
                                    condition=("<", 0),
                                ),
                                dp.FormattingRule(
                                    style={"color": WBColor.GREEN_DARK.value, "fontWeight": "bold"},
                                    condition=(">", 0),
                                ),
                            ],
                            width=Unit.PIXEL(150),
                        ),
                    ],
                )
            )
            fields.append(
                dp.Field(
                    label="Total Value",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(
                            key="effective_total_value_fx_portfolio",
                            label="Effective Total Value",
                            show="open",
                            width=Unit.PIXEL(150),
                        ),
                        dp.Field(
                            key="target_total_value_fx_portfolio",
                            label="Target Total Value",
                            show="open",
                            width=Unit.PIXEL(150),
                        ),
                        dp.Field(
                            key="total_value_fx_portfolio",
                            label="Total Value",
                            formatting_rules=[
                                dp.FormattingRule(
                                    style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
                                    condition=("<", 0),
                                ),
                                dp.FormattingRule(
                                    style={"color": WBColor.GREEN_DARK.value, "fontWeight": "bold"},
                                    condition=(">", 0),
                                ),
                            ],
                            width=Unit.PIXEL(150),
                        ),
                    ],
                )
            )
        fields.append(
            dp.Field(
                label="Information",
                open_by_default=False,
                key=None,
                children=[
                    dp.Field(
                        key="transaction_subtype",
                        label="Direction",
                        formatting_rules=[
                            dp.FormattingRule(
                                style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
                                condition=("==", Trade.Type.SELL.name),
                            ),
                            dp.FormattingRule(
                                style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
                                condition=("==", Trade.Type.DECREASE.name),
                            ),
                            dp.FormattingRule(
                                style={"color": WBColor.GREEN_DARK.value, "fontWeight": "bold"},
                                condition=("==", Trade.Type.INCREASE.name),
                            ),
                            dp.FormattingRule(
                                style={"color": WBColor.GREEN_DARK.value, "fontWeight": "bold"},
                                condition=("==", Trade.Type.BUY.name),
                            ),
                            dp.FormattingRule(
                                style={"color": WBColor.GREY.value, "fontWeight": "bold"},
                                condition=("==", Trade.Type.NO_CHANGE.name),
                            ),
                        ],
                        width=Unit.PIXEL(125),
                    ),
                    dp.Field(key="comment", label="Comment", width=Unit.PIXEL(250)),
                    dp.Field(key="order", label="Order", show="open", width=Unit.PIXEL(100)),
                ],
            )
        )
        return dp.ListDisplay(
            fields=fields,
            legends=[TRADE_STATUS_LEGENDS],
            formatting=[TRADE_STATUS_FORMATTING],
        )

    def get_instance_display(self) -> Display:
        trade_proposal = get_object_or_404(TradeProposal, pk=self.view.kwargs.get("trade_proposal_id", None))

        fields = [
            ["company", "security", "underlying_instrument"],
            ["effective_weight", "target_weight", "weighting"],
        ]
        if not trade_proposal.portfolio.only_weighting:
            fields.append(["effective_shares", "target_shares", "shares"])
        fields.append([repeat_field(3, "comment")])
        return create_simple_display(fields)
