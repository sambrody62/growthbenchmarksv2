const fs = require("fs");

const fetch = require("node-fetch");

// TODO I don't think these numbers are correct, but the script works...but the server data is just wrong...

console.log("Benchmarks beginning to get cached");

url =
  process.env.NODE_ENV === "production"
    ? "https://api.growthbenchmarks.com/cache_benchmarks"
    : "http://localhost:8000/cache_benchmarks";

console.log("Fetching " + url);

fetch(url)
  .then((response) => {
    return response.text();
  })
  .then((benchmarkData) => {
    console.log("Received " + benchmarkData);
    const jsFileContents =
      "export const cachedBenchmarks = " +
      JSON.stringify(JSON.parse(benchmarkData));
    const fileName = __dirname + "/Components/cachedBenchmarks.js";
    fs.writeFile(fileName, jsFileContents, "utf8", () => {
      console.log("saved file at " + fileName);
    });
  })
  .catch((error) => {
    console.log("Error with fetch: " + error);
  });
