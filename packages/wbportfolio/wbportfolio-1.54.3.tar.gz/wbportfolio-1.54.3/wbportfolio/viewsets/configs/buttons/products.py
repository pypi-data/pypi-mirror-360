from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbfdm.viewsets.configs.buttons.instruments import InstrumentButtonViewConfig


class ProductButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()

    def get_custom_instance_buttons(self):
        return {
            bt.DropDownButton(
                label="Commission",
                icon=WBIcon.UNFOLD.icon,
                buttons=(
                    bt.WidgetButton(key="claims", label="Claims"),
                    bt.WidgetButton(key="aum", label="AUM per account"),
                ),
            ),
            *InstrumentButtonViewConfig(self.view, self.request, self.instance).get_custom_instance_buttons(),
            bt.DropDownButton(
                label="Risk Management",
                icon=WBIcon.UNFOLD.icon,
                buttons=[
                    bt.WidgetButton(
                        key="risk_rules",
                        label="Rules",
                        icon=WBIcon.CONFIGURE.icon,
                    ),
                    bt.WidgetButton(
                        key="risk_incidents",
                        label="Incidents",
                        icon=WBIcon.WARNING.icon,
                    ),
                ],
            ),
        }


class ProductCustomerButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.WidgetButton(
                key="historical-chart",
                label="Historical Chart",
                icon=WBIcon.STATS.icon,
            )
        }

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()
