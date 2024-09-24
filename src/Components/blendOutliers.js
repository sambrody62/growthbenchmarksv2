const math = require("mathjs");

export function blendOutliers(benchmarkData, isBenchmark = false) {
  if (!isBenchmark || benchmarkData.length === 0) {
    return benchmarkData;
  }
  const data = benchmarkData.map((datum) => datum.value);

  const stdDev = math.std(data);
  const mean = math.mean(data);
  const outliersCutoff = stdDev * 3;

  const lowerLimit = mean - outliersCutoff;
  const upperLimit = mean + outliersCutoff;

  const blendedData = [];
  for (let i = 0; i < benchmarkData.length; i++) {
    if (
      benchmarkData[i].value > upperLimit ||
      benchmarkData[i].value < lowerLimit
    ) {
      const blendedValue = math.mean(mean, benchmarkData[i].value);
      blendedData.push({
        date: benchmarkData[i].date,
        value: blendedValue,
      });
    } else {
      blendedData.push({
        date: benchmarkData[i].date,
        value: benchmarkData[i].value,
      });
    }
  }

  return blendedData;
}
