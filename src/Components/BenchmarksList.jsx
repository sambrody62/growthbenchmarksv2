import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Container } from "react-bootstrap";
import { useParams } from "react-router-dom";

import { Navigation } from "./Navigation";
import { Footer } from "./Footer";
import { filters } from "./filters";
import myFetch from "./myFetch";

export const BenchmarksList = () => {
  const [benchmarks, setBenchmarks] = useState([]);
  const { providerName } = useParams();

  useEffect(() => {
    myFetch
      .get(`/${providerName}/benchmarks/list`)
      .then((response) => response.json())
      .then((data) => {
        const { benchmarks } = data;
        setBenchmarks(benchmarks);
      });
  }, []);

  return (
    <>
      <Navigation />
      <Container>
        <h1>All Benchmarks</h1>
        {benchmarks.map((benchmark) => {
          const fullBenchmarkName = benchmark.split(".").join("/");
          return Object.keys(filters).map((filter) => {
            return (
              <>
                <Link
                  key={`${filter}_${fullBenchmarkName}`}
                  to={`/${providerName}/${filter}/${fullBenchmarkName}`}
                >
                  {fullBenchmarkName[0].toUpperCase() +
                    fullBenchmarkName.split("/").join(" ").slice(1)}{" "}
                  - {filter}
                </Link>
                <br />
              </>
            );
          });
        })}
      </Container>
      <Footer />
    </>
  );
};
