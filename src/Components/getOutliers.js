const math = require("mathjs");

export function getOutliers(benchmarkData) {
  const data = benchmarkData.map((datum) => datum.value);

  const stdDev = math.std(data);
  const mean = math.mean(data);
  const outliersCutoff = stdDev * 3;

  const lowerLimit = mean - outliersCutoff;
  const upperLimit = mean + outliersCutoff;

  const outlierData = [];
  for (let i = 0; i < benchmarkData.length; i++) {
    if (
      benchmarkData[i].value > upperLimit ||
      benchmarkData[i].value < lowerLimit
    ) {
      console.log("outlier at ", i);
      outlierData.push({
        date: benchmarkData[i].date,
        value: benchmarkData[i].value,
      });
    } else {
      outlierData.push({
        date: benchmarkData[i].date,
        value: 0,
      });
    }
  }

  return outlierData;
}
