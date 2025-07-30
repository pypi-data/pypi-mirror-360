from contextlib import suppress
from datetime import date, datetime

import pandas as pd
import plotly.graph_objects as go
from django.db.models import Exists, F, OuterRef, Q, Sum
from django.utils.dateparse import parse_date
from django.utils.functional import cached_property
from plotly.subplots import make_subplots
from wbcore import viewsets
from wbcore.contrib.currency.models import Currency, CurrencyFXRates
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.filters import DjangoFilterBackend
from wbcore.pandas import fields as pf
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.serializers import decorator
from wbcore.utils.date import get_date_interval_from_request
from wbcore.utils.figures import (
    get_default_timeserie_figure,
    get_hovertemplate_timeserie,
)
from wbcore.utils.strings import format_number
from wbfdm.contrib.metric.viewsets.mixins import InstrumentMetricMixin
from wbfdm.models import Instrument

from wbportfolio.filters import (
    AssetPositionFilter,
    AssetPositionInstrumentFilter,
    AssetPositionPortfolioFilter,
    AssetPositionUnderlyingInstrumentChartFilter,
    CashPositionPortfolioFilterSet,
    CompositionContributionChartFilter,
    CompositionModelPortfolioPandasFilter,
    ContributionChartFilter,
)
from wbportfolio.import_export.resources.assets import AssetPositionResource
from wbportfolio.metric.backends.portfolio_base import (
    PORTFOLIO_CAPITAL_EMPLOYED,
    PORTFOLIO_EBIT,
    PORTFOLIO_LIABILITIES,
    PORTFOLIO_ROCE,
    PORTFOLIO_TOTAL_ASSETS,
)
from wbportfolio.metric.backends.portfolio_esg import PORTFOLIO_ESG_KEYS
from wbportfolio.models import (
    AssetPosition,
    InstrumentPortfolioThroughModel,
    Portfolio,
    Product,
)
from wbportfolio.serializers.assets import (
    AssetPositionAggregatedPortfolioModelSerializer,
    AssetPositionInstrumentModelSerializer,
    AssetPositionModelSerializer,
    AssetPositionPortfolioModelSerializer,
    CashPositionPortfolioModelSerializer,
)

from .configs import (
    AssetPositionButtonConfig,
    AssetPositionDisplayConfig,
    AssetPositionEndpointConfig,
    AssetPositionInstrumentButtonConfig,
    AssetPositionInstrumentDisplayConfig,
    AssetPositionInstrumentEndpointConfig,
    AssetPositionInstrumentTitleConfig,
    AssetPositionPortfolioButtonConfig,
    AssetPositionPortfolioDisplayConfig,
    AssetPositionPortfolioEndpointConfig,
    AssetPositionPortfolioTitleConfig,
    AssetPositionTitleConfig,
    AssetPositionUnderlyingInstrumentChartEndpointConfig,
    AssetPositionUnderlyingInstrumentChartTitleConfig,
    CashPositionPortfolioDisplayConfig,
    CashPositionPortfolioEndpointConfig,
    CashPositionPortfolioTitleConfig,
    CompositionModelPortfolioPandasDisplayConfig,
    CompositionModelPortfolioPandasEndpointConfig,
    CompositionModelPortfolioPandasTitleConfig,
    ContributorPortfolioChartEndpointConfig,
    ContributorPortfolioChartTitleConfig,
)
from .mixins import UserPortfolioRequestPermissionMixin


class AssetPositionModelViewSet(
    UserPortfolioRequestPermissionMixin,
    InternalUserPermissionMixin,
    viewsets.ReadOnlyModelViewSet,
):
    IDENTIFIER = "wbportfolio:assetposition"
    IMPORT_ALLOWED = False

    queryset = AssetPosition.objects.all()
    serializer_class = AssetPositionModelSerializer
    filterset_class = AssetPositionFilter

    ordering_fields = [
        "total_value_fx_portfolio",
        "total_value_fx_usd",
        "total_value",
        "portfolio__name",
        "portfolio_created__name",
        "underlying_quote",
        "underlying_quote_name",
        "underlying_quote_ticker",
        "underlying_quote_isin",
        "price",
        "currency__key",
        "currency_fx_rate",
        "shares",
        "date",
        "asset_valuation_date",
        "weighting",
        "market_share",
        "liquidity",
    ]
    ordering = ["-weighting"]
    search_fields = ["underlying_quote_ticker", "underlying_quote_name", "underlying_quote_isin"]

    display_config_class = AssetPositionDisplayConfig
    button_config_class = AssetPositionButtonConfig
    endpoint_config_class = AssetPositionEndpointConfig
    title_config_class = AssetPositionTitleConfig

    def get_resource_class(self):
        return AssetPositionResource

    def get_aggregates(self, queryset, paginated_queryset):
        aggregates = super().get_aggregates(queryset, paginated_queryset)
        if queryset.exists():
            total_value_fx_usd = queryset.aggregate(s=Sum(F("total_value_fx_usd")))["s"]
            weighting = queryset.aggregate(s=Sum(F("weighting")))["s"]
            aggregates.update(
                {
                    "weighting": {"Σ": format_number(weighting, decimal=4)},
                    "total_value_fx_usd": {"Σ": format_number(total_value_fx_usd)},
                }
            )
        return aggregates

    def get_queryset(self):
        if self.is_analyst:
            return (
                super()
                .get_queryset()
                .annotate(
                    underlying_quote_isin=F("underlying_quote__isin"),
                    underlying_quote_ticker=F("underlying_quote__ticker"),
                    underlying_quote_name=F("underlying_quote__name"),
                )
                .select_related(
                    "underlying_quote",
                    "currency",
                    "portfolio",
                    "exchange",
                    "portfolio_created",
                )
            )
        return AssetPosition.objects.none()


# Portfolio Viewsets


class AssetPositionPortfolioModelViewSet(InstrumentMetricMixin, AssetPositionModelViewSet):
    METRIC_KEYS = (
        PORTFOLIO_EBIT,
        PORTFOLIO_TOTAL_ASSETS,
        PORTFOLIO_LIABILITIES,
        PORTFOLIO_CAPITAL_EMPLOYED,
        PORTFOLIO_ROCE,
        *PORTFOLIO_ESG_KEYS,
    )
    METRIC_BASKET_LABEL = "portfolio"
    METRIC_INSTRUMENT_LABEL = "underlying_quote"
    METRIC_SHOW_BY_DEFAULT = False
    METRIC_SHOW_FILTERS = True

    @property
    def metric_date(self):
        if date_str := self.request.GET.get("date"):
            return parse_date(date_str)

    @property
    def metric_basket(self):
        return self.portfolio

    filterset_class = AssetPositionPortfolioFilter
    display_config_class = AssetPositionPortfolioDisplayConfig
    button_config_class = AssetPositionPortfolioButtonConfig
    title_config_class = AssetPositionPortfolioTitleConfig
    endpoint_config_class = AssetPositionPortfolioEndpointConfig

    def get_serializer_class(self):
        if self.request.GET.get("aggregate", "false") == "true":
            return AssetPositionAggregatedPortfolioModelSerializer
        return AssetPositionPortfolioModelSerializer

    def get_aggregates(self, queryset, paginated_queryset):
        if not queryset.exists():
            return {}
        weighting = queryset.aggregate(s=Sum(F("weighting")))["s"]
        total_value_fx_portfolio = queryset.aggregate(s=Sum(F("total_value_fx_portfolio")))["s"]
        aggregates = super().get_aggregates(queryset, paginated_queryset)
        aggregates["total_value_fx_portfolio"] = {"Σ": format_number(total_value_fx_portfolio)}
        aggregates["weighting"] = {"Σ": format_number(weighting, decimal=4)}
        return aggregates

    def get_queryset(self):
        if self.has_portfolio_access:
            return (
                super()
                .get_queryset()
                .filter(portfolio=self.portfolio)
                .select_related("underlying_quote", "currency", "exchange", "portfolio_created")
            )
        return AssetPosition.objects.none()


# Underlying Assets viewsets
class AssetPositionInstrumentModelViewSet(AssetPositionModelViewSet):
    filterset_class = AssetPositionInstrumentFilter
    serializer_class = AssetPositionInstrumentModelSerializer
    display_config_class = AssetPositionInstrumentDisplayConfig
    title_config_class = AssetPositionInstrumentTitleConfig
    button_config_class = AssetPositionInstrumentButtonConfig
    endpoint_config_class = AssetPositionInstrumentEndpointConfig

    def get_aggregates(self, queryset, paginated_queryset):
        queryset = queryset.filter(is_invested=True)
        if queryset.exists():
            total_value_fx_usd = queryset.aggregate(s=Sum(F("total_value_fx_usd")))["s"]
            total_shares = queryset.aggregate(s=Sum(F("shares")))["s"]
            total_market_share = queryset.aggregate(s=Sum(F("market_share")))["s"]
            return {
                "shares": {"Σ": format_number(total_shares)},
                "total_value_fx_usd": {"Σ": format_number(total_value_fx_usd)},
                "market_share": {"Σ": format_number(total_market_share)},
            }
        return {}

    def get_queryset(self):
        qs = super().get_queryset().filter(underlying_quote__in=self.instrument.get_descendants(include_self=True))
        if self.request.GET.get("filter_last_positions", "false") == "true":
            if self.instrument.assets.exists():
                qs = qs.filter(date=self.instrument.assets.latest("date").date)
        return qs


class CashPositionPortfolioPandasAPIView(
    UserPortfolioRequestPermissionMixin, InternalUserPermissionMixin, ExportPandasAPIViewSet
):
    queryset = AssetPosition.objects.all()
    display_config_class = CashPositionPortfolioDisplayConfig
    title_config_class = CashPositionPortfolioTitleConfig
    endpoint_config_class = CashPositionPortfolioEndpointConfig

    serializer_class = CashPositionPortfolioModelSerializer
    filterset_class = CashPositionPortfolioFilterSet

    search_fields = ["portfolio_name"]
    ordering_fields = ["portfolio_name", "total_value_fx_usd", "portfolio_weight"]

    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="portfolio", label="ID"),
            pf.CharField(key="portfolio_name", label="Portfolio"),
            pf.FloatField(
                key="total_value_fx_usd",
                label="Total Value",
                precision=2,
                decorators=(decorator(decorator_type="text", position="right", value="$"),),
            ),
            pf.FloatField(key="portfolio_weight", label="Total portfolio value", precision=2, percent=True),
        )
    )

    def get_aggregates(self, request, df):
        if not df.empty:
            sum_total_value_fx_usd = df.total_value_fx_usd.sum()
            return {
                "total_value_fx_usd": {"Σ": format_number(sum_total_value_fx_usd)},
            }
        return {}

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame()
        if queryset.exists():
            df = pd.DataFrame(
                queryset.values(
                    "underlying_instrument__is_cash",
                    "total_value_fx_portfolio",
                    "fx_rate",
                    "portfolio__name",
                    "portfolio",
                )
            )
            df_name = (
                df[["portfolio", "portfolio__name"]]
                .groupby("portfolio")
                .agg("first")
                .rename(columns={"portfolio__name": "portfolio_name"})
            )

            df["total_value_fx_usd"] = df.total_value_fx_portfolio * df.fx_rate
            df_total = (
                df[["portfolio", "total_value_fx_usd"]]
                .groupby("portfolio")
                .sum()
                .rename(columns={"total_value_fx_usd": "total_portfolio_fx_usd"})
            )
            df = df[df["underlying_instrument__is_cash"]]
            df = df[["portfolio", "total_value_fx_usd"]].groupby("portfolio").sum()
            if not df.empty:
                df = df[df["total_value_fx_usd"] != 0]
                df = pd.concat([df, df_total, df_name], axis=1).dropna(how="any")
                df["portfolio_weight"] = df.total_value_fx_usd / df.total_portfolio_fx_usd
                return df.reset_index()
        return df

    def get_queryset(self):
        if self.is_portfolio_manager:
            if date_str := self.request.GET.get("date", None):
                val_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                val_date = date.today()
            active_products = Product.active_objects.filter_active_at_date(val_date)
            return (
                super()
                .get_queryset()
                .annotate(
                    fx_rate=CurrencyFXRates.get_fx_rates_subquery(
                        "date", currency="portfolio__currency", lookup_expr="exact"
                    ),
                    is_product_portfolio=Exists(
                        InstrumentPortfolioThroughModel.objects.filter(
                            portfolio=OuterRef("portfolio"), instrument__in=active_products
                        )
                    ),
                )
                .filter(is_product_portfolio=True)
            )
        return AssetPosition.objects.none()


# ##### CHART VIEWS #####


class ContributorPortfolioChartView(UserPortfolioRequestPermissionMixin, viewsets.ChartViewSet):
    filterset_class = ContributionChartFilter
    filter_backends = (DjangoFilterBackend,)
    IDENTIFIER = "wbportfolio:portfolio-contributor"
    queryset = AssetPosition.objects.all()

    title_config_class = ContributorPortfolioChartTitleConfig
    endpoint_config_class = ContributorPortfolioChartEndpointConfig

    ROW_HEIGHT: int = 20

    @property
    def min_height(self):
        if hasattr(self, "nb_rows"):
            return self.nb_rows * self.ROW_HEIGHT
        return "300px"

    @cached_property
    def hedged_currency(self) -> Currency | None:
        if "hedged_currency" in self.request.GET:
            with suppress(Currency.DoesNotExist):
                return Currency.objects.get(pk=self.request.GET["hedged_currency"])

    @cached_property
    def show_lookthrough(self) -> bool:
        return self.portfolio.is_composition and self.request.GET.get("show_lookthrough", "false").lower() == "true"

    def get_filterset_class(self, request):
        if self.portfolio.is_composition:
            return CompositionContributionChartFilter
        return ContributionChartFilter

    def get_plotly(self, queryset):
        fig = go.Figure()
        data = []
        if self.show_lookthrough:
            d1, d2 = get_date_interval_from_request(self.request)
            for _d in pd.date_range(d1, d2):
                for pos in self.portfolio.get_lookthrough_positions(_d.date()):
                    data.append(
                        [
                            pos.date,
                            pos.initial_price,
                            pos.initial_currency_fx_rate,
                            pos.underlying_instrument_id,
                            pos.weighting,
                        ]
                    )
        else:
            data = queryset.annotate_hedged_currency_fx_rate(self.hedged_currency).values_list(
                "date", "price", "hedged_currency_fx_rate", "underlying_instrument", "weighting"
            )
        df = Portfolio.get_contribution_df(data).rename(columns={"group_key": "underlying_instrument"})
        if not df.empty:
            df = df[["contribution_total", "contribution_forex", "underlying_instrument"]].sort_values(
                by="contribution_total", ascending=True
            )

            df["instrument_id"] = df.underlying_instrument.map(
                dict(Instrument.objects.filter(id__in=df["underlying_instrument"]).values_list("id", "name_repr"))
            )
            df_forex = df[["instrument_id", "contribution_forex"]]
            df_forex = df_forex[df_forex.contribution_forex != 0]

            contribution_equity = df.contribution_total - df.contribution_forex

            text_forex = df_forex.contribution_forex.apply(lambda x: f"{x:,.2%}")
            text_equity = contribution_equity.apply(lambda x: f"{x:,.2%}")
            setattr(self, "nb_rows", df.shape[0])
            fig.add_trace(
                go.Bar(
                    y=df.instrument_id,
                    x=contribution_equity,
                    name="Contribution Equity",
                    orientation="h",
                    marker=dict(
                        color="rgba(247,110,91,0.6)",
                        line=dict(color="rgb(247,110,91,1.0)", width=2),
                    ),
                    text=text_equity.values,
                    textposition="auto",
                )
            )
            fig.add_trace(
                go.Bar(
                    y=df_forex.instrument_id,
                    x=df_forex.contribution_forex,
                    name="Contribution Forex",
                    orientation="h",
                    marker=dict(
                        color="rgba(58, 71, 80, 0.6)",
                        line=dict(color="rgba(58, 71, 80, 1.0)", width=2),
                    ),
                    text=text_forex.values,
                    textposition="outside",
                )
            )
            fig.update_layout(
                barmode="relative",
                xaxis=dict(showgrid=False, showline=False, zeroline=False, tickformat=".2%"),
                yaxis=dict(showgrid=False, showline=False, zeroline=False, tickmode="linear"),
                margin=dict(b=0, r=20, l=20, t=0, pad=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="roboto", size=12, color="black"),
                bargap=0.3,
            )
            # fig = get_horizontal_barplot(df, x_label="contribution_total", y_label="name")
        return fig

    def parse_figure_dict(self, figure_dict: dict[str, any]) -> dict[str, any]:
        figure_dict = super().parse_figure_dict(figure_dict)
        figure_dict["style"]["minHeight"] = self.min_height
        return figure_dict

    def get_queryset(self):
        if self.has_portfolio_access:
            return super().get_queryset().filter(portfolio=self.portfolio)
        return AssetPosition.objects.none()


class AssetPositionUnderlyingInstrumentChartViewSet(UserPortfolioRequestPermissionMixin, viewsets.ChartViewSet):
    IDENTIFIER = "wbportfolio:assetpositionchart"

    queryset = AssetPosition.objects.all()

    title_config_class = AssetPositionUnderlyingInstrumentChartTitleConfig
    endpoint_config_class = AssetPositionUnderlyingInstrumentChartEndpointConfig
    filterset_class = AssetPositionUnderlyingInstrumentChartFilter

    def get_queryset(self):
        return AssetPosition.objects.filter(underlying_quote__in=self.instrument.get_descendants(include_self=True))

    def get_plotly(self, queryset):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig = get_default_timeserie_figure(fig)
        if queryset.exists():
            df_price = (pd.DataFrame(queryset.values("date", "price_fx_usd"))).groupby("date").first()

            df_price = df_price.where(pd.notnull(df_price), 0)
            fig.add_trace(
                go.Scatter(
                    x=df_price.index, y=df_price.price_fx_usd, mode="lines", marker_color="green", name="Price"
                ),
                secondary_y=False,
            )

            df_weight = pd.DataFrame(queryset.values("date", "weighting", "portfolio__name"))
            df_weight = df_weight.where(pd.notnull(df_weight), 0)
            df_weight = df_weight.groupby(["date", "portfolio__name"]).sum().reset_index()
            for portfolio_name, df_tmp in df_weight.groupby("portfolio__name"):
                fig.add_trace(
                    go.Scatter(
                        x=df_tmp.date,
                        y=df_tmp.weighting,
                        hovertemplate=get_hovertemplate_timeserie(is_percent=True),
                        mode="lines",
                        name=f"Allocation: {portfolio_name}",
                    ),
                    secondary_y=True,
                )

            # Set x-axis title
            fig.update_xaxes(title_text="Date")
            # Set y-axes titles
            fig.update_yaxes(
                title_text="<b>Price</b>",
                secondary_y=False,
                titlefont=dict(color="green"),
                tickfont=dict(color="green"),
            )
            fig.update_yaxes(
                title_text="<b>Portfolio Allocation (%)</b>",
                secondary_y=True,
                titlefont=dict(color="blue"),
                tickfont=dict(color="blue"),
            )

        return fig


class CompositionModelPortfolioPandasView(
    UserPortfolioRequestPermissionMixin, InternalUserPermissionMixin, ExportPandasAPIViewSet
):
    IDENTIFIER = "wbportfolio:topdowncomposition"
    filterset_class = CompositionModelPortfolioPandasFilter
    queryset = AssetPosition.objects.all()

    display_config_class = CompositionModelPortfolioPandasDisplayConfig
    title_config_class = CompositionModelPortfolioPandasTitleConfig
    endpoint_config_class = CompositionModelPortfolioPandasEndpointConfig

    @cached_property
    def val_date(self) -> date:
        return parse_date(self.request.GET["date"])

    @cached_property
    def dependant_portfolios(self):
        return Portfolio.objects.filter(
            Q(depends_on__in=[self.portfolio]) | Q(dependent_portfolios__in=[self.portfolio])
        )

    def get_queryset(self):
        if self.has_portfolio_access:
            return super().get_queryset().filter(portfolio=self.portfolio)
        return AssetPosition.objects.none()

    def get_pandas_fields(self, request):
        fields = [
            pf.PKField(key="underlying_instrument", label="ID"),
            pf.CharField(key="underlying_instrument_repr", label="Instrument"),
        ]
        if not self.portfolio.only_weighting:
            fields.append(pf.FloatField(key=f"shares_{self.portfolio.id}", label=str(self.portfolio)))
        fields.append(pf.FloatField(key=f"weighting_{self.portfolio.id}", label=str(self.portfolio), percent=True))

        for portfolio in self.dependant_portfolios:
            if not portfolio.only_weighting:
                fields.append(pf.FloatField(key=f"shares_{portfolio.id}", label=str(portfolio)))
                fields.append(pf.FloatField(key=f"difference_{portfolio.id}", label=str(portfolio)))
            else:
                fields.append(pf.FloatField(key=f"weighting_{portfolio.id}", label=str(portfolio), percent=True))
                fields.append(pf.FloatField(key=f"difference_{portfolio.id}", label=str(portfolio), percent=True))

        return pf.PandasFields(fields=fields)

    search_fields = ["underlying_instrument_repr"]
    ordering_fields = ["underlying_instrument_repr", "model_portfolio"]

    def get_dataframe(self, request, queryset, **kwargs):
        rows = []
        for portfolio in [*self.dependant_portfolios, self.portfolio]:
            rows.extend(
                list(
                    map(
                        lambda x: {
                            "underlying_instrument": x.underlying_instrument.id,
                            "weighting": x.weighting,
                            "shares": x.shares,
                            "portfolio": portfolio.id,
                        },
                        portfolio.get_positions(self.val_date),
                    )
                )
            )
        df = pd.DataFrame(rows, columns=["underlying_instrument", "weighting", "shares", "portfolio"])
        df = df.pivot_table(
            index="underlying_instrument",
            columns=["portfolio"],
            values=["weighting", "shares"],
            aggfunc="sum",
            fill_value=0,
        )
        for portfolio in self.dependant_portfolios:
            with suppress(KeyError):
                if portfolio.only_weighting:
                    df["difference", portfolio.id] = df["weighting"][self.portfolio.id] - df["weighting"][portfolio.id]
                else:
                    df["difference", portfolio.id] = df["shares"][self.portfolio.id] - df["shares"][portfolio.id]

        df.columns = ["_".join([str(item) for item in col]) for col in df.columns.to_flat_index()]
        df = df.reset_index()

        return df

    def manipulate_dataframe(self, df):
        df["underlying_instrument_repr"] = df["underlying_instrument"].map(
            dict(Instrument.objects.filter(id__in=df["underlying_instrument"]).values_list("id", "computed_str"))
        )
        return df
