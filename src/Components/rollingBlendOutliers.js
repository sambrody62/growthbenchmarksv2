const math = require("mathjs");

export function rollingBlendOutliers(benchmarkData, isBenchmark = true) {
  if (!isBenchmark || benchmarkData.length === 0) {
    return benchmarkData;
  }
  const lookbackWindow = 30;
  const blendedData = [];
  for (let i = 0; i < benchmarkData.length; i++) {
    const startIndex = i - lookbackWindow < 0 ? 0 : i - lookbackWindow; // if less than 0, use 0
    const data = benchmarkData
      .slice(startIndex, i + 1)
      .map((datum) => datum.value);

    const stdDev = math.std(data);
    const mean = math.mean(data);
    const outliersCutoff = stdDev * 3;

    const lowerLimit = mean - outliersCutoff;
    const upperLimit = mean + outliersCutoff;
    if (
      benchmarkData[i].value > upperLimit ||
      benchmarkData[i].value < lowerLimit
    ) {
      console.log("outlier at ", i);
      blendedData.push({ date: benchmarkData[i].date, value: mean });
    } else {
      console.log("no outlier at ", i);
      console.log(lowerLimit, benchmarkData[i].value, upperLimit);
      blendedData.push({
        date: benchmarkData[i].date,
        value: benchmarkData[i].value * 1.5,
      });
    }
  }

  return blendedData;
}
