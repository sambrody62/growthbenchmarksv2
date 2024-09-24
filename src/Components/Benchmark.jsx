import React, { useState, useMemo, useEffect } from "react";
import { useParams } from "react-router-dom";
import moment from "moment";

import { filters } from "./filters";
import { allConversionEvents as conversionEvents } from "./allConversionEvents";
import { Chart } from "./Chart";
import { Navigation } from "./Navigation";
import { Footer } from "./Footer";
import { getFilteredDataMap, calculateMean } from "./helpers";
import { SEOText } from "./SEOText";
import { cachedBenchmarks } from "./cachedBenchmarks";
import myFetch from "./myFetch";

export const Benchmark = (props) => {
  const { embedded = false } = props;
  const {
    providerName,
    metricName,
    benchmarkName,
    benchmarkPrefixName,
    benchmarkSuffixName,
  } = useParams();

  const fullBenchmarkName =
    benchmarkName || benchmarkPrefixName + "." + benchmarkSuffixName;

  const userFriendlyBenchmarkName =
    (benchmarkName &&
      benchmarkName[0].toUpperCase() +
        benchmarkName.split("_").join(" ").slice(1)) ||
    (benchmarkSuffixName &&
      benchmarkSuffixName[0].toUpperCase() +
        benchmarkSuffixName.split("_").join(" ").slice(1));

  const userFriendlyProviderName =
    providerName[0].toUpperCase() + providerName.split("_").join(" ").slice(1);

  const [isLoadingData, setIsLoadingData] = useState(true);
  const [startDate, setStartDate] = useState();
  const [selectedConversionEvent, setSelectedConversionEvent] = useState();
  const [dates, setDates] = useState([]);
  const [allBenchmarkRawData, setAllBenchmarkRawData] = useState();
  const [selectedCharts, setSelectedCharts] = useState([
    {
      value: fullBenchmarkName,
      label: userFriendlyBenchmarkName,
      isBenchmark: true,
    },
  ]);

  const benchmarkData = useMemo(() => {
    return getFilteredDataMap(
      allBenchmarkRawData,
      dates,
      selectedConversionEvent
    );
  }, [allBenchmarkRawData, selectedConversionEvent]);

  useEffect(() => {
    setIsLoadingData(true);
    myFetch
      .get(`/${providerName}/${fullBenchmarkName}/get_benchmark`)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        setIsLoadingData(false);
        setDates(data.dates);
        setAllBenchmarkRawData(data.benchmark);
        setSelectedCharts([
          {
            value: fullBenchmarkName,
            label: userFriendlyBenchmarkName,
            isBenchmark: true,
          },
        ]);
      });
  }, [
    providerName,
    metricName,
    benchmarkName,
    benchmarkPrefixName,
    benchmarkSuffixName,
  ]);

  const selectedFilter = filters[metricName];

  const averageData = useMemo(() => {
    if (benchmarkData[selectedFilter.id].length > 0) {
      return calculateMean(benchmarkData[selectedFilter.id], startDate);
    }
    const cachedBenchmarkMetrics = cachedBenchmarks[metricName];
    if (!cachedBenchmarkMetrics) {
      return;
    }
    const cachedBenchmarkValues = cachedBenchmarkMetrics[fullBenchmarkName];
    if (!cachedBenchmarkValues) {
      return;
    }
    const mean = cachedBenchmarkValues["mean"];
    const delta30 = cachedBenchmarkValues["delta30"];
    const delta90 = cachedBenchmarkValues["delta90"];
    const dateString = moment(cachedBenchmarks.updated).format("ll");
    return {
      mean,
      delta30,
      delta90,
      dateString,
    };
  }, [benchmarkData, startDate]);

  const average = useMemo(() => {
    return averageData && averageData.mean;
  }, [averageData]);

  const averages = useMemo(() => {
    return [average];
  }, [average, selectedCharts]);

  const [numCompanies, setNumCompanies] = useState("169");
  useEffect(() => {
    myFetch
      .get(`/${providerName}/num_companies`)
      .then((response) => {
        return response.json();
      })
      .then((json) => {
        const numResp = JSON.stringify(json["num_companies"]);
        setNumCompanies(numResp);
      })
      .catch((error) => {
        console.log(error, "Error with fetching num_companies");
      });
  }, []);

  return (
    <>
      {!embedded && <Navigation />}
      <div
        className="ml-auto mr-auto mt-5 main-content text-center"
        style={{
          flex: "1 0 auto",
          maxWidth: 1000,
        }}
      >
        {!embedded && (
          <>
            <h1>
              {userFriendlyProviderName} {selectedFilter.title} for{" "}
              {userFriendlyBenchmarkName}
            </h1>
            <SEOText
              userFriendlyBenchmarkName={userFriendlyBenchmarkName}
              metricName={metricName}
              averageData={averageData}
              numCompanies={numCompanies}
            />
          </>
        )}
        <Chart
          title={`Facebook Ads ${selectedFilter.title} Benchmark`}
          metric={selectedFilter.title}
          isBenchmarkOnly={true}
          allData={[benchmarkData && benchmarkData[selectedFilter.id]]}
          currency={"USD"}
          dates={dates}
          ySuffix={selectedFilter.ySuffix}
          isLoadingData={isLoadingData}
          isLowGood={selectedFilter.isLowGood}
          hasConversionEvent={selectedFilter.hasConversionEvent}
          handleSelectConversionEvent={(newEvent) =>
            setSelectedConversionEvent(newEvent)
          }
          selectedConversionEvent={selectedConversionEvent}
          conversionEvents={conversionEvents || []}
          selectedCharts={selectedCharts}
          handleSelectCharts={(newSelectedCharts) =>
            setSelectedCharts(newSelectedCharts)
          }
          allBenchmarks={[fullBenchmarkName]}
          canChooseCharts={false}
          setStartDate={setStartDate}
          averages={averages}
        />
      </div>
      {!embedded && <Footer />}
    </>
  );
};
