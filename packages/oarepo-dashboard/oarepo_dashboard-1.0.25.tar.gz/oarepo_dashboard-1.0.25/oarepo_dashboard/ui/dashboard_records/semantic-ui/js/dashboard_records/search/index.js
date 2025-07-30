import React from "react";
import { Grid, Button } from "semantic-ui-react";
import { parametrize } from "react-overridable";
import { i18next } from "@translations/oarepo_dashboard";
import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  SearchappSearchbarElement,
  DynamicResultsListItem,
  SearchAppLayoutWithSearchbarHOC,
  SearchAppResultViewWithSearchbar,
} from "@js/oarepo_ui";
import PropTypes from "prop-types";

const [
  {
    overridableIdPrefix,
    dashboardRecordsCreateUrl,
    permissions: { can_create },
  },
] = parseSearchAppConfigs();

const SearchAppResultViewWithSearchbarWAppName = parametrize(
  SearchAppResultViewWithSearchbar,
  {
    appName: overridableIdPrefix,
  }
);

const CreateNewDraftButton = ({ dashboardRecordsCreateUrl }) => {
  !dashboardRecordsCreateUrl &&
    console.error(
      "DASHBOARD_RECORD_CREATE_URL was not provided in invenio.cfg"
    );
  return (
    can_create &&
    dashboardRecordsCreateUrl && (
      <Grid.Column textAlign="right">
        <Button
          as="a"
          href={dashboardRecordsCreateUrl}
          type="button"
          labelPosition="left"
          icon="plus"
          content={i18next.t("Create new draft")}
          primary
        />
      </Grid.Column>
    )
  );
};

CreateNewDraftButton.propTypes = {
  dashboardRecordsCreateUrl: PropTypes.string,
};

export const DashboardUploadsSearchLayout = SearchAppLayoutWithSearchbarHOC({
  placeholder: i18next.t("Search in my uploads..."),
  extraContent: parametrize(CreateNewDraftButton, {
    dashboardRecordsCreateUrl: dashboardRecordsCreateUrl,
  }),
  appName: overridableIdPrefix,
});
export const componentOverrides = {
  [`${overridableIdPrefix}.ResultsList.item`]: DynamicResultsListItem,
  [`${overridableIdPrefix}.SearchBar.element`]: SearchappSearchbarElement,
  // [`${overridableIdPrefix}.SearchApp.facets`]: ContribSearchAppFacetsWithConfig,
  [`${overridableIdPrefix}.SearchApp.results`]:
    SearchAppResultViewWithSearchbarWAppName,
  [`${overridableIdPrefix}.SearchApp.layout`]: DashboardUploadsSearchLayout,
};

createSearchAppsInit({ componentOverrides });
