from django.contrib import admin

from wbportfolio.models import Trade, TradeProposal


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    search_fields = ["portfolio__name", "underlying_instrument__computed_str", "bank"]
    list_filter = ("portfolio", "pending")
    list_display = (
        "status",
        "transaction_subtype",
        "transaction_date",
        "underlying_instrument",
        "portfolio",
        "shares",
        "price",
        "total_value",
        "pending",
        "marked_for_deletion",
        "exclude_from_history",
        "import_source",
    )

    readonly_fields = [
        "_effective_weight",
        "_target_weight",
        "_effective_shares",
        "_target_shares",
        "total_value",
        "total_value_gross",
        "total_value_fx_portfolio",
        "total_value_gross_fx_portfolio",
        "created",
        "updated",
    ]
    fieldsets = (
        (
            "Transaction Information",
            {
                "fields": (
                    ("transaction_subtype", "status"),
                    ("pending", "marked_for_deletion", "exclude_from_history"),
                    (
                        "portfolio",
                        "underlying_instrument",
                        "import_source",
                    ),
                    ("transaction_date", "book_date", "value_date"),
                    ("price", "currency", "currency_fx_rate"),
                    ("total_value", "total_value_gross"),
                    ("total_value_fx_portfolio", "total_value_gross_fx_portfolio"),
                    ("_effective_weight", "_target_weight", "weighting"),
                    ("_effective_shares", "_target_shares", "shares"),
                    ("register", "custodian", "bank", "external_id", "external_id_alternative"),
                    ("created", "updated"),
                    ("comment",),
                )
            },
        ),
    )
    autocomplete_fields = ["portfolio", "underlying_instrument", "currency", "register", "custodian"]
    ordering = ("-transaction_date",)
    raw_id_fields = ["import_source", "underlying_instrument", "portfolio", "register", "custodian"]


@admin.register(TradeProposal)
class TradeProposalAdmin(admin.ModelAdmin):
    search_fields = ["portfolio__name", "comment"]

    list_display = ("portfolio", "rebalancing_model", "trade_date", "status")
    autocomplete_fields = ["portfolio", "rebalancing_model"]
