from oarepo_ui.resources.config import (
    RecordsUIResourceConfig,
)
from oarepo_ui.resources.resource import RecordsUIResource
from flask_menu import current_menu
from flask_login import login_required
from oarepo_runtime.i18n import lazy_gettext as _
from oarepo_ui.resources.components import AllowedHtmlTagsComponent


class DashboardCommunitiesUIResourceConfig(RecordsUIResourceConfig):
    url_prefix = "/me/communities/"
    blueprint_name = "communities_dashboard"
    template_folder = "templates"
    application_id = "communities_dashboard"
    templates = {
        "search": "DashboardCommunitiesPage",
    }
    components = [AllowedHtmlTagsComponent]
    routes = {
        "search": "/",
    }
    api_service = "communities"

    def search_endpoint_url(self, identity, api_config, overrides={}, **kwargs):
        return "/api/user/communities"


class DashboardCommunitiesUIResource(RecordsUIResource):
    decorators = [
        login_required,
    ]


def create_blueprint(app):
    """Register blueprint for this resource."""
    app_blueprint = DashboardCommunitiesUIResource(
        DashboardCommunitiesUIResourceConfig()
    ).as_blueprint()

    @app_blueprint.before_app_first_request
    def init_menu():
        user_dashboard = current_menu.submenu("user_dashboard")
        user_dashboard.submenu("communities").register(
            "communities_dashboard.search",
            text=_("Communities"),
            order=2,
        )

    return app_blueprint
