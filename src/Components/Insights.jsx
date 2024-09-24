import React, { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Col, Row, Button, InputGroup } from "react-bootstrap";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-text";
import "ace-builds/src-noconflict/theme-clouds";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faStar, faSpinner } from "@fortawesome/fontawesome-free-solid";
import { faStar as faStarO } from "@fortawesome/free-regular-svg-icons";

import { filters } from "./filters";
import myFetch from "./myFetch";

export const Insights = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasBeenCopied, setHasBeenCopied] = useState(false);
  const [includeSampleSize, setIncludeSampleSize] = useState(false);
  const [selectedInsights, setSelectedInsights] = useState([]);
  const editorRef = useRef(null);
  const copyAreaRef = useRef(null);

  const { providerName } = useParams();

  // in a useEffect, call to get these from the server
  // combine to get an 'all_insights', a list of lists
  // get all the absolute data (sums) from server
  // use the filters to create the CPC, CPM, etc
  /* 
  {
    "featured": ['insight CPC', 'insight CPM', 'insight CTR', ...],
    "all_companies": ['insight CPC', 'insight CPM', 'insight CTR', ...],
    "industry.cpg": ['insight CPC', 'insight CPM', 'insight CTR', ...],
  }
  */
  // change the map functions below to account for new structure
  // create an endpoint to get the latest insights data
  // create an endpoint (for a cloud scheduled task) to generate insights
  // runs once every day, looking at last month vs the month previous
  // for example, if today is 19th August, we'd run for July vs June
  // function for deciding what is featured (highest difference above a certain sample size)
  // function to select featured insights

  const [filteredInsights, setFilteredInsights] = useState({});
  useEffect(async () => {
    setIsLoading(true);
    // create filteredInsights object
    const updatedFilteredInsights = {};

    const unfilteredInsights = await myFetch
      .get(`/${providerName}/get_commentary`)
      .then((response) => response.json());

    // loop through each benchmark
    Object.keys(unfilteredInsights).forEach((benchmarkKey) => {
      const benchmark = unfilteredInsights[benchmarkKey];

      // loop through each filter
      updatedFilteredInsights[benchmarkKey] = Object.keys(filters).map(
        (filterKey) => {
          const filter = filters[filterKey];
          const lastMonthsValue = filter.f(benchmark.last_month);
          const prevMonthsValue = filter.f(benchmark.prev_month);
          const difference = Math.round(
            (100 * (lastMonthsValue - prevMonthsValue)) / prevMonthsValue
          );
          const insight = {
            benchmarkKey,
            filterKey: filter.title,
            difference,
            accounts: benchmark.accounts,
          };
          return insight;
        }
      );
    });
    const featuredInsights = selectFeatured(updatedFilteredInsights);
    updatedFilteredInsights["featured"] = featuredInsights;
    setFilteredInsights(updatedFilteredInsights);
    setIsLoading(false);
  }, []);

  const selectFeatured = (filteredInsights) => {
    // {
    //   benchmarkKey,
    //   filterKey,
    //   difference,
    //   accounts
    // };

    let featuredInsights = [];
    Object.keys(filteredInsights).forEach((benchmarkKey) => {
      const insights = filteredInsights[benchmarkKey];
      // exclude insights with low sample size (< 5)
      const aboveSampleSize = insights.filter(
        (insight) => insight.accounts >= 5
      );
      const isNotNaN = aboveSampleSize.filter(
        (insight) => !isNaN(insight.difference)
      );
      featuredInsights = [...featuredInsights, ...isNotNaN];
    });
    // rank by highest absolute difference
    featuredInsights.sort((insight1, insight2) => {
      // Bias towards all_companies(x 1.2)
      let difference1 = insight1.difference;
      if (insight1.benchmarkKey === "all_companies") {
        difference1 *= 1.2;
      }
      let difference2 = insight2.difference;
      if (insight2.benchmarkKey === "all_companies") {
        difference2 *= 1.2;
      }
      return Math.abs(difference1) < Math.abs(difference2) ? 1 : -1;
    });

    // Limit to 5
    return featuredInsights.slice(0, 5);
  };

  const buildInsightString = (insight) => {
    return `${insight.benchmarkKey} ${insight.filterKey} is ${
      insight.difference >= 0 ? "up" : "down"
    } by ${Math.abs(insight.difference)}% (${insight.accounts} accounts)`;
  };

  return (
    <div className="m-4">
      <h3 className="pb-5">
        {providerName[0].toUpperCase()}
        {providerName.slice(1)} Insights!
      </h3>
      <Row>
        <Col md={6}>
          {isLoading ? (
            <div className="mx-auto" style={{ inlineSize: "fit-content" }}>
              <p>
                <span>
                  <FontAwesomeIcon icon={faSpinner} spin />
                </span>{" "}
                Loading....
              </p>
            </div>
          ) : (
            <div className="mx-auto" style={{ inlineSize: "fit-content" }}>
              {/* map each category */}
              {Object.keys(filteredInsights)
                // Sort alphabetically with featured at the top
                .sort((insightKeyA, insightKeyB) => {
                  if (insightKeyA === "featured") {
                    return -1;
                  }
                  if (insightKeyB === "featured") {
                    return 1;
                  }
                  return insightKeyA > insightKeyB ? 1 : -1;
                })
                .map((insightCategory) => {
                  return (
                    <div key={`insight_${insightCategory}`}>
                      <h5 className="mt-3">{insightCategory}</h5>
                      <ul
                        style={{ listStyleType: "none", paddingLeft: "15px" }}
                      >
                        {/* map each insight in the category */}
                        {filteredInsights[insightCategory]
                          .filter((insight) => !isNaN(insight.difference))
                          .map((insight, index) => {
                            const insightStr = buildInsightString(insight);
                            return (
                              <li
                                key={"featured-" + index}
                                style={{ cursor: "pointer" }}
                                onClick={() => {
                                  selectedInsights.includes(insightStr)
                                    ? setSelectedInsights([
                                        ...selectedInsights.filter(
                                          (currentInsight) =>
                                            currentInsight !== insightStr
                                        ),
                                      ])
                                    : setSelectedInsights([
                                        ...selectedInsights,
                                        insightStr,
                                      ]);
                                  setHasBeenCopied(false);
                                }}
                              >
                                <FontAwesomeIcon
                                  icon={
                                    selectedInsights.includes(insightStr)
                                      ? faStar
                                      : faStarO
                                  }
                                />{" "}
                                <span className="pl-1">{insightStr}</span>
                              </li>
                            );
                          })}
                      </ul>
                    </div>
                  );
                })}
            </div>
          )}
        </Col>
        <Col md={6}>
          <div className="d-flex flex-row justify-content-between mb-3">
            <h4>({selectedInsights.length}) Selected</h4>
            <Button
              onClick={() => {
                console.log("text copied!");
                try {
                  console.log("current", editorRef.current.editor.getValue());
                  const currentText = editorRef.current.editor.getValue();
                  copyAreaRef.current.value = currentText;
                  copyAreaRef.current.select();
                  document.execCommand("copy");
                  copyAreaRef.current.value = "";
                  copyAreaRef.current.blur();
                  setHasBeenCopied(true);
                } catch (error) {
                  console.error(error);
                }
              }}
            >
              {hasBeenCopied ? "Text Copied!" : "Click to copy"}
            </Button>
          </div>

          <AceEditor
            ref={editorRef}
            style={{
              height: "300px",
              width: "100%",
            }}
            placeholder="Select insights on the left!"
            mode="text"
            theme="clouds"
            name="selectedInsights"
            fontSize={16}
            showPrintMargin={false}
            showGutter={true}
            highlightActiveLine={true}
            value={
              selectedInsights.length > 0
                ? includeSampleSize
                  ? "– " + selectedInsights.join("\n– ")
                  : "– " +
                    selectedInsights
                      .join("\n– ")
                      .replace(/( \(\d+ accounts\))/gm, "")
                : ""
            }
            wrapEnabled={true}
            setOptions={{
              showLineNumbers: false,
              tabSize: 2,
              readOnly: false,
            }}
          />
          <InputGroup className="mt-3 d-flex justify-content-end">
            <InputGroup.Checkbox
              id="includeSampleSize"
              aria-label="Checkbox for including sample size"
              checked={includeSampleSize}
              onChange={() => setIncludeSampleSize(!includeSampleSize)}
            />
            <label htmlFor="includeSampleSize" className="ml-2">
              Include Sample Size?
            </label>
          </InputGroup>

          <textarea
            style={{
              opacity: ".01",
              height: 0,
              width: 0,
              position: "absolute",
              zIndex: -9999,
            }}
            ref={copyAreaRef}
          ></textarea>
        </Col>
      </Row>
    </div>
  );
};
