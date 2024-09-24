import React, { useState, useEffect, useMemo } from "react";
import moment from "moment";
import { useParams } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner } from "@fortawesome/fontawesome-free-solid";

import { firebase } from "./Firebase";
import { filters } from "./filters";
import { allConversionEvents } from "./allConversionEvents";
import myFetch from "./myFetch";
import { Chart } from "./Chart";
import { Navigation } from "./Navigation";
import { Home } from "./Home";
import { Footer } from "./Footer";
import { AccountForm } from "./Form";
import { getFilteredDataMap, getBenchmarkFriendlyName } from "./helpers";
import {
  FACEBOOK_FAKE_PROVIDER,
  FACEBOOK_PROVIDER,
  GOOGLE_FAKE_PROVIDER,
  GOOGLE_PROVIDER,
} from "./providers";

export const Main = (props) => {
  const { user, setUser } = props;

  const [isEditingAccount, setIsEditingAccount] = useState(false);
  const [selectedBenchmarks, setSelectedBenchmarks] = useState([
    "all_companies",
  ]);
  let refreshDataTimer;

  const [allBenchmarks, setAllBenchmarks] = useState([
    selectedBenchmarks.length > 0 && selectedBenchmarks[0],
  ]);
  const [isCreatingAnExampleCompany, setIsCreatingAnExampleCompany] = useState(
    false
  );
  const [startDate, setStartDate] = useState();
  const [didInitiallyFetch, setDidInitiallyFetch] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isFetchingBenchmarkData, setIsFetchingBenchmarkData] = useState(false);
  const [isLoadingCompanies, setIsLoadingCompanies] = useState(true);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const [companiesList, setCompaniesList] = useState([]);
  const [dates, setDates] = useState([]);
  const [allRawData, setAllRawData] = useState();
  const [allBenchmarkRawData, setAllBenchmarkRawData] = useState({});
  const [allSimilarCompaniesRawData, setAllSimilarCompaniesRawData] = useState(
    []
  );

  function getDefaultBenchmark() {
    if (selectedBenchmarks.length === 0) {
      setSelectedBenchmarks(["all_companies"]);
    }
    const firstSelectedBenchmark =
      selectedBenchmarks &&
      selectedBenchmarks.length > 0 &&
      selectedBenchmarks[0];
    return {
      value: firstSelectedBenchmark,
      label: getBenchmarkFriendlyName(firstSelectedBenchmark),
      isBenchmark: true,
    };
  }

  const [selectedFilter, setFilter] = useState(filters.cpc);
  const [selectedConversionEvent, setSelectedConversionEvent] = useState();
  const [selectedCompany, setSelectedCompany] = useState({});

  const [selectedCharts, setSelectedCharts] = useState([
    {
      value: "you",
      label: selectedCompany?.name || selectedCompany.account_id,
    },
    { value: "similar_companies", label: "Similar Companies" },
    getDefaultBenchmark(),
  ]);

  useEffect(() => {
    myFetch
      .get(`/${selectedCompany?.providerId || "facebook"}/benchmarks/list`)
      .then((response) => response.json())
      .then((data) => {
        const { benchmarks } = data;
        setAllBenchmarks(benchmarks);
      })
      .catch((errorGettingBenchmarks) => {
        console.error(
          "Error getting benchmarks list: " + errorGettingBenchmarks
        );
      });

    if (selectedFilterId) {
      const newSelectedFilterKey = Object.keys(filters).find(
        (filterKey) => filterKey === selectedFilterId
      );
      setFilter(filters[newSelectedFilterKey]);
    }

    checkUser();
    if (selectedCompanyId) {
      setSelectedCompany({ account_id: selectedCompanyId });
      setIsLoadingCompanies(true);
    } else {
      try {
        const selectedCompany = JSON.parse(
          localStorage.getItem("selectedCompany")
        );
        if (selectedCompany) {
          setSelectedCompany(selectedCompany);
          setSelectedChartsWithDefaults(selectedCompany);
        }
      } catch (errorParsingSelectedCompany) {
        console.log("Could not parse selected company");
      }
    }
    setIsLoading(false);

    firebase.auth().onAuthStateChanged(() => {
      const firebaseUser = firebase.auth().currentUser;
      if (firebaseUser && !didInitiallyFetch) {
        setDidInitiallyFetch(true);
        fetchData();
      }
    });
  }, []);

  function setSelectedFilter(newFilter) {
    setFilter(newFilter, setURL);
  }

  useEffect(() => {
    clearTimeout(refreshDataTimer);
  }, [selectedCompany]);

  useEffect(() => {
    setURL();
  }, [selectedFilter, selectedCompany]);

  useEffect(() => {
    setSelectedCharts(
      selectedCharts.map((chart) => {
        if (chart.value === "you") {
          chart.label = selectedCompany?.name || selectedCompany.account_id;
        }
        return { ...chart };
      })
    );
  }, [selectedCompany]);

  useEffect(() => {
    fetchBenchmarkData();
  }, [selectedBenchmarks]);

  const { selectedCompanyId, selectedFilterId } = useParams();

  function setURL() {
    if (!user) {
      props.history.push("/");
      return;
    }
    props.history.push(
      `/${selectedCompany && selectedCompany.account_id}/${
        selectedFilter && selectedFilter.id
      }`
    );
  }

  function setSelectedChartsWithDefaults(newSelectedCompany) {
    if (newSelectedCompany?.isExampleCompany) {
      setSelectedCharts([
        { value: "similar_companies", label: "Similar Companies" },
        getDefaultBenchmark(),
      ]);
    } else {
      setSelectedCharts([
        {
          value: "you",
          label: newSelectedCompany?.name || newSelectedCompany.account_id,
        },
        { value: "similar_companies", label: "Similar Companies" },
        getDefaultBenchmark(),
      ]);
    }
  }

  function checkUser() {
    try {
      const authUser = JSON.parse(localStorage.getItem("user"));
      if (authUser) {
        setUser(authUser);
        setIsLoadingCompanies(false);
      }
    } catch (e) {
      console.log("There was an error loading the data/user: " + e);
    }
  }

  function getAverage(rawData) {
    if (!rawData) {
      return NaN;
    }
    const data = Object.keys(rawData).map((key) => rawData[key]);
    return selectedFilter.averageFunction(
      data,
      selectedFilter.f,
      startDate,
      selectedConversionEvent
    );
  }

  const data = useMemo(() => {
    return getFilteredDataMap(allRawData, dates, selectedConversionEvent);
  }, [allRawData, selectedConversionEvent]);

  const benchmarkData = useMemo(() => {
    const result = {};
    selectedBenchmarks.forEach((benchmark) => {
      result[benchmark] = getFilteredDataMap(
        allBenchmarkRawData[benchmark],
        dates,
        selectedConversionEvent
      );
    });
    return result;
  }, [allBenchmarkRawData, selectedConversionEvent, selectedBenchmarks]);

  const similarCompaniesData = useMemo(() => {
    return getFilteredDataMap(
      allSimilarCompaniesRawData,
      dates,
      selectedConversionEvent
    );
  }, [allSimilarCompaniesRawData, selectedConversionEvent]);

  const conversionEvents = useMemo(() => {
    return allConversionEvents.reduce(
      (conversionEventsList, [conversionEvent, conversionEventName]) => {
        if (!allRawData && !allBenchmarkRawData) {
          return conversionEventsList;
        }

        if (
          dates.find((date) => {
            const datum = allRawData && allRawData[date];
            const similarCompaniesDatum =
              allSimilarCompaniesRawData && allSimilarCompaniesRawData[date];

            const benchmarkDatums = [];

            if (allBenchmarkRawData) {
              for (const selectedChart of selectedCharts) {
                if (selectedChart.isBenchmark) {
                  const selectedBenchmark = selectedChart.value;
                  if (allBenchmarkRawData[selectedBenchmark]) {
                    benchmarkDatums.push(
                      allBenchmarkRawData[selectedBenchmark][date]
                    );
                  }
                }
              }
            }

            return (
              (datum &&
                datum[conversionEvent] !== null &&
                datum[conversionEvent] !== undefined) ||
              (similarCompaniesDatum &&
                similarCompaniesDatum[conversionEvent] !== null &&
                similarCompaniesDatum[conversionEvent] !== undefined) ||
              benchmarkDatums.some(
                (benchmarkDatum) =>
                  benchmarkDatum &&
                  benchmarkDatum[conversionEvent] !== null &&
                  benchmarkDatum[conversionEvent] !== undefined
              )
            );
          })
        ) {
          conversionEventsList.push([conversionEvent, conversionEventName]);
          if (!selectedConversionEvent) {
            setSelectedConversionEvent(conversionEvent);
          }
        }
        return conversionEventsList;
      },
      []
    );
  }, [allRawData, allBenchmarkRawData, dates]);

  function updateData(data, companyId) {
    if (companyId) {
      let cache = {};
      try {
        cache = JSON.parse(localStorage.getItem("cache")) || {};
      } catch {
        console.log("Could not process cache");
      }

      cache[companyId] = data;
      cache[companyId].lastFetch = moment();
      try {
        localStorage.setItem("cache", JSON.stringify(cache));
      } catch (errorSavingLocalStorage) {
        console.log(
          "Error storing localstorage; removing old data and trying again: " +
            errorSavingLocalStorage
        );
        const cacheKeysSortedByAge = Object.keys(cache).sort((keyA, keyB) => {
          cache[keyA] &&
          cache[keyA].lastFetch > cache[keyB] &&
          cache[keyB].lastFetch
            ? 1
            : -1;
        });
        const oldestKey = cacheKeysSortedByAge[0];
        delete cache[oldestKey];
        try {
          localStorage.setItem("cache", JSON.stringify(cache));
        } catch (errorSavingSecondTime) {
          console.error(
            "Could not save cache even with old data removed: " +
              errorSavingSecondTime
          );
          localStorage.removeItem("cache");
        }
      }
    }
    const actualData = data.you;
    const benchmarks = data.benchmarks;
    const similarCompaniesData = data.similar_companies;
    const dates = data.dates;
    if (dates) {
      const allRawData = dates.reduce((allData, date) => {
        allData[date] = { ...actualData[date], date };
        return allData;
      }, {});
      const allSimilarCompaniesRawData = dates.reduce((allData, date) => {
        allData[date] = { ...similarCompaniesData[date], date };
        return allData;
      }, {});
      setDates(dates);
      setAllRawData(allRawData);
      setAllSimilarCompaniesRawData(allSimilarCompaniesRawData);
      processAllBenchmarkData(benchmarks);
    } else {
      setDates([]);
      setAllRawData([]);
      setAllBenchmarkRawData({});
      setAllSimilarCompaniesRawData([]);
    }
  }

  function saveUser(user) {
    myFetch
      .post("/user/upsert", { user })
      .then((response) => response.json())
      .then((data) => {
        if (!data.success) {
          alert("Error saving the user to the databse: " + data.message);
        }

        if (data.isNewUser) {
          // push signup event
          window.dataLayer = window.dataLayer || [];
          window.dataLayer.push({
            eventCategory: "Account",
            eventAction: "Sign Up",
            eventLabel:
              user.providerId === FACEBOOK_PROVIDER
                ? "Facebook"
                : user.providerId === GOOGLE_PROVIDER
                ? "Google"
                : user.providerId,
            event: "SignUp",
          });
          fetchData();
        }
      });
  }

  async function fetchData() {
    setDidInitiallyFetch(true);
    const { currentUser } = firebase.auth();
    if (currentUser) {
      setIsLoadingCompanies(true);
      setIsLoadingData(true);
      myFetch
        .get("/user/get_my_companies")
        .then(async (response) => {
          if (!response.ok) {
            throw new Error("Server down!");
          }
          return response.json();
        })
        .then((data) => {
          const { companiesList: newCompaniesList } = data;
          if (!data || !newCompaniesList) {
            setIsLoadingCompanies(false);
            const errorMessage = "Got no companies!";
            alert(errorMessage);
            console.error(errorMessage);
            return;
          }
          setCompaniesList(newCompaniesList);
          // If it is the first time the user loads this page, then they will not have
          // any companies yet, so it will still be loading in the background...
          if (currentUser.emailVerified || newCompaniesList?.length > 0) {
            setIsLoadingCompanies(false);
          }

          if (currentUser.emailVerified && newCompaniesList?.length === 0) {
            setIsCreatingAnExampleCompany(true);
          }

          let selectedCompany =
            newCompaniesList &&
            newCompaniesList.length > 0 &&
            newCompaniesList[0];
          try {
            const cachedSelectedCompany =
              localStorage.getItem("selectedCompany") &&
              JSON.parse(localStorage.getItem("selectedCompany"));
            if (cachedSelectedCompany) {
              selectedCompany = cachedSelectedCompany;
            }
          } catch (error) {
            console.error("Could not process locally stored selected company");
          }

          if (newCompaniesList && newCompaniesList.length > 0) {
            handleSelectCompany(
              selectedCompany && selectedCompany.account_id,
              newCompaniesList
            );
          }
        })
        .catch((errorGettingMyCompanies) => {
          const errorMessage =
            "Could not get my companies: " + errorGettingMyCompanies;
          alert(errorMessage);
          setIsLoadingCompanies(false);
          console.error(errorMessage);
        });
    } else {
      setIsLoadingData(true);
      getDataFetch();
    }
  }

  const onLogout = () => {
    setUser(null);
    setCompaniesList([]);
    setAllRawData([]);
    setAllBenchmarkRawData({});
    setAllSimilarCompaniesRawData([]);
    setSelectedCompany({});
    props.logout();
    props.history.push("/");
  };

  const onLogin = (user) => {
    setUser(user);
    localStorage.setItem("user", JSON.stringify(user));

    const providerId =
      user?.additionalUserInfo?.providerId === "facebook.com"
        ? FACEBOOK_PROVIDER
        : user?.additionalUserInfo?.providerId === "google.com"
        ? GOOGLE_PROVIDER
        : user?.additionalUserInfo?.providerId;

    let userData = {
      id: user?.additionalUserInfo?.profile?.id,
      name: user?.additionalUserInfo?.profile?.name,
      displayName: user?.user?.displayName,
      email: user?.additionalUserInfo?.profile?.email,
      uid: user?.user?.uid,
      provider_id: providerId,
    };

    switch (providerId) {
      case FACEBOOK_PROVIDER:
        userData = {
          ...userData,
          first_name: user?.additionalUserInfo?.profile?.first_name,
          last_name: user?.additionalUserInfo?.profile?.last_name,
          access_token: user?.credential?.accessToken,
          refresh_token: user?.user?.refreshToken,
          facebook_access_token: user?.credential?.accessToken,
        };
        break;
      case GOOGLE_PROVIDER:
        userData = {
          ...userData,
          first_name: user?.additionalUserInfo?.profile?.given_name,
          last_name: user?.additionalUserInfo?.profile?.family_name,
          google_access_token: user?.credential?.accessToken,
          google_refresh_token: user?.credential?.refreshToken,
        };
        break;
    }

    saveUser(userData);
  };

  const handleSelectCompany = (
    companyAccountId,
    allCompaniesList = companiesList
  ) => {
    setIsLoadingData(true);
    setIsEditingAccount(false);
    let selectedCompanyData = allCompaniesList?.find(
      (company) => company?.account_id === companyAccountId
    );
    if (!selectedCompanyData) {
      selectedCompanyData =
        allCompaniesList && allCompaniesList.length > 0 && allCompaniesList[0];
    }
    setSelectedCompany(selectedCompanyData);
    setSelectedChartsWithDefaults(selectedCompanyData);
    setSelectedConversionEvent(
      (selectedCompanyData && selectedCompanyData.conversion_event) || ""
    );
    localStorage.setItem(
      "selectedCompany",
      JSON.stringify(selectedCompanyData)
    );

    if (
      !selectedCompanyData ||
      (!selectedCompanyData.isExampleCompany &&
        !selectedCompanyData.has_completed_questionnaire)
    ) {
      setIsLoadingData(false);
      return;
    }

    let cache = {};
    try {
      cache = JSON.parse(localStorage.getItem("cache"));
    } catch {
      console.log("Could not parse cache from local storage");
    }
    const cachedData = cache && cache[companyAccountId];

    if (
      cachedData &&
      moment(cachedData.lastFetch).isSameOrAfter(moment().startOf("day")) &&
      cachedData.has_completed_first_fb_data_pull
    ) {
      updateData(cachedData, null);
      setIsLoadingData(false);
      return;
    }
    getDataFetch(companyAccountId, selectedCompanyData?.provider_id);
  };

  const processAllBenchmarkData = (benchmarks) => {
    const newAllBenchmarksRawData = {};
    for (const benchmark of benchmarks) {
      const dates = benchmark.dates;
      const newBenchmarksRawData = dates.reduce((allData, date) => {
        allData[date] = { ...benchmark.benchmark[date], date };
        return allData;
      }, {});

      newAllBenchmarksRawData[benchmark.name] = newBenchmarksRawData;
    }

    setAllBenchmarkRawData(newAllBenchmarksRawData);
  };

  let dataSource = "facebook";
  const providerId = selectedCompany?.provider_id;
  if (
    providerId === FACEBOOK_PROVIDER ||
    providerId === FACEBOOK_FAKE_PROVIDER
  ) {
    dataSource = "facebook";
  } else if (
    providerId === GOOGLE_PROVIDER ||
    providerId === GOOGLE_FAKE_PROVIDER
  ) {
    dataSource = "google";
  }

  const fetchBenchmarkData = () => {
    setIsFetchingBenchmarkData(true);
    myFetch
      .post(`/${dataSource}/get_benchmark_data`, {
        selectedBenchmarks,
        currency: selectedCompany && selectedCompany.currency,
      })
      .then((response) => {
        setIsFetchingBenchmarkData(false);
        return response.json();
      })
      .then((data) => {
        processAllBenchmarkData(data.benchmarks);
      })
      .catch((errorGettingBenchmarkData) => {
        setIsFetchingBenchmarkData(false);
        setIsLoadingData(false);
        console.error(
          "Error getting benchmark data: " + errorGettingBenchmarkData
        );
      });
  };

  const getDataFetch = (companyAccountId, providerId) => {
    const currentUser = firebase.auth().currentUser;
    let filter = {};
    if (companyAccountId) {
      filter = {
        providerId,
        companyId: companyAccountId,
        selectedBenchmarks,
      };
    }

    if (currentUser) {
      myFetch
        .post("/user/get_data", filter)
        .then((response) => {
          return response.json();
        })
        .then((data) => {
          if (data.error) {
            updateData({}, companyAccountId);
            setIsLoadingData(false);
          } else {
            if (!companyAccountId || data.account_id === companyAccountId) {
              // Check the data is for the selected company
              updateData(data, companyAccountId);
              setIsLoadingData(false);

              if (
                (selectedCompany.provider_id === GOOGLE_PROVIDER ||
                  selectedCompany.provider_id === FACEBOOK_PROVIDER) &&
                companyAccountId &&
                data.you &&
                !data.has_completed_first_data_pull
              ) {
                refreshDataTimer = setTimeout(() => {
                  getDataFetch(companyAccountId, providerId);
                }, 1000);
              }
            }
          }
        })
        .catch((errorGettingCompanyData) => {
          setIsLoadingData(false);
          console.error(
            "Error getting company data: " + errorGettingCompanyData
          );
        });
    } else {
      setIsLoadingData(false);
    }
  };

  const handleSelectConversionEvent = (newConversionEvent) => {
    setSelectedConversionEvent(newConversionEvent);
    myFetch
      .post("/facebook/set_conversion_event", {
        account_id: selectedCompany?.account_id,
        conversion_event: newConversionEvent,
        is_example_company: selectedCompany?.isExampleCompany,
      })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) {
          console.error("There was an error updating the conversion event");
        }
      })
      .catch((errorUpdatingConversionEvent) => {
        console.error(
          "There was an error updating the conversion Event: " +
            errorUpdatingConversionEvent
        );
      });
  };

  const handleSaveCompany = (newCompanyDetails) => {
    setIsSaving(true);

    if (!isCreatingAnExampleCompany) {
      newCompanyDetails.companyId = selectedCompany?.account_id;

      try {
        const cache = JSON.parse(localStorage.getItem("cache")) || {};
        cache[companyId] = null;
        localStorage.setItem("cache", JSON.stringify(cache));
      } catch {
        console.log("Could not parse cache of data");
      }

      // setSelectedCompany(newCompanyDetails);
    }

    let { dataSource, isExampleCompany, provider_id } = newCompanyDetails;

    if (!dataSource) {
      dataSource =
        provider_id === FACEBOOK_PROVIDER
          ? "facebook"
          : provider_id === GOOGLE_PROVIDER
          ? "google"
          : "";
    }

    let newProviderId = FACEBOOK_PROVIDER;

    if (dataSource === "facebook" && isExampleCompany) {
      newProviderId = FACEBOOK_FAKE_PROVIDER;
    } else if (dataSource === "google" && isExampleCompany) {
      newProviderId = GOOGLE_FAKE_PROVIDER;
    } else if (dataSource === "google" && !isExampleCompany) {
      newProviderId = GOOGLE_PROVIDER;
    }

    newCompanyDetails.provider_id = newProviderId;

    myFetch
      .post(`/${dataSource}/set_company_data`, { company: newCompanyDetails })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        const { updatedCompany } = data;
        const newCompaniesList = companiesList.map((company) => {
          if (company?.account_id === selectedCompany?.account_id) {
            return updatedCompany;
          } else {
            return company;
          }
        });
        setCompaniesList(newCompaniesList);
        setSelectedCompany(updatedCompany);
        localStorage.setItem("selectedCompany", JSON.stringify(updatedCompany));
        setIsSaving(false);
        setIsCreatingAnExampleCompany(false);
        fetchData();
      })
      .catch((error) => {
        console.log("Error saving data: " + error);
        setIsCreatingAnExampleCompany(false);
        setIsSaving(false);
      });
  };

  const allData = useMemo(() => {
    const result = [];
    for (const selectedChart of selectedCharts) {
      if (selectedChart.value === "you") {
        result.push(data[selectedFilter.id]);
      }
      if (selectedChart.value === "similar_companies") {
        result.push(similarCompaniesData[selectedFilter.id]);
      }
      if (selectedChart.isBenchmark) {
        const selectedBenchmark = selectedChart.value;
        if (
          benchmarkData[selectedBenchmark] &&
          benchmarkData[selectedBenchmark][selectedFilter.id]
        ) {
          result.push(benchmarkData[selectedBenchmark][selectedFilter.id]);
        }
      }
    }
    return result;
  }, [
    selectedFilter,
    data,
    similarCompaniesData,
    selectedBenchmarks,
    benchmarkData,
  ]);

  const averages = useMemo(() => {
    const result = [];
    for (const selectedChart of selectedCharts) {
      if (selectedChart.value === "you") {
        const average = getAverage(allRawData);
        result.push(average);
      }
      if (selectedChart.value === "similar_companies") {
        const average = getAverage(allSimilarCompaniesRawData);
        result.push(average);
      }
      if (selectedChart.isBenchmark) {
        const selectedBenchmark = selectedChart.value;
        if (allBenchmarkRawData[selectedBenchmark]) {
          const average = getAverage(allBenchmarkRawData[selectedBenchmark]);
          result.push(average);
        }
      }
    }

    return result;
  }, [
    allRawData,
    allSimilarCompaniesRawData,
    allBenchmarkRawData,
    startDate,
    selectedConversionEvent,
    selectedFilter,
  ]);

  const allDataWithFilter = (filter) => {
    const result = [];
    for (const selectedChart of selectedCharts) {
      if (selectedChart.value === "you") {
        result.push(data[filter.id]);
      }
      if (selectedChart.value === "similar_companies") {
        result.push(similarCompaniesData[filter.id]);
      }
      if (selectedChart.isBenchmark) {
        const selectedBenchmark = selectedChart.value;
        if (
          benchmarkData[selectedBenchmark] &&
          benchmarkData[selectedBenchmark][filter.id]
        ) {
          result.push(benchmarkData[selectedBenchmark][filter.id]);
        }
      }
    }
    return result;
  };

  return !user ? (
    <Home onLogin={onLogin} checkUser={() => checkUser()} />
  ) : (
    <>
      <Navigation
        user={user}
        isLoading={isLoading}
        isLoadingCompanies={isLoadingCompanies || !didInitiallyFetch}
        selectedCompany={selectedCompany}
        companiesList={companiesList}
        handleSelectCompany={handleSelectCompany}
        onLogout={onLogout}
      />

      <div
        className="ml-auto mr-auto mt-5 main-content text-center"
        style={{ flex: "1 0 auto", maxWidth: 1000 }}
      >
        {user &&
          didInitiallyFetch &&
          !isLoadingCompanies &&
          isLoadingData &&
          (selectedCompany?.isExampleCompany ||
            selectedCompany?.has_completed_questionnaire) && (
            <>
              <h2>Loading Data...</h2>
              <FontAwesomeIcon icon={faSpinner} spin />
            </>
          )}

        {!isLoadingCompanies &&
          user &&
          (isCreatingAnExampleCompany ||
            (selectedCompany &&
              !selectedCompany.has_completed_questionnaire &&
              !selectedCompany.isExampleCompany) ||
            isEditingAccount) && (
            <AccountForm
              isEditingAccount={isEditingAccount}
              isCreatingAnExampleCompany={isCreatingAnExampleCompany}
              selectedCompany={selectedCompany}
              key={selectedCompany.account_id}
              isSaving={isSaving}
              onSubmit={(newCompanyData) => {
                handleSaveCompany(newCompanyData);
              }}
              onCancel={() => {
                setIsEditingAccount(false);
                setIsCreatingAnExampleCompany(false);
              }}
            />
          )}

        {!isLoadingData &&
          !isLoadingCompanies &&
          user &&
          !isCreatingAnExampleCompany &&
          selectedCompany &&
          (selectedCompany.has_completed_questionnaire ||
            selectedCompany.isExampleCompany) &&
          !isEditingAccount && (
            <>
              <Chart
                title="Facebook Ads Benchmark"
                companyName={selectedCompany.name}
                metric={selectedFilter.title}
                allData={allData}
                isBenchmarkOnly={user.isLoggedInWithEmail}
                doesHideYou={selectedCompany?.isExampleCompany}
                currency={selectedCompany.currency}
                dates={dates}
                ySuffix={selectedFilter.ySuffix}
                isLoadingData={isLoadingData || isFetchingBenchmarkData}
                isLowGood={selectedFilter.isLowGood}
                handleSelectConversionEvent={handleSelectConversionEvent}
                hasConversionEvent={selectedFilter.hasConversionEvent}
                selectedConversionEvent={selectedConversionEvent}
                conversionEvents={conversionEvents || []}
                selectedCharts={selectedCharts}
                handleSelectCharts={(newSelectedCharts) => {
                  const newSelectedBenchmarks = newSelectedCharts
                    .filter((newSelectedChart) => {
                      return newSelectedChart.isBenchmark;
                    })
                    .map((newSelectedChart) => {
                      return newSelectedChart.value;
                    });
                  setSelectedBenchmarks(newSelectedBenchmarks);
                  setSelectedCharts(newSelectedCharts);
                }}
                allBenchmarks={allBenchmarks}
                averages={averages}
                setStartDate={setStartDate}
              />

              <h2 className="p-3 text-left">Other Facebook Ads Benchmarks</h2>

              <div className="d-flex flex-wrap justify-content-center text-center">
                {Object.keys(filters).map((key) => {
                  const filter = filters[key];
                  if (selectedFilter !== filter) {
                    return (
                      <Chart
                        key={filter.title}
                        metric={filter.title}
                        allData={allDataWithFilter(filter)}
                        selectedCharts={selectedCharts}
                        dates={dates}
                        isLoadingData={isLoadingData}
                        ySuffix={filter.ySuffix}
                        onClick={() => {
                          window.scrollTo(0, 0);
                          setSelectedFilter(filter);
                        }}
                        isSmall={true}
                      />
                    );
                  } else {
                    return null;
                  }
                })}
              </div>
              <div className="py-3">
                <a href="#" onClick={() => setIsEditingAccount(true)}>
                  Edit account
                </a>
              </div>
            </>
          )}
        {!isLoadingData &&
          !isLoadingCompanies &&
          user &&
          !isCreatingAnExampleCompany && (
            <>
              <div className="py-3">
                Create an{" "}
                <a
                  href="#"
                  onClick={() => {
                    setIsCreatingAnExampleCompany(true);
                  }}
                >
                  example company
                </a>
              </div>
              <div className="py-3">
                Visit your <a href="/profile">profile</a>
              </div>
            </>
          )}
      </div>
      <Footer />
    </>
  );
};
