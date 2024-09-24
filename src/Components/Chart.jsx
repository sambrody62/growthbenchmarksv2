import React, { useState, useEffect, useRef, useMemo } from "react";
import { Col, Row, Form } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner } from "@fortawesome/fontawesome-free-solid";
import Select from "react-select";
import * as d3 from "d3";
import moment from "moment";
import Switch from "react-switch";

import {
  firstLineColour,
  secondLineColour,
  thirdLineColour,
  chartSettings,
  smallChartSettings,
  langCountry,
} from "../config";

import {
  getBenchmarkFriendlyName,
  getConversionEventFriendlyName,
} from "./helpers";
import { blendOutliers } from "./blendOutliers";
import { rollingOutliers } from "./rollingOutliers";
import { Tooltip } from "./Tooltip";
import { ExpandIcon } from "./ExpandIcon";
import { FullLegend } from "./FullLegend";

function debounce(fn, ms) {
  let timer;
  return () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      timer = null;
      fn.apply(this, arguments);
    }, ms);
  };
}

const bisectInternal = d3.bisector((d) => d.date).left;

const axisColour = "#BFBFBF";
const lineThickness = 1.5;
const tickSpacing = 150;

const chartTimeFilters = ["1W", "2W", "1M", "1Q", "MAX"];

export const Chart = (props) => {
  const {
    title,
    metric,
    companyName,
    allData = [],
    isBenchmarkOnly = false,
    canChooseCharts = true,
    doesHideYou = false,
    dates,
    ySuffix,
    isSmall,
    isLoadingData,
    currency = "USD",
    isLowGood = false,
    hasConversionEvent = false,
    selectedConversionEvent = "link_click",
    conversionEvents,
    handleSelectConversionEvent = () => {},
    allBenchmarks = [],
    selectedCharts = [],
    handleSelectCharts = () => {},
    averages = [],
    setStartDate,
  } = props;

  const [isShowingOutliers, setIsShowingOutliers] = useState(false);

  const firstData =
    allData.length >= 1
      ? blendOutliers(allData[0], selectedCharts[0].isBenchmark)
      : [];

  const secondData =
    allData.length >= 2
      ? blendOutliers(allData[1], selectedCharts[1].isBenchmark)
      : [];
  const thirdData =
    allData.length >= 3
      ? blendOutliers(allData[2], selectedCharts[2].isBenchmark)
      : [];

  const { outliersData, lowerData, upperData } =
    allData.length >= 1
      ? rollingOutliers(firstData)
      : { outliersData: [], lowerData: [], upperData: [] };

  const [isHover, setHover] = useState(false);
  const [selectedTypeFilter, setSelectedTypeFilter] = useState("currency");
  const [selectedTimeFilter, setSelectedTimeFilter] = useState("1Q");
  const [dimensions, setDimensions] = useState(
    isSmall ? smallChartSettings : chartSettings
  );

  const [tooltipX, setTooltipX] = useState(-1);
  const [tooltip, setTooltip] = useState({});

  const firstPathRef = useRef();
  const secondPathRef = useRef();
  const thirdPathRef = useRef();
  const outlierBackgroundPathRef = useRef();

  useEffect(() => {
    const debouncedHandleResize = debounce(function handleResize() {
      setDimensions({
        ...dimensions,
        height:
          window.innerHeight > dimensions.maxHeight
            ? dimensions.maxHeight
            : window.innerHeight,
        width:
          window.innerWidth > dimensions.maxWidth
            ? dimensions.maxWidth
            : window.innerWidth,
      });
    }, 10);

    window.addEventListener("resize", debouncedHandleResize);
    debouncedHandleResize();
    return () => {
      window.removeEventListener("resize", debouncedHandleResize);
    };
  }, []);

  const startDate = useMemo(() => {
    let newStartDate;
    if (selectedTimeFilter !== "MAX") {
      let timeAmount = "days";
      if (selectedTimeFilter.indexOf("W") > -1) {
        timeAmount = "weeks";
      } else if (selectedTimeFilter.indexOf("M") > -1) {
        timeAmount = "months";
      } else if (selectedTimeFilter.indexOf("Q") > -1) {
        timeAmount = "quarters";
      } else if (selectedTimeFilter.indexOf("Y") > -1) {
        timeAmount = "years";
      }
      const dateToReturn = moment()
        .subtract(parseInt(selectedTimeFilter), timeAmount)
        .set({
          hour: 0,
          minute: 0,
          second: 0,
          millisecond: 0,
        });
      newStartDate = dateToReturn;
    } else if (dates && dates.length > 0) {
      newStartDate = moment(dates[0], "YYYY-MM-DD").set({
        hour: 0,
        minute: 0,
        second: 0,
        millisecond: 0,
      });
    } else {
      newStartDate = moment().set({
        hour: 0,
        minute: 0,
        second: 0,
        millisecond: 0,
      });
    }
    return newStartDate;
  }, [dates, selectedTimeFilter]);

  useEffect(() => {
    setStartDate && setStartDate(startDate);
  }, [startDate]);

  const endDate = moment()
    .subtract(1, "days")
    .set({ hour: 0, minute: 0, second: 0, millisecond: 0 });

  const xScale = useMemo(() => {
    return d3
      .scaleTime()
      .domain([startDate, endDate])
      .range([
        0,
        dimensions.width -
          dimensions.paddingRight -
          dimensions.paddingLeft -
          dimensions.margin * 2,
      ]);
  }, [dimensions, startDate, endDate]);

  function getStartValue(data) {
    if (data && data.length > 0) {
      const dataValue = data.find((datum) => {
        return moment(datum.date).isSameOrAfter(startDate);
      });
      return dataValue !== undefined ? dataValue.value : 0;
    }
  }

  function getEndValue(data) {
    return data && data.length > 0 && data[data.length - 1].value;
  }

  function getPercentageChange(start, end) {
    return parseFloat(((100 * (end - start)) / start).toFixed(0));
  }

  const firstDataStartValue = useMemo(() => {
    return getStartValue(firstData);
  });
  const endValue = useMemo(() => {
    return getEndValue(firstData);
  });
  const percentageChange = useMemo(() => {
    return getPercentageChange(firstDataStartValue, endValue);
  });
  const average = useMemo(() => {
    return averages[0];
  }, [averages]);

  const secondDataStartValue = useMemo(() => {
    return getStartValue(secondData);
  });
  const secondDataEndValue = useMemo(() => {
    return getEndValue(secondData);
  });
  const secondDataPercentageChange = useMemo(() => {
    return getPercentageChange(secondDataStartValue, secondDataEndValue);
  });
  const secondDataAverage = useMemo(() => {
    return averages[1];
  }, [averages]);
  const thirdDataStartValue = useMemo(() => {
    return getStartValue(thirdData);
  });
  const thirdDataEndValue = useMemo(() => {
    return getEndValue(thirdData);
  });
  const thirdDataPercentageChange = useMemo(() => {
    return getPercentageChange(thirdDataStartValue, thirdDataEndValue);
  });
  const thirdDataAverage = useMemo(() => {
    return averages[2];
  }, [averages]);

  const yScale = useMemo(() => {
    if (selectedTypeFilter === "%") {
      const allData = (firstData || [])
        .filter((datum) => {
          return moment(datum.date).isSameOrAfter(startDate);
        })
        .map((d) => {
          return getPercentageChange(firstDataStartValue, d.value);
        })
        .concat(
          (secondData || [])
            .filter((datum) => {
              return moment(datum.date).isSameOrAfter(startDate);
            })
            .map((d) => {
              return getPercentageChange(secondDataStartValue, d.value);
            })
        )
        .concat(
          (thirdData || [])
            .filter((datum) => {
              return moment(datum.date).isSameOrAfter(startDate);
            })
            .map((d) => {
              return getPercentageChange(thirdDataStartValue, d.value);
            })
        )
        .concat(
          (lowerData || [])
            .filter((datum) => {
              return moment(datum.date).isSameOrAfter(startDate);
            })
            .map((d) => {
              return getPercentageChange(firstDataStartValue, d.value);
            })
        )
        .concat(
          (upperData || [])
            .filter((datum) => {
              return moment(datum.date).isSameOrAfter(startDate);
            })
            .map((d) => {
              return getPercentageChange(firstDataStartValue, d.value);
            })
        );
      return d3
        .scaleLinear()
        .domain([d3.min(allData), d3.max(allData)])
        .range([
          dimensions.height -
            dimensions.paddingTop -
            dimensions.paddingBottom -
            dimensions.margin * 2,
          0,
        ]);
    }

    const allData = (firstData || [])
      .concat(secondData || [])
      .concat(thirdData || [])
      .concat(lowerData || [])
      .concat(upperData || [])
      .filter((datum) => {
        return moment(datum.date).isSameOrAfter(startDate);
      });
    return d3
      .scaleLinear()
      .domain([
        d3.min(allData.map((d) => d.value)),
        d3.max(allData.map((d) => d.value)),
      ])
      .range([
        dimensions.height -
          dimensions.paddingTop -
          dimensions.paddingBottom -
          dimensions.margin * 2,
        0,
      ]);
  }, [
    dimensions,
    firstData,
    secondData,
    thirdData,
    lowerData,
    upperData,
    selectedTypeFilter,
    selectedTimeFilter,
  ]);

  const lineData = (d, dataStartValue) => {
    return d3
      .line()
      .x((d) => (d && d.date ? xScale(d.date) : false))
      .y((d) => {
        return d && d.value !== undefined
          ? yScale(
              selectedTypeFilter === "%"
                ? getPercentageChange(dataStartValue, d.value)
                : d.value
            )
          : false;
      })(d);
  };

  useEffect(() => {
    d3.select(firstPathRef.current)
      .datum(firstData)
      .attr("d", (d) => lineData(d, firstDataStartValue));

    d3.select(secondPathRef.current)
      .datum(secondData)
      .attr("d", (d) => lineData(d, secondDataStartValue));

    d3.select(thirdPathRef.current)
      .datum(thirdData)
      .attr("d", (d) => lineData(d, thirdDataStartValue));

    d3.select(outlierBackgroundPathRef.current)
      .datum(lowerData.concat(upperData.slice().reverse()))
      .attr("d", (d) => lineData(d, firstDataStartValue));
  });

  function bisect(mx, bisectData) {
    if (!bisectData || bisectData.length === 0) {
      return 0;
    }
    const date = xScale.invert(mx);
    const index = bisectInternal(bisectData, date, 1);
    const a = Object.assign({}, bisectData[index - 1]);
    const b = Object.assign({}, bisectData[index]);
    return b && date - a.date > b.date - date ? b : a;
  }

  function createTooltip(event) {
    const pointerPosition = d3.pointer(event, this)[0];
    setTooltipX(pointerPosition);
    let { date: firstDate, value: firstValue } = bisect(
      d3.pointer(event, this)[0],
      firstData
    );
    let { date: secondDate, value: secondValue } = bisect(
      pointerPosition,
      secondData
    );
    let { date: thirdDate, value: thirdValue } = bisect(
      pointerPosition,
      thirdData
    );
    let { value: lowerValue } = bisect(pointerPosition, lowerData);
    let { value: upperValue } = bisect(pointerPosition, upperData);

    firstValue =
      selectedTypeFilter === "%"
        ? getPercentageChange(firstDataStartValue, firstValue)
        : firstValue && firstValue.toFixed(2);
    secondValue =
      selectedTypeFilter === "%"
        ? getPercentageChange(secondDataStartValue, secondValue)
        : secondValue && secondValue.toFixed(2);
    thirdValue =
      selectedTypeFilter === "%"
        ? getPercentageChange(thirdDataStartValue, thirdValue)
        : thirdValue && thirdValue.toFixed(2);
    lowerValue =
      selectedTypeFilter === "%"
        ? getPercentageChange(firstDataStartValue, lowerValue)
        : lowerValue && lowerValue.toFixed(2);
    upperValue =
      selectedTypeFilter === "%"
        ? getPercentageChange(firstDataStartValue, upperValue)
        : upperValue && upperValue.toFixed(2);

    const isOutlier =
      parseFloat(firstValue) >= parseFloat(upperValue) ||
      parseFloat(firstValue) <= parseFloat(lowerValue);

    setTooltip({
      firstDate,
      firstValue,
      secondDate,
      secondValue,
      thirdDate,
      thirdValue,
      isOutlier,
      lowerValue,
      upperValue,
    });
  }

  const benchmarkOptions = (isBenchmarkOnly
    ? []
    : doesHideYou
    ? [
        {
          value: "similar_companies",
          label: "Similar Companies",
          isDisabled: selectedCharts.length >= 3,
        },
      ]
    : [
        {
          value: "you",
          label: companyName,
          isDisabled: selectedCharts.length >= 3,
        },
        {
          value: "similar_companies",
          label: "Similar Companies",
          isDisabled: selectedCharts.length >= 3,
        },
      ]
  ).concat(
    allBenchmarks.map((benchmark) => {
      return {
        value: benchmark,
        label: getBenchmarkFriendlyName(benchmark),
        isBenchmark: true,
        isDisabled: selectedCharts.length >= 3,
      };
    })
  );

  const selectedConversionEventData = conversionEvents?.find(
    (conversionEvent) => conversionEvent[0] === selectedConversionEvent
  );
  const selectedConversionEventName = getConversionEventFriendlyName(
    selectedConversionEventData
  );

  return (
    <div className={isSmall ? "cursor" : ""}>
      {!isSmall && (
        <div className="mb-3 text-left d-flex">
          <Row className="mr-3 ml-3" style={{ width: "100%" }}>
            <Col md={5} xs={12}>
              <h6 className="title">{title}</h6>
              <h3>{metric}</h3>
            </Col>
            <Col md={7} xs={12}>
              <Row className="mt-auto mb-auto">
                {canChooseCharts && (
                  <>
                    <Col
                      md={2}
                      xs={12}
                      className="text-right mt-auto mb-auto text-left-xs"
                    >
                      <Form.Label>Compare</Form.Label>
                    </Col>
                    <Col md={10}>
                      <Select
                        key={selectedCharts
                          .map((chart) => {
                            return chart.label;
                          })
                          .join(",")}
                        isMulti
                        isSearchable={true}
                        value={selectedCharts}
                        onChange={(charts) => {
                          handleSelectCharts(charts);
                        }}
                        options={benchmarkOptions}
                      />
                    </Col>
                  </>
                )}

                {hasConversionEvent && conversionEvents.length > 0 && (
                  <>
                    <Col md={6} xs={12} className="text-right mt-auto mb-auto">
                      <Form.Label>Conversion Event</Form.Label>
                    </Col>
                    <Col md={6}>
                      <Select
                        isMulti={false}
                        value={
                          {
                            value: selectedConversionEvent,
                            label: selectedConversionEventName,
                          } || {}
                        }
                        onChange={(newConversionEvent) => {
                          handleSelectConversionEvent(newConversionEvent.value);
                        }}
                        options={conversionEvents.map(
                          ([conversionEvent, conversionEventName]) => {
                            return {
                              value: conversionEvent,
                              label: getConversionEventFriendlyName([
                                conversionEvent,
                                conversionEventName,
                              ]),
                            };
                          }
                        )}
                      />
                    </Col>
                  </>
                )}
              </Row>
            </Col>
          </Row>
        </div>
      )}
      <div
        className={`mt-3 ${isSmall ? "mx-2" : "m-auto"} chart`}
        style={{
          width: dimensions.width - dimensions.margin * 2,
          height: dimensions.height - dimensions.margin * 2,
          position: "relative",
        }}
        onClick={() => {
          props.onClick && props.onClick();
        }}
      >
        {isLoadingData && <FontAwesomeIcon icon={faSpinner} spin />}

        <svg
          className={
            (isSmall ? "small-chart" : "") +
            (isSmall && isHover ? " small-chart-hover" : "")
          }
          width="100%"
          height="100%"
          onMouseEnter={() => setHover(true)}
          onMouseLeave={() => setHover(false)}
        >
          <g
            transform={`translate(${dimensions.paddingLeft},
            ${dimensions.paddingTop})`}
            onMouseEnter={(event) => {
              createTooltip(event);
            }}
            onMouseMove={(event) => {
              createTooltip(event);
            }}
            onMouseLeave={() => {
              setTooltipX(-1);
            }}
            width={
              dimensions.width -
              dimensions.paddingLeft -
              dimensions.paddingRight
            }
            height={
              dimensions.height -
              dimensions.paddingTop -
              dimensions.paddingBottom
            }
          >
            <rect
              fill="#FFF"
              width={
                dimensions.width -
                dimensions.paddingLeft -
                dimensions.paddingRight
              }
              height={
                dimensions.height -
                dimensions.paddingTop -
                dimensions.paddingBottom
              }
            ></rect>
            {isShowingOutliers && !isSmall && outlierBackgroundPathRef && (
              <path
                className={`graphLine`}
                stroke={"#B395F4"}
                strokeWidth={lineThickness}
                fill="#F2EDFD"
                ref={outlierBackgroundPathRef}
              />
            )}
            {thirdPathRef && (
              <path
                className={`graphLine`}
                stroke={
                  !isLoadingData && !isSmall ? thirdLineColour : "#BFBFBF"
                }
                strokeWidth={lineThickness}
                fill="none"
                ref={thirdPathRef}
              />
            )}
            {secondPathRef && (
              <path
                className={`graphLine`}
                stroke={
                  !isLoadingData && !isSmall ? secondLineColour : "#BFBFBF"
                }
                strokeWidth={lineThickness}
                fill="none"
                ref={secondPathRef}
              />
            )}

            {isShowingOutliers &&
              !isSmall &&
              outliersData.map((outlierDatum, outlierIndex) => {
                return (
                  <circle
                    key={`circle_${outlierIndex}`}
                    cx={xScale(outlierDatum.date)}
                    cy={yScale(
                      selectedTypeFilter === "%"
                        ? getPercentageChange(
                            firstDataStartValue,
                            outlierDatum.value
                          )
                        : outlierDatum.value
                    )}
                    r={5}
                    stroke={"#ff556a"}
                    fill={"#ffaab5"}
                  />
                );
              })}

            {firstPathRef && (
              <path
                className={`graphLine`}
                stroke={!isLoadingData && !isSmall ? firstLineColour : "#000"}
                strokeWidth={lineThickness}
                fill="none"
                ref={firstPathRef}
              />
            )}

            <rect
              transform={`translate(-${
                dimensions.paddingLeft
              },${-dimensions.paddingTop})`}
              className="y-axis-cover"
              width={dimensions.paddingLeft}
              height={dimensions.height}
            ></rect>
            <rect
              transform={`translate(${
                dimensions.width -
                dimensions.paddingLeft -
                dimensions.paddingRight
              },${-dimensions.paddingTop})`}
              className="y-axis-cover-right"
              width={dimensions.paddingRight}
              height={dimensions.height}
            ></rect>
            <Axis
              width={dimensions.width}
              xScale={xScale}
              yScale={yScale}
              ySuffix={ySuffix}
              currency={currency}
              selectedTypeFilter={selectedTypeFilter}
            />
            {!isSmall &&
              ((firstData && firstData.length > 0) ||
                (thirdData && thirdData.length > 0)) &&
              tooltipX > -1 && (
                <>
                  <line
                    x1={tooltipX}
                    x2={tooltipX}
                    y0={0}
                    y1={
                      dimensions.height -
                      dimensions.paddingTop -
                      dimensions.paddingBottom
                    }
                    stroke={axisColour}
                  />

                  <Tooltip
                    tooltip={tooltip}
                    xScale={xScale}
                    yScale={yScale}
                    selectedTypeFilter={selectedTypeFilter}
                    ySuffix={ySuffix}
                    currency={currency}
                    selectedCharts={selectedCharts}
                    isShowingOutliers={isShowingOutliers}
                  />
                </>
              )}
          </g>
          {isLoadingData ? (
            <text
              x={dimensions.width / 2}
              y={dimensions.height / 2}
              style={{ textAnchor: "middle" }}
            >
              Loading...
            </text>
          ) : (
            false
          )}

          {!isLoadingData &&
            firstData &&
            firstData.length === 0 &&
            secondData &&
            secondData.length === 0 &&
            thirdData &&
            thirdData.length === 0 && (
              <text
                x={dimensions.width / 2}
                y={dimensions.height / 2}
                style={{ textAnchor: "middle" }}
              >
                No Data
              </text>
            )}

          {isSmall && (
            <g
              transform={`translate(${dimensions.textMarginLeft},${dimensions.textMarginTop})`}
            >
              <text
                className="subtitle"
                style={{ fontSize: dimensions.fontSize }}
              >
                {metric}
              </text>
            </g>
          )}

          {isSmall && (
            <g
              transform={
                `translate(${dimensions.width - 50}, 5)` +
                (isHover ? " scale(1.5) translate(-5,0)" : "")
              }
              width={20}
              height={20}
              className="fa-expand"
            >
              <ExpandIcon />
            </g>
          )}

          {!isSmall && (
            <FullLegend
              doesHideYou={doesHideYou}
              percentageChange={percentageChange}
              selectedTypeFilter={selectedTypeFilter}
              selectedCharts={selectedCharts}
              isLowGood={isLowGood}
              ySuffix={ySuffix}
              langCountry={langCountry}
              currency={currency}
              average={average}
              secondPercentageChange={secondDataPercentageChange}
              secondAverage={secondDataAverage}
              thirdPercentageChange={thirdDataPercentageChange}
              thirdAverage={thirdDataAverage}
              mainLineColour={firstLineColour}
              secondLineColour={secondLineColour}
              thirdLineColour={thirdLineColour}
            />
          )}
        </svg>

        {isSmall && (
          <div
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
            style={{
              textAlign: "center",
              position: "absolute",
              width: dimensions.width - dimensions.margin * 2,
              padding: 10,
              fontSize: 26,
              top: dimensions.height / 2 - 26,
              backgroundColor: "white",
              zIndex: 1,
              opacity: isHover ? 1 : 0,
              transition: "opacity 1s",
            }}
          >
            Click to View
          </div>
        )}
      </div>
      {!isSmall && (
        <div className="d-flex mt-3 mb-3">
          <div className="text-left mr-auto">
            {chartTimeFilters.map((timeFilter, index) => {
              return (
                <span
                  key={index}
                  className={`timeFilter ${
                    timeFilter === selectedTimeFilter ? "selected" : ""
                  }`}
                  onClick={() => {
                    setSelectedTimeFilter(timeFilter);
                  }}
                >
                  {timeFilter}
                </span>
              );
            })}
          </div>

          <div className="text-right ml-auto d-flex">
            <span className="mr-4">
              <label className="d-flex align-items-center">
                <Switch
                  onChange={() => {
                    setIsShowingOutliers(!isShowingOutliers);
                  }}
                  checked={isShowingOutliers}
                  uncheckedIcon={false}
                  checkedIcon={false}
                  onColor={firstLineColour}
                  handleDiameter={18}
                  height={20}
                  width={40}
                />
                <span className="ml-2">Outliers</span>
              </label>
            </span>
            <span
              className={`absoluteRelativeFilter ${
                selectedTypeFilter === "currency" && `selected`
              }`}
              onClick={() => setSelectedTypeFilter("currency")}
            >
              Value
            </span>

            <span
              className={`absoluteRelativeFilter ${
                selectedTypeFilter === "%" && `selected`
              }`}
              onClick={() => setSelectedTypeFilter("%")}
            >
              Index
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

const Axis = (props) => {
  const {
    xScale,
    yScale,
    width,
    ySuffix,
    currency,
    selectedTypeFilter,
  } = props;
  const xTicks = useMemo(() => {
    return xScale.ticks(width / tickSpacing).map((value) => ({
      value,
      xOffset: xScale(value),
    }));
  }, [props]);
  const yTicks = useMemo(() => {
    return yScale.ticks().map((value) => ({
      value,
      yOffset: yScale(value),
    }));
  }, [props]);

  return (
    <g className="axis">
      {yScale && (
        <path
          d={`M 0 ${yScale.range()[0]} V 0`}
          stroke={axisColour}
          strokeDasharray="1,5"
        />
      )}

      {xScale && (
        <path
          d={`M 0 0 H ${xScale.range()[1]}`}
          stroke={axisColour}
          transform={`translate(${0},${yScale && yScale.range()[0]})`}
          strokeDasharray="1,5"
        />
      )}

      {xTicks.map(({ value, xOffset }) => (
        <g
          key={value}
          transform={`translate(${xOffset || 0}, ${
            yScale && yScale.range()[0]
          })`}
        >
          <line
            y2={-yScale.range()[0]}
            stroke={axisColour}
            strokeDasharray="1,5"
          />
          <text
            key={value}
            style={{
              fontSize: "14px",
              textAnchor: "middle",
            }}
            transform={"translate(0,25)"}
          >
            {moment(value).format("DD/MM")}
          </text>
        </g>
      ))}

      {yTicks.map(({ value, yOffset }, index) => {
        let displayValue = ySuffix
          ? `${parseFloat(value).toFixed(2)}${ySuffix}`
          : Intl.NumberFormat(langCountry, {
              style: "currency",
              currency,
            }).format(value);
        if (selectedTypeFilter && selectedTypeFilter === "%") {
          displayValue = value.toFixed(0) + "%";
        }
        return (
          <g
            key={`${value}_${index}`}
            transform={`translate(0, ${yScale.range()[1] + yOffset})`}
          >
            <line
              x2={xScale.range()[1]}
              stroke={axisColour}
              strokeDasharray="1,5"
            />
            <text
              key={value}
              style={{
                fontSize: "14px",
                textAnchor: "middle",
              }}
              transform={"translate(-35,3)"}
            >
              {displayValue}
            </text>
          </g>
        );
      })}
    </g>
  );
};
