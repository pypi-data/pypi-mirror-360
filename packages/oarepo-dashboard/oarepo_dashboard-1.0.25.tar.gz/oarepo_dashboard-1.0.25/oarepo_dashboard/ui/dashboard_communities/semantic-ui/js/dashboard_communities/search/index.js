import React from "react";
import { parametrize } from "react-overridable";
import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  SearchappSearchbarElement,
  SearchAppLayoutWithSearchbarHOC,
  SearchAppResultViewWithSearchbar,
} from "@js/oarepo_ui";
import { CommunitiesEmptySearchResults } from "@js/invenio_communities/community";
import PropTypes from "prop-types";
import { ComputerTabledCommunitiesListItem } from "@js/oarepo_communities/search/ComputerTabletCommunitiesListItem";
import { MobileCommunitiesListItem } from "@js/oarepo_communities/search/MobileCommunitiesListItem";
import { i18next } from "@translations/oarepo_dashboard";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

export const UserDashboardCommunitiesListItem = ({
  result,
  communityTypeLabelTransparent,
}) => {
  const isRestricted = result?.access?.visibility === "restricted";
  return (
    <React.Fragment>
      <ComputerTabledCommunitiesListItem
        result={result}
        communityTypeLabelTransparent={communityTypeLabelTransparent}
        isRestricted={isRestricted}
      />
      <MobileCommunitiesListItem
        result={result}
        communityTypeLabelTransparent={communityTypeLabelTransparent}
        isRestricted={isRestricted}
      />
    </React.Fragment>
  );
};

UserDashboardCommunitiesListItem.propTypes = {
  result: PropTypes.object.isRequired,
  communityTypeLabelTransparent: PropTypes.bool,
};

UserDashboardCommunitiesListItem.defaultProps = {
  communityTypeLabelTransparent: false,
};

const SearchAppResultViewWithSearchbarWAppName = parametrize(
  SearchAppResultViewWithSearchbar,
  {
    appName: overridableIdPrefix,
  }
);
export const DashboardUploadsSearchLayout = SearchAppLayoutWithSearchbarHOC({
  placeholder: i18next.t("Search in my communities..."),
  appName: overridableIdPrefix,
});
export const componentOverrides = {
  [`${overridableIdPrefix}.EmptyResults.element`]:
    CommunitiesEmptySearchResults,
  [`${overridableIdPrefix}.ResultsList.item`]: UserDashboardCommunitiesListItem,
  [`${overridableIdPrefix}.SearchApp.results`]:
    SearchAppResultViewWithSearchbarWAppName,
  [`${overridableIdPrefix}.SearchBar.element`]: SearchappSearchbarElement,
  [`${overridableIdPrefix}.SearchApp.layout`]: DashboardUploadsSearchLayout,
};

createSearchAppsInit({ componentOverrides });
