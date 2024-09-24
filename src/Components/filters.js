import moment from "moment";

function valueOrZero(value) {
  if (
    value !== null &&
    value !== undefined &&
    value !== Infinity &&
    !isNaN(value)
  ) {
    return parseFloat(value);
  } else {
    return 0;
  }
}

function getTotalsAndAverage(
  necessaryKeys,
  data,
  f,
  startDate,
  conversionEvent
) {
  const start = {};
  necessaryKeys.forEach((key) => {
    start[key] = 0;
  });
  if (!data) return f(start);
  const totalData = data.reduce((accumulator, datum) => {
    if (startDate && moment(datum.date).isBefore(startDate)) {
      return accumulator;
    }
    necessaryKeys.forEach((key) => {
      accumulator[key] = accumulator[key] + valueOrZero(datum[key]);
    });
    return accumulator;
  }, start);
  return f(totalData, conversionEvent);
}

export const filters = {
  cpc: {
    id: "cpc",
    title: "Cost per Click (CPC)",
    f: (datum) => {
      return datum && datum.spend / datum.clicks;
    },
    averageFunction: (data, f, startDate) => {
      return getTotalsAndAverage(["spend", "clicks"], data, f, startDate);
    },
    isLowGood: true,
  },
  cpm: {
    id: "cpm",
    title: "Cost per Mille (CPM)",
    f: (datum) => {
      return datum && (1000 * datum.spend) / datum.impressions;
    },
    averageFunction: (data, f, startDate) => {
      return getTotalsAndAverage(["spend", "impressions"], data, f, startDate);
    },
    isLowGood: true,
  },
  ctr: {
    id: "ctr",
    title: "Click Through Rate (CTR)",
    f: (datum) => {
      return datum && (100 * datum.clicks) / datum.impressions;
    },
    averageFunction: (data, f, startDate) => {
      return getTotalsAndAverage(["clicks", "impressions"], data, f, startDate);
    },
    ySuffix: "%",
  },
  cpa: {
    id: "cpa",
    title: "Cost per Acquisition (CPA)",
    f: (datum, conversionEvent = "purchase") => {
      return (
        datum && datum[conversionEvent] && datum.spend / datum[conversionEvent]
      );
    },
    averageFunction: (data, f, startDate, conversionEvent) => {
      return getTotalsAndAverage(
        ["spend", conversionEvent],
        data,
        f,
        startDate,
        conversionEvent
      );
    },
    isLowGood: true,
    hasConversionEvent: true,
  },
  cvr: {
    id: "cvr",
    title: "Conversion Rate (CVR)",
    f: (datum, conversionEvent = "purchase") => {
      return (
        datum &&
        datum[conversionEvent] &&
        datum.link_click &&
        (100 * datum[conversionEvent]) / datum.link_click
      );
    },
    averageFunction: (data, f, startDate, conversionEvent) => {
      return getTotalsAndAverage(
        ["link_click", conversionEvent],
        data,
        f,
        startDate,
        conversionEvent
      );
    },
    ySuffix: "%",
    hasConversionEvent: true,
  },
  acv: {
    id: "acv",
    title: "Average Conversion Value (ACV)",
    f: (datum, conversionEvent = "purchase") => {
      return (
        datum &&
        datum[conversionEvent] &&
        datum[`${conversionEvent}.value`] &&
        datum[`${conversionEvent}.value`] / datum[conversionEvent]
      );
    },
    averageFunction: (data, f, startDate, conversionEvent) => {
      return getTotalsAndAverage(
        [conversionEvent + ".value", conversionEvent],
        data,
        f,
        startDate,
        conversionEvent
      );
    },
    hasConversionEvent: true,
  },
  roi: {
    id: "roi",
    title: "Return on Investment (ROI)",
    f: (datum, conversionEvent = "purchase") => {
      return (
        datum &&
        datum[`${conversionEvent}.value`] &&
        datum.spend &&
        (100 * (datum[`${conversionEvent}.value`] - datum.spend)) / datum.spend
      );
    },
    averageFunction: (data, f, startDate, conversionEvent) => {
      return getTotalsAndAverage(
        [conversionEvent + ".value", "spend"],
        data,
        f,
        startDate,
        conversionEvent
      );
    },
    ySuffix: "%",
    hasConversionEvent: true,
  },
};
