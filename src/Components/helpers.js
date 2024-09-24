import moment from "moment";
import * as math from "mathjs";

import { filters } from "./filters";
import formQuestions from "./formQuestions.json";

export const industries = formQuestions.industries;

export function getBenchmarkFriendlyName(benchmark) {
  if (!benchmark) {
    return null;
  }
  return (
    benchmark[0].toUpperCase() +
    benchmark.split("_").join(" ").split(".").join(": ").slice(1)
  );
}

export function getConversionEventFriendlyName(conversionEventList) {
  if (!conversionEventList || !conversionEventList[0]) {
    return "";
  }
  const [conversionEvent, conversionEventName] = conversionEventList;
  return (
    conversionEventName ||
    conversionEvent[0].toUpperCase() +
      conversionEvent.split("_").join(" ").slice(1)
  );
}

export function calculateMean(data, startDate) {
  if (data.length != 0) {
    let mean = math.mean(
      data
        .filter((datum) => {
          if (startDate) {
            return moment(datum.date).isSameOrAfter(startDate);
          }
          return true;
        })
        .map((data) => data.value)
    );
    data = data.map((data) => data.value);
    mean = String(Math.round((mean + Number.EPSILON) * 100) / 100);
    const d1 = data[0];
    const d60 = data[59];
    const d90 = data[data.length - 1];

    let delta30 = (d90 / d60 - 1) * 100;
    let delta90 = (d90 / d1 - 1) * 100;

    // https://stackoverflow.com/questions/11832914/how-to-round-to-at-most-2-decimal-places-if-necessary
    delta30 = Math.round((delta30 + Number.EPSILON) * 100) / 100;
    delta90 = Math.round((delta90 + Number.EPSILON) * 100) / 100;

    delta30 = delta30 >= 0 ? "+" + String(delta30) : String(delta30);
    delta90 = delta90 >= 0 ? "+" + String(delta90) : String(delta90);
    const dateString = moment().format("ll");
    return { mean, delta30, delta90, dateString };
  }
  return;
}

function getFilteredData(dates, rawData, filter, selectedConversionEvent) {
  return dates.reduce((list, date) => {
    if (!rawData) {
      return list;
    }
    const datum = rawData[date];
    if (!datum) {
      return list;
    }
    const value = filter.f(datum, selectedConversionEvent);
    if (
      value !== null &&
      value !== undefined &&
      value !== Infinity &&
      !isNaN(value)
    ) {
      list.push({
        date: moment(date, "YYYY-MM-DD"),
        value,
      });
    }
    return list;
  }, []);
}

export const getFilteredDataMap = (
  inputData,
  dates,
  selectedConversionEvent
) => {
  const returnData = {};
  Object.keys(filters).forEach((key) => {
    const filter = filters[key];
    returnData[filter.id] = getFilteredData(
      dates,
      inputData,
      filter,
      selectedConversionEvent
    );
  });
  return returnData;
};
