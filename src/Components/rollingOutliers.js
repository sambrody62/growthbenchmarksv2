const math = require("mathjs");
const moment = require("moment");

export function rollingOutliers(benchmarkData) {
  const outliersData = [];
  const lowerData = [];
  const upperData = [];
  const lookbackWindow = 21;
  const standardDeviations = 2;
  for (let i = 0; i < benchmarkData.length; i++) {
    // get last x days data
    const startIndex = i - lookbackWindow < 0 ? 0 : i - lookbackWindow; // if less than 0, use 0
    const data = benchmarkData
      .slice(startIndex, i + 1)
      .map((datum) => datum.value);

    // calculate the mean, stdev, limits
    const stdDev = math.std(data);
    const mean = math.mean(data);
    const outliersCutoff = stdDev * standardDeviations;

    const lowerLimit = mean - outliersCutoff;
    const upperLimit = mean + outliersCutoff;

    // add upper/lower limit data
    lowerData.push({
      date: benchmarkData[i].date,
      value: lowerLimit,
    });
    upperData.push({
      date: benchmarkData[i].date,
      value: upperLimit,
    });

    // check if anomaly
    if (
      benchmarkData[i].value > upperLimit ||
      benchmarkData[i].value < lowerLimit
    ) {
      // if anomaly add to outliers
      outliersData.push({
        date: benchmarkData[i].date,
        value: benchmarkData[i].value,
      });
    }
  }

  const lowerDataLength = lowerData.length;
  if (lowerDataLength > 0) {
    lowerData.push({
      date: moment(lowerData[lowerDataLength - 1].date).add(1000, "days"),
      value: lowerData[lowerDataLength - 1].value,
    });
  }
  const upperDataLength = upperData.length;
  if (upperDataLength > 0) {
    upperData.push({
      date: moment(upperData[upperDataLength - 1].date).add(1000, "days"),
      value: upperData[upperDataLength - 1].value,
    });
  }

  // return outliers, lower, upper
  return { outliersData, lowerData, upperData };
}
