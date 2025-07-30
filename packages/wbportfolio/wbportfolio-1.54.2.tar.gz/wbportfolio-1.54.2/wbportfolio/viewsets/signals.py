from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.dispatch import receiver
from rest_framework.reverse import reverse
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.signals.instance_buttons import add_instance_button

from wbportfolio.viewsets.products import ProductModelViewSet


@receiver(add_instance_button, sender=ProductModelViewSet)
def add_report_buttons(sender, many, *args, request=None, **kwargs):
    report_buttons = []
    try:
        if instrument_id := kwargs.get("pk", None):
            content_type_product = ContentType.objects.get(app_label="wbportfolio", model="product")
            content_type_instrument = ContentType.objects.get(app_label="wbfdm", model="instrument")
            Report = apps.get_model("wbreport", "Report")
            for report in Report.objects.filter(object_id=instrument_id, is_active=True).filter(
                Q(content_type=content_type_product) | Q(content_type=content_type_instrument)
            ):
                if primary_version := report.primary_version:
                    report_buttons.append(
                        bt.HyperlinkButton(
                            label=f"{report.title} Report",
                            endpoint=reverse(
                                "public_report:report_version", args=[primary_version.lookup], request=request
                            ),
                        ),
                    )
                    if request.user.profile.is_internal or request.user.is_superuser:
                        report_buttons.append(
                            bt.HyperlinkButton(
                                label=f"{report.title} Widget",
                                endpoint=reverse("wbreport:report-detail", args=[report.id], request=request),
                            ),
                        )
    except LookupError:
        pass
    if report_buttons:
        return bt.DropDownButton(label="Reports", buttons=tuple(report_buttons), icon=WBIcon.NOTEBOOK.icon)
