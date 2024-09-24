import React from "react";

import { Legend } from "./Legend";

export const FullLegend = (props) => {
  const {
    selectedCharts,
    isLowGood,
    ySuffix,
    langCountry,
    currency,
    average,
    secondPercentageChange,
    secondAverage,
    percentageChange,
    thirdPercentageChange,
    thirdAverage,
    selectedTypeFilter,
    mainLineColour,
    secondLineColour,
    thirdLineColour,
  } = props;

  const colours = [mainLineColour, secondLineColour, thirdLineColour];
  const data = [
    { percentageChange, average },
    { percentageChange: secondPercentageChange, average: secondAverage },
    { percentageChange: thirdPercentageChange, average: thirdAverage },
  ];

  return (
    <g>
      {selectedCharts.map((chart, index) => {
        return (
          <Legend
            key={`${index}_legend_${chart.label}`}
            name={`${chart.label}${index === 0 ? " (base)" : ""}`}
            amount={
              selectedTypeFilter === "%"
                ? data[index].percentageChange
                : data[index].average
            }
            color={colours[index]}
            originalAmount={
              selectedTypeFilter === "%"
                ? data[0].percentageChange
                : data[0].average
            }
            index={index}
            isLowGood={isLowGood}
            ySuffix={ySuffix}
            langCountry={langCountry}
            currency={currency}
            selectedTypeFilter={selectedTypeFilter}
          />
        );
      })}
    </g>
  );
};
