import React from "react";
import moment from "moment";

import { filters } from "./filters";

export const SEOText = (props) => {
  const {
    metricName,
    userFriendlyBenchmarkName,
    averageData = {},
    numCompanies = {},
  } = props;
  const selectedFilter = filters[metricName];
  const { ySuffix } = selectedFilter;

  const {
    mean = "",
    delta30 = "",
    delta90 = "",
    dateString = moment().format("ll"),
  } = averageData;

  function clean(number) {
    if (isNaN(number)) {
      return "+0";
    }
    return number;
  }

  return (
    <h3
      className="pb-5"
      style={{
        fontSize: "20px",
        fontWeight: "normal",
        fontFamily: "Gothic A1",
      }}
    >
      Facebook Ads {selectedFilter.title} is{" "}
      <b>
        {!ySuffix && "$"}
        {clean(mean)}
        {ySuffix}
      </b>{" "}
      on average for <i>{userFriendlyBenchmarkName}</i>. Updated: {dateString}{" "}
      from the GrowthBenchmarks Index, with <b>{numCompanies} companies</b>{" "}
      tagged as <i>{userFriendlyBenchmarkName}</i>. {selectedFilter.title} went{" "}
      <b>{clean(delta30)}%</b> in the last <i>30 days</i> and{" "}
      <b>{clean(delta90)}%</b> in the last <i>90 days</i>.
    </h3>
  );
};
