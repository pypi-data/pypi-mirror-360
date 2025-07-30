import datetime as dt

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from wbcore import viewsets
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.filters import DjangoFilterBackend
from wbcore.pandas import fields as pf
from wbfdm.models import (
    ClassificationGroup,
    Instrument,
    InstrumentClassificationThroughModel,
    InstrumentType,
)

from wbportfolio.filters.assets import DistributionFilter
from wbportfolio.models import (
    AssetPosition,
    AssetPositionGroupBy,
    Portfolio,
    PortfolioRole,
)

from ..configs.buttons.assets import (
    DistributionChartButtonConfig,
    DistributionTableButtonConfig,
)
from ..configs.display.assets import DistributionTableDisplayConfig
from ..configs.endpoints.assets import (
    DistributionChartEndpointConfig,
    DistributionTableEndpointConfig,
)
from ..configs.titles.assets import (
    DistributionChartTitleConfig,
    DistributionTableTitleConfig,
)


class AbstractDistributionMixin:
    AUTORESIZE = False
    queryset = AssetPosition.objects.all()
    filterset_class = DistributionFilter
    filter_backends = (DjangoFilterBackend,)

    @cached_property
    def classification_group(self):
        try:
            return ClassificationGroup.objects.get(id=self.request.GET.get("group_by_classification_group"))
        except ClassificationGroup.DoesNotExist:
            return ClassificationGroup.objects.get(is_primary=True)

    @cached_property
    def classification_field_names(self):
        return [f"classification__{field_name}__name" for field_name in self.classification_group.get_fields_names()]

    @cached_property
    def classification_levels_representation(self):
        return self.classification_group.get_levels_representation()

    @cached_property
    def classification_columns_map(self):
        return dict(
            zip(["classification__name", *self.classification_field_names], self.classification_levels_representation)
        )

    def _generate_classification_df(self, queryset):
        df = pd.DataFrame(
            queryset.filter(underlying_instrument__instrument_type=InstrumentType.EQUITY).values(
                "weighting", "underlying_instrument"
            ),
            columns=["weighting", "underlying_instrument"],
        )
        df.underlying_instrument = df.underlying_instrument.map(
            dict(
                Instrument.objects.filter(id__in=df.underlying_instrument)
                .annotate_base_data()
                .values_list("id", "root")
            )
        )
        df = df.groupby("underlying_instrument").sum()
        classifications = InstrumentClassificationThroughModel.objects.filter(
            classification__group=self.classification_group, instrument__in=df.index
        )
        df_classification = pd.DataFrame(
            classifications.values(
                "instrument",
                "classification__name",
                *self.classification_field_names,
            )
        )
        if df_classification.empty:
            return pd.DataFrame()
        return pd.concat([df, df_classification.groupby("instrument").first()], axis=1).replace(
            [np.inf, -np.inf, np.nan], "N/A"
        )

    def get_queryset(self):
        portfolio = get_object_or_404(Portfolio, id=self.kwargs["portfolio_id"])
        if (
            PortfolioRole.is_analyst(self.request.user.profile, portfolio=portfolio)
            or self.request.user.profile.is_internal
        ):
            return super().get_queryset().filter(portfolio=portfolio)
        return AssetPosition.objects.none()

    @staticmethod
    def dataframe_group_by_instrument(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
        return df.groupby("aggregated_title").sum().sort_values(by="weighting", ascending=False)

    def dataframe_groupby_with_class_method(self, qs: QuerySet, class_method: classmethod):
        df = pd.DataFrame()
        if qs.exists():
            df = self.dataframe_group_by_instrument(
                pd.DataFrame(class_method(qs).values("weighting", "aggregated_title"))
            )
        return df


class DistributionChartViewSet(AbstractDistributionMixin, viewsets.ChartViewSet):
    title_config_class = DistributionChartTitleConfig
    endpoint_config_class = DistributionChartEndpointConfig
    button_config_class = DistributionChartButtonConfig

    @staticmethod
    def pie_chart(df: pd.DataFrame) -> go.Figure:
        fig = go.Figure()
        if not df.empty:
            fig.add_pie(
                labels=df.index,
                values=df.weighting.mul(100),
                marker=dict(colors=px.colors.qualitative.Plotly[: df.shape[0]], line=dict(color="#000000", width=2)),
                hovertemplate="<b>%{label}</b><extra></extra>",
            )
        return fig

    def get_plotly(self, queryset):
        fig = go.Figure()
        group_by = self.request.GET.get("group_by", "COUNTRY")
        class_method = AssetPositionGroupBy.get_class_method_group_by(name=group_by)
        queryset_without_cash = queryset.exclude(underlying_instrument__is_cash=True)
        if group_by not in ["INDUSTRY", "CURRENCY"]:
            df = self.dataframe_groupby_with_class_method(qs=queryset_without_cash, class_method=class_method)
            fig = self.pie_chart(df=df)
        elif group_by == "CURRENCY":
            df = self.dataframe_groupby_with_class_method(qs=queryset, class_method=class_method)
            fig = self.pie_chart(df=df)
        else:
            df = self._generate_classification_df(queryset_without_cash)
            if not df.empty:
                df["weighting"] = df.weighting / df.weighting.sum()
                df.weighting = df.weighting.astype("float")
                df = df.reset_index().rename(
                    columns={**self.classification_columns_map, "weighting": "weight", "index": "Equity"}
                )

                levels = [*self.classification_levels_representation[::-1], "Equity"]
                df["Equity"] = df["Equity"].map(
                    dict(Instrument.objects.filter(id__in=df["Equity"]).values_list("id", "name_repr"))
                )
                portfolio = Portfolio.objects.get(id=self.kwargs["portfolio_id"])
                if not PortfolioRole.is_analyst(self.request.user.profile, portfolio=portfolio):
                    del df["Equity"]
                    levels.remove("Equity")
                fig = px.sunburst(
                    df,
                    path=levels,
                    values="weight",
                    hover_data={"weight": ":.2%"},
                )
                fig.update_traces(hovertemplate="<b>%{label}</b><br>Weight = %{customdata:.3p}")
        return fig


class DistributionTableViewSet(AbstractDistributionMixin, ExportPandasAPIViewSet):
    endpoint_config_class = DistributionTableEndpointConfig
    display_config_class = DistributionTableDisplayConfig
    title_config_class = DistributionTableTitleConfig
    button_config_class = DistributionTableButtonConfig

    def get_pandas_fields(self, request):
        if self.request.GET.get("group_by") != "INDUSTRY":
            fields = [
                pf.PKField(key="aggregate_field", label=""),
            ]
        else:
            fields = [
                pf.PKField(key="id", label="IDS"),
                pf.CharField(key="equity", label="Equity"),
            ]
            for level_rep in self.classification_levels_representation:
                fields.append(pf.CharField(key=level_rep, label=level_rep))
        fields.extend([pf.FloatField(key="weighting", label="Weight", precision=2, percent=True)])
        return pf.PandasFields(fields=tuple(fields))

    def get_date_filter(self):
        if date_str := self.request.GET.get("date", None):
            val_date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        elif super().get_queryset().exists():
            val_date = AssetPosition.objects.latest("date").date
        else:
            val_date = dt.date.today()
        return val_date

    def get_queryset(self):
        val_date = self.get_date_filter()
        queryset = super().get_queryset().filter(date=val_date)
        return queryset

    def get_dataframe(self, request, queryset, **kwargs):
        group_by = self.request.GET.get("group_by", "COUNTRY")
        class_method = AssetPositionGroupBy.get_class_method_group_by(name=group_by)
        queryset_without_cash = queryset.exclude(underlying_instrument__is_cash=True)
        if group_by not in ["INDUSTRY", "CURRENCY"]:
            df = self.dataframe_groupby_with_class_method(qs=queryset_without_cash, class_method=class_method)
        elif group_by == "CURRENCY":
            df = self.dataframe_groupby_with_class_method(qs=queryset, class_method=class_method)
        else:  # group_by == "INDUSTRY"
            df = self._generate_classification_df(queryset_without_cash)

            if not df.empty:
                df.weighting /= df.weighting.sum()
                df = df.reset_index().rename(columns={**self.classification_columns_map, "index": "equity"})
                df["equity"] = df["equity"].map(
                    dict(Instrument.objects.filter(id__in=df["equity"]).values_list("id", "name_repr"))
                )
                for level in self.classification_levels_representation:
                    tmp = df.groupby(by=level).weighting.sum().astype(float).mul(100).round(1)
                    df = df.join(tmp, on=level, rsuffix=f"_{level}")
                    df[level] += " (" + df[f"weighting_{level}"].astype(str) + "%)"
                portfolio = Portfolio.objects.get(id=self.request.GET.get("portfolio"))
                if not PortfolioRole.is_analyst(self.request.user.profile, portfolio=portfolio):
                    df[["weighting", "equity"]] = None
                    df.drop_duplicates(inplace=True)
        return df

    def manipulate_dataframe(self, df):
        if not df.empty:
            df.sort_values(by="weighting", ascending=False, inplace=True)
            if df.weighting.sum() != 1:  # normalize
                df.weighting /= df.weighting.sum()
            df = df.reset_index(names="aggregate_field" if self.request.GET.get("group_by") != "INDUSTRY" else "id")
        return df
