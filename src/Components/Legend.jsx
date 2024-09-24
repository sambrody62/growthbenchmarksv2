import React, { useRef, useState, useEffect } from "react";

const legendWidth = 250;

export const Legend = (props) => {
  const {
    name,
    amount,
    doesHideYou,
    color,
    originalAmount,
    isLowGood,
    ySuffix,
    langCountry,
    currency,
    index = 0,
    selectedTypeFilter,
  } = props;

  const textRef = useRef(null);
  const baseCompareRef = useRef();
  const baseLabelRef = useRef();
  const nameRef = useRef();

  const [youOffset, setYouOffset] = useState(
    textRef.current && textRef.current.getBoundingClientRect().width + 25 + 15
  );

  useEffect(() => {
    setYouOffset(
      textRef.current && textRef.current.getBoundingClientRect().width + 25 + 15
    );
  });

  return (
    <g
      transform={`translate(${index * legendWidth},0)`}
      key={`legend_${index}_${name}_${amount}_${originalAmount}`}
    >
      <text className={`percentageChange`} dy="60" dx="25" ref={textRef}>
        {selectedTypeFilter === "%" && `${amount > 0 ? "+" : ""}${amount}%`}
        {selectedTypeFilter === "currency" &&
          (ySuffix
            ? `${amount && parseFloat(amount).toFixed(2)}${ySuffix}`
            : isNaN(amount)
            ? "--"
            : Intl.NumberFormat(langCountry, {
                style: "currency",
                currency,
              }).format(amount))}
      </text>
      <rect fill={color} width={11} height={11} y="75" x="25"></rect>
      <foreignObject
        ref={nameRef}
        className={`legend`}
        y="72"
        x="40"
        width={legendWidth - 40}
        height={"3em"}
      >
        <div style={{ textAlign: "left" }}>{name}</div>
      </foreignObject>
      {!doesHideYou && index > 0 && (
        <g
          key={`youOffset_${name}`}
          transform={`translate(${youOffset || 0},0)`}
        >
          <rect
            className={
              (isLowGood && amount > originalAmount) ||
              (!isLowGood && amount < originalAmount)
                ? "successFill"
                : (isLowGood && amount < originalAmount) ||
                  (!isLowGood && amount > originalAmount)
                ? "failureFill"
                : "nothingFill"
            }
            width={
              baseCompareRef.current &&
              baseLabelRef.current &&
              baseCompareRef.current.getBoundingClientRect().width +
                baseLabelRef.current.getBoundingClientRect().width +
                20
            }
            height="25"
            y="37"
            x={-10}
          ></rect>

          <text ref={baseLabelRef} className={`legend`} y="55">
            Base:
          </text>
          <text
            ref={baseCompareRef}
            y="55"
            dx="42"
            className={
              (isLowGood && amount > originalAmount) ||
              (!isLowGood && amount < originalAmount)
                ? "success"
                : (isLowGood && amount < originalAmount) ||
                  (!isLowGood && amount > originalAmount)
                ? "failure"
                : ""
            }
          >
            {amount - originalAmount > 0 && "+"}
            {selectedTypeFilter === "%" && `${amount - originalAmount}%`}
            {selectedTypeFilter === "currency" &&
              (ySuffix
                ? `${(amount - originalAmount).toFixed(2)}%`
                : isNaN(originalAmount)
                ? "--"
                : Intl.NumberFormat(langCountry, {
                    style: "currency",
                    currency,
                  }).format(amount - originalAmount))}
            {amount - originalAmount > 0
              ? "↑"
              : amount - originalAmount < 0
              ? "↓"
              : isNaN(amount) || isNaN(originalAmount)
              ? ""
              : "="}
          </text>
        </g>
      )}
    </g>
  );
};
