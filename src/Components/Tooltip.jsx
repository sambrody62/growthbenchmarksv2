import React from "react";
import moment from "moment";

import {
  firstLineColour,
  secondLineColour,
  thirdLineColour,
  chartSettings as dimensions,
  langCountry,
} from "../config";

export const Tooltip = (props) => {
  const {
    tooltip,
    xScale,
    yScale,
    selectedTypeFilter,
    ySuffix,
    currency,
    isShowingOutliers,
  } = props;
  const {
    firstDate,
    firstValue,
    secondDate,
    secondValue,
    thirdValue,
    thirdDate,
    isOutlier,
    upperValue,
    lowerValue,
  } = tooltip;

  const tooltipsList = [];
  const upperAndLowerValueFill = "#B395F4";
  const firstLineTooltipColour =
    isShowingOutliers && isOutlier ? "#ff556a" : firstLineColour;

  if (isShowingOutliers) {
    // push upper value
    const upperTooltip = createTooltipText(
      upperValue,
      firstDate,
      upperAndLowerValueFill,
      "⤒"
    );
    tooltipsList.push(upperTooltip);
  }

  // push first value
  tooltipsList.push(createTooltipText(firstValue, firstDate));

  if (isShowingOutliers) {
    // push lower value
    const lowerTooltip = createTooltipText(
      lowerValue,
      firstDate,
      upperAndLowerValueFill,
      "⤓"
    );

    tooltipsList.push(lowerTooltip);
  }

  // push other values
  tooltipsList.push(
    createTooltipText(secondValue, secondDate, secondLineColour)
  );
  tooltipsList.push(createTooltipText(thirdValue, thirdDate, thirdLineColour));

  function createTooltipText(
    value,
    date,
    colour = firstLineTooltipColour,
    prefixTextOverride = false
  ) {
    const valueFixed = parseFloat(value).toFixed(2);

    const tooltipText = `${
      prefixTextOverride || moment(date).format("DD/MM")
    } ${
      selectedTypeFilter === "%"
        ? `${valueFixed}%`
        : ySuffix
        ? `${valueFixed}${ySuffix}`
        : Intl.NumberFormat(langCountry, {
            style: "currency",
            currency,
          }).format(valueFixed)
    }`;

    const tooltipWidth = tooltipText.length;

    const xValueToPositionTooltipAt = firstDate || secondDate || thirdDate;
    const xTransform = Math.min(
      xScale(xValueToPositionTooltipAt) + 10,
      dimensions.width -
        dimensions.paddingLeft -
        dimensions.paddingRight -
        tooltipWidth * 6
    );
    const yValueToPositionTooltipAt = firstValue || secondValue || thirdValue;
    const yTransform = Math.min(
      yScale(yValueToPositionTooltipAt),
      dimensions.height -
        dimensions.paddingTop -
        dimensions.paddingBottom -
        3 * 20
    );
    if (isNaN(xTransform) || isNaN(yTransform) || isNaN(value)) {
      return null;
    }
    return (
      <g key={tooltipsList.length}>
        <rect
          width={tooltipWidth + 3 + "ch"}
          height="2.5em"
          y={`${-1.5 + 2.5 * tooltipsList.length}em`}
          fill={colour}
          transform={`translate(${xTransform},${yTransform})`}
        ></rect>
        <text
          transform={`translate(${xTransform},${yTransform})`}
          dx="1em"
          dy={`${0.2 + 2.5 * tooltipsList.length}em`}
          fill="white"
        >
          {tooltipText}
        </text>
      </g>
    );
  }

  return <>{tooltipsList}</>;
};
