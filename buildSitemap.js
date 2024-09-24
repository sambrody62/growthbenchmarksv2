import fs from "fs";

import fetch from "node-fetch";

import { filters } from "./src/Components/filters";

const buildPath = "./public/sitemap.xml";

const PUBLIC_URL = "https://growthbenchmarks.com"; // I am pulling my baseUrl from env - you can generate it however you want

let routes = ["/", "/about", "/benchmarks"];

async function generateSitemap() {
  async function getAllBenchmarks() {
    console.log("Trying to get all benchmarks for sitemap");
    const allBenchmarks = await fetch(
      "http://localhost:8000/facebook/benchmarks/list"
    )
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        return data.benchmarks;
      })
      .catch((error) => {
        console.error("Could not load benchmarks!");
        console.error(error);
        return [];
      });

    return await allBenchmarks;
  }

  const allBenchmarks = await getAllBenchmarks();

  Object.keys(filters).forEach((filter) => {
    routes.push(`/facebook/${filter}/all_companies`);
    const allBenchmarkRoutes = allBenchmarks.map((benchmark) => {
      return `/facebook/${filter}/${benchmark.split(".").join("/")}`;
    });
    routes = routes.concat(allBenchmarkRoutes);
  });

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${routes.reduce(
  (acc, route) => `${acc}
  <url>
    <loc>${PUBLIC_URL}${route}</loc>
  </url>`,
  ""
)}
</urlset>
`;

  fs.writeFileSync(buildPath, xml);
}

generateSitemap();
