from oarepo_ui.resources.config import (
    RecordsUIResourceConfig,
)
from oarepo_ui.resources.resource import RecordsUIResource
from flask_menu import current_menu
from flask_login import login_required
from oarepo_runtime.i18n import lazy_gettext as _
from oarepo_dashboard.ui.dashboard_components.search import (
    DashboardRequestsSearchComponent,
)
from oarepo_ui.resources.components import AllowedHtmlTagsComponent


class DashboardRequestsUIResourceConfig(RecordsUIResourceConfig):
    url_prefix = "/me/requests/"
    blueprint_name = "requests_dashboard"
    template_folder = "templates"
    application_id = "requests_dashboard"
    templates = {
        "search": "DashboardRequestsPage",
    }

    routes = {
        "search": "/",
    }
    api_service = "requests"

    components = [DashboardRequestsSearchComponent, AllowedHtmlTagsComponent]

    def search_endpoint_url(self, identity, api_config, overrides={}, **kwargs):
        return "/api/requests"

    def ignored_search_filters(self):
        """
        Return a list of search filters to ignore.
        """
        return [
            *super().ignored_search_filters(),
            "is_all",
            "is_open",
            "is_closed",
            "all",
            "mine",
            "assigned",
        ]


class DashboardRequestsUIResource(RecordsUIResource):
    decorators = [
        login_required,
    ]


def create_blueprint(app):
    """Register blueprint for this resource."""
    app_blueprint = DashboardRequestsUIResource(
        DashboardRequestsUIResourceConfig()
    ).as_blueprint()

    @app_blueprint.before_app_first_request
    def init_menu():
        user_dashboard = current_menu.submenu("user_dashboard")
        user_dashboard.submenu("requests").register(
            "requests_dashboard.search",
            text=_("Requests"),
            order=3,
        )

    return app_blueprint
