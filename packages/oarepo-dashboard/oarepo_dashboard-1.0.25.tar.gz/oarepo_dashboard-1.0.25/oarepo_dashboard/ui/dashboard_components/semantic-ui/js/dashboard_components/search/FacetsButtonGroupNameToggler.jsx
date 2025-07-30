import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Button } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components";

const FacetsButtonGroupNameTogglerComponent = ({
  currentResultsState,
  currentQueryState,
  updateQueryState,
  toggledFilters,
  keepFiltersOnUpdate,
  ...uiProps
}) => {
  const { initialQueryState } = useContext(SearchConfigurationContext);
  const currentFilter = currentQueryState.filters?.find((f) =>
    toggledFilters.map((f) => f.filterName).includes(f[0])
  );
  const initialQueryFacets = initialQueryState.filters?.map((f) => f[0]);
  if (!currentFilter)
    console.error(
      "FacetsButtonGroup: Query does not contain any of the facets you wish to toggle between, please make sure you are passing initialFilters properly"
    );
  const facetStatus = currentFilter && JSON.parse(currentFilter?.[1]);
  const handleFacetNameChange = (facetName) => {
    if (currentFilter[0] === facetName) return;

    currentQueryState.filters = keepFiltersOnUpdate
      ? currentQueryState.filters.filter(
          (element) => element[0] !== currentFilter[0]
        )
      : [
          ...(currentQueryState?.filters
            ? currentQueryState.filters.filter((element) =>
                initialQueryFacets.includes(element[0])
              )
            : []),
        ];
    currentQueryState.filters = currentQueryState.filters.filter(
      (f) => !toggledFilters.map((f) => f.filterName).includes(f[0])
    );

    currentQueryState.filters.push([facetName, facetStatus]);
    updateQueryState(currentQueryState);
  };
  return (
    <Button.Group className="rel-mb-1" {...uiProps}>
      {toggledFilters.map(({ text, filterName }) => (
        <Button
          key={filterName}
          className="request-search-filter"
          onClick={() => handleFacetNameChange(filterName)}
          active={filterName === currentFilter[0]}
        >
          {text}
        </Button>
      ))}
    </Button.Group>
  );
};

FacetsButtonGroupNameTogglerComponent.propTypes = {
  currentQueryState: PropTypes.object.isRequired,
  updateQueryState: PropTypes.func.isRequired,
  currentResultsState: PropTypes.object.isRequired,
  toggledFilters: PropTypes.arrayOf(
    PropTypes.shape({
      filterName: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
    })
  ).isRequired,
  keepFiltersOnUpdate: PropTypes.bool,
};

FacetsButtonGroupNameTogglerComponent.defaultProps = {
  keepFiltersOnUpdate: true,
};
export const FacetsButtonGroupNameToggler = withState(
  FacetsButtonGroupNameTogglerComponent
);
