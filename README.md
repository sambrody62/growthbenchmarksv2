# GrowthBenchmarks.com

# Get Started

First install with `npm install`

To run the client: `npm start`

To run the server: `npm run server`

To deploy the client: `npm run deploy`

To deploy the server (on linux/mac): `cd api` and then `./deploy.sh`

---

# Server

This runs off Flask inside the api directory and is served at api.growthbenchmarks.com

## Database

Firebase is used to manage all of the data.

Data is stored into a few main collections:

- Users: these have a token, list of account, some meta data like email and the way they logged in (fb, google, email)
- Accounts: the id of which is always `{provider_id}-{account_id}` (e.g. Provider: fb, fbfake, google, googlefake). This contains the questionnaire information as well as a subcollection of metrics (stored daily) and a list of anomalies (also calculated daily)
- Benchmarks: In a similar structure to the metrics inside an account, we store all data within each benchmark daily as a summation of all the accounts that match the benchmark
- Rankings: This is created monthly and holds the cpm, cpc and ctr results and position for each month

Deprecated:

- metrics
- companies
- benchmarks // (lowercase)

Please note, there is a cost associated with reads from the firebase database, and so processing so much data regularly causes a reasonable spike in cost.

We also run a daily backup task for the database which is stored in a Google Cloud S3 bucket (this is slowly growing and should perhaps be automatically cycled at some point!).

## Daily tasks

We have a few scripts that are run daily using Google Cloud Scheduler (most importantly pulling in the data for each account).

At the time of writing here is a brief summary:

| Name                | Time    | Script                                                   |
| ------------------- | ------- | -------------------------------------------------------- |
| Fetch Metrics       | Daily   | load_metrics, load_google_metrics                        |
| Generate Benchmarks | Daily   | generate_facebook_benchmarks, generate_google_benchmarks |
| Generate Anomalies  | Daily   | generate_facebook_anomalies, generate_google_anomalies   |
| Send Anomalies      | Daily   | send_anomalies                                           |
| Generate Rankings   | Monthly | generate_facebook_rankings, generate_google_rankings     |
| Send Rankings       | Monthly | send_rankings                                            |
| Generate Commentary | Monthly | generate_facebook_commentary, generate_google_commentary |

---

# Client

The client is served in the src directory. It is based off [Create React App](https://github.com/facebook/create-react-app) and most of the standard tools associated with that.

The main entry point is App.jsx which is where we route (using react-router) all of the incoming links.

Main.jsx is the standard main page link.

A few pages of interest (`facebook` can be replaced with `google`):

- /facebook/cpc/all_companies (structure for all benchmarks)
- /facebook/benchmarks (a list of all the benchmarks)
- /facebook/insights (a list of all of last month's insights about each benchmark - e.g. fb-industry.apparel Cost per Acquisition (CPA) is up by 473%)

To allow Google login, you must use a http connection and so start with `npm run start-google` otherwise use `npm start` and you must add #beta to the URL.

We use authentication through Google Firebase Authentication which allows email, Facebook and Google logins (at the time of writing).

We also have a couple of scripts to cache benchmarks so they are stored into the code (`npm run cache`) and a way to create a sitemap of all the benchmarks (`npm run build-sitemap`).

---
