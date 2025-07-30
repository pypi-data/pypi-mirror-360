from flask_menu import current_menu
from flask_login import current_user, login_required
from oarepo_runtime.i18n import lazy_gettext as _
from oarepo_global_search.ui.config import (
    GlobalSearchUIResourceConfig,
    GlobalSearchUIResource,
)
from oarepo_dashboard.ui.dashboard_components.search import (
    DashboardRecordsSearchComponent,
)
from oarepo_ui.resources.components import AllowedHtmlTagsComponent


class DashboardRecordsUIResourceConfig(GlobalSearchUIResourceConfig):
    url_prefix = "/me/records/"
    blueprint_name = "records_dashboard"
    template_folder = "templates"
    application_id = "records_dashboard"
    templates = {
        "search": "DashboardRecordsPage",
    }

    routes = {
        "search": "/",
    }
    api_service = "records"

    components = [
        DashboardRecordsSearchComponent,
        AllowedHtmlTagsComponent,
    ]

    def search_available_sort_options(self, api_config, identity):
        return api_config.search_drafts.sort_options

    def search_active_sort_options(self, api_config, identity):
        return list(api_config.search_drafts.sort_options.keys())

    def search_endpoint_url(self, identity, api_config, overrides={}, **kwargs):
        return "/api/user/search"


class DashboardRecordsUIResource(GlobalSearchUIResource):
    decorators = [
        login_required,
    ]


def create_blueprint(app):
    """Register blueprint for this resource."""
    app_blueprint = DashboardRecordsUIResource(
        DashboardRecordsUIResourceConfig()
    ).as_blueprint()

    @app_blueprint.before_app_first_request
    def init_menu():
        user_dashboard = current_menu.submenu("user_dashboard")
        user_dashboard.submenu("records").register(
            "records_dashboard.search",
            text=_("Records"),
            order=1,
            visible_when=lambda: current_user and current_user.is_authenticated,
        )

        # if you add dashboard to your project, the library adds itself to the main menu
        main_menu_dashboard = current_menu.submenu("main.dashboard")
        main_menu_dashboard.register(
            "records_dashboard.search",
            _("User Dashboard"),
            order=1,
            visible_when=lambda: current_user and current_user.is_authenticated,
        )

    return app_blueprint
