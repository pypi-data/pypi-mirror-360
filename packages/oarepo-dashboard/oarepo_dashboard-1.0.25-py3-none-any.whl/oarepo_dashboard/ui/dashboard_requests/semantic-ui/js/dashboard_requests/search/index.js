import React from "react";
import { Grid } from "semantic-ui-react";
import { parametrize } from "react-overridable";
import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  SearchappSearchbarElement,
  SearchAppLayoutWithSearchbarHOC,
  SearchAppResultViewWithSearchbar,
  DynamicResultsListItem,
} from "@js/oarepo_ui/search";
import { withState } from "react-searchkit";
import { RequestsEmptyResultsWithState } from "@js/invenio_requests/search";
import { defaultContribComponents } from "@js/invenio_requests/contrib";
import { PropTypes } from "prop-types";
import { FacetsButtonGroupNameToggler } from "@js/dashboard_components";
import { i18next } from "@translations/oarepo_dashboard";
import { ComputerTabletRequestsListItem } from "@js/oarepo_requests_common/search/ComputerTabletRequestsListItem";
import { MobileRequestsListItem } from "@js/oarepo_requests_common/search/MobileRequestsListItem";
import { requestTypeSpecificComponents } from "@js/oarepo_requests_common/search/RequestTypeSpecificComponents";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

export function RequestsResultsItemTemplateDashboard({ result }) {
  const ComputerTabletRequestsItemWithState = withState(
    ComputerTabletRequestsListItem
  );
  const MobileRequestsItemWithState = withState(MobileRequestsListItem);
  const detailPageUrl = result?.links?.self_html;
  return (
    <>
      <ComputerTabletRequestsItemWithState
        result={result}
        detailsURL={detailPageUrl}
      />
      <MobileRequestsItemWithState result={result} detailsURL={detailPageUrl} />
    </>
  );
}

RequestsResultsItemTemplateDashboard.propTypes = {
  result: PropTypes.object.isRequired,
};
export const FacetButtons = () => (
  <React.Fragment>
    <Grid.Column only="computer" textAlign="right">
      <FacetsButtonGroupNameToggler
        basic
        toggledFilters={[
          { text: i18next.t("All"), filterName: "is_all" },
          { text: i18next.t("Open"), filterName: "is_open" },
          { text: i18next.t("Closed"), filterName: "is_closed" },
        ]}
      />
      <span className="rel-ml-2"></span>
      <FacetsButtonGroupNameToggler
        basic
        toggledFilters={[
          { text: i18next.t("All"), filterName: "all" },
          { text: i18next.t("My"), filterName: "mine" },
          { text: i18next.t("Others"), filterName: "assigned" },
        ]}
      />
    </Grid.Column>
    <Grid.Column only="mobile tablet" textAlign="left">
      <FacetsButtonGroupNameToggler
        basic
        toggledFilters={[
          { text: i18next.t("All"), filterName: "is_all" },
          { text: i18next.t("Open"), filterName: "is_open" },
          { text: i18next.t("Closed"), filterName: "is_closed" },
        ]}
      />
    </Grid.Column>
    <Grid.Column only="mobile tablet" textAlign="right">
      <FacetsButtonGroupNameToggler
        basic
        toggledFilters={[
          { text: i18next.t("All"), filterName: "all" },
          { text: i18next.t("My"), filterName: "mine" },
          { text: i18next.t("Others"), filterName: "assigned" },
        ]}
      />
    </Grid.Column>
  </React.Fragment>
);

const SearchAppResultViewWithSearchbarWAppName = parametrize(
  SearchAppResultViewWithSearchbar,
  {
    appName: overridableIdPrefix,
  }
);

export const DashboardUploadsSearchLayout = SearchAppLayoutWithSearchbarHOC({
  placeholder: i18next.t("Search in my requests..."),
  extraContent: FacetButtons,
  appName: overridableIdPrefix,
});

const DynamicRequestListItem = parametrize(DynamicResultsListItem, {
  FallbackComponent: RequestsResultsItemTemplateDashboard,
  selector: "type",
});
export const componentOverrides = {
  [`${overridableIdPrefix}.EmptyResults.element`]:
    RequestsEmptyResultsWithState,
  [`${overridableIdPrefix}.ResultsList.item`]: DynamicRequestListItem,
  [`${overridableIdPrefix}.ClearFiltersButton.container`]: () => null,
  [`${overridableIdPrefix}.SearchApp.results`]:
    SearchAppResultViewWithSearchbarWAppName,
  [`${overridableIdPrefix}.SearchBar.element`]: SearchappSearchbarElement,
  [`${overridableIdPrefix}.SearchApp.layout`]: DashboardUploadsSearchLayout,

  // from invenio requests in case we have some overlapping request types
  ...defaultContribComponents,
  // our request type specific components (icons, labels, etc.)
  ...requestTypeSpecificComponents,
};

createSearchAppsInit({ componentOverrides });
