# V1 Migration Plan: Modular Architecture + Infrastructure Swap

## Context

V1 is a tightly-coupled monolith: CRA 4 / React 17 / React Router 5 / Firebase Auth / Firestore / Cloud Run / Firebase Hosting. The goal is twofold:

1. **Infrastructure swap**: Vite, Supabase (auth + Postgres), Vercel (frontend), Railway (API)
2. **Modular refactor**: Break tight coupling so changes in one area stop breaking everything else

### Current coupling problems (from codebase audit)

**Frontend:**
- [Main.jsx](src/Components/Main.jsx) — 968 lines, 12+ responsibilities: auth, data fetching, company selection, filter logic, chart data prep, localStorage caching, error handling
- [Chart.jsx](src/Components/Chart.jsx) — 992 lines, receives 15+ individual props
- 8 files directly `import { firebase }` — no auth abstraction
- [myFetch.js](src/Components/myFetch.js) imports Firebase for tokens — every API caller transitively depends on Firebase
- No state management — 12+ boolean loading flags, localStorage as source of truth

**Backend:**
- 10+ files call `db.collection()` directly with hardcoded collection names — no data access layer
- [user/routes.py](api/fathom/user/routes.py) (372 lines) mixes HTTP parsing + business logic + Firestore writes in single functions
- [connector_base.py](api/fathom/components/connectors_base_class/connector_base.py) reads Firestore on `__init__` — can't test or swap storage
- `FireStoreWrapper` is useless (thin forwarding, only used by GoogleAdsConnector)
- Business logic in `generate_account_benchmarks.py`, `generate_anomalies.py`, `rankings.py` tangled with data access
- Authorization checked AFTER data fetch in `get_data`

### Design patterns to fix this

Six patterns, integrated into the migration phases:

| # | Pattern | Problem it solves | Phase |
|---|---------|-------------------|-------|
| 1 | **Repository Layer** (backend) | 10+ files access Firestore directly; swap = grep-and-replace 30+ call sites | Phase 0 (prep) |
| 2 | **Auth Adapter** (frontend) | 8 files import Firebase; swap = change 8 files | Phase 0 (prep) |
| 3 | **Service Layer** (backend) | Route handlers are 76-133 line functions mixing HTTP + logic + data | Phase 3 |
| 4 | **Connector Decoupling** (backend) | BaseConnector couples API clients to storage | Phase 3 |
| 5 | **Hook Extraction** (frontend) | Main.jsx is 968 lines with 12+ responsibilities | Phase 2 |
| 6 | **Chart Props Object** (frontend) | Chart receives 15+ individual props | Phase 2 |

---

## Phase 0: Decoupling Prep (Pure Refactors, No Behavior Change)

Do these BEFORE any infrastructure changes. They are mechanical extractions that make the actual swap trivial.

### 0.1 Backend: Repository Layer

**Create** `api/fathom/repositories/` with one class per collection:

```
api/fathom/repositories/
    __init__.py          # exports repo instances
    base.py              # BaseRepository with _db() helper
    accounts.py          # AccountsRepository
    users.py             # UsersRepository
    benchmarks.py        # BenchmarksRepository
    rankings.py          # RankingsRepository
    anomalies.py         # AnomaliesRepository
```

**Interface** (example — `accounts.py`):
```python
class AccountsRepository(BaseRepository):
    def get_by_id(self, provider_id, account_id) -> dict | None
    def get_metrics(self, provider_id, account_id) -> list[dict]
    def save_metrics(self, provider_id, account_id, date, data) -> None
    def update(self, provider_id, account_id, data) -> None
    def get_with_questionnaire(self, provider_id=None) -> list
    def delete(self, provider_id, account_id) -> None
```

**What changes**: Every file that currently does `db = current_app.extensions["db"]; db.collection('Accounts')...` changes to `from fathom.repositories import accounts_repo; accounts_repo.get_by_id(...)`.

**Files to update** (10 files, ~50 call sites):

| File | Current pattern | New pattern |
|------|----------------|-------------|
| [decor_authenticate.py](api/fathom/lib/decor_authenticate.py) | `db.collection('users').where('uid','==',uid)` | `users_repo.get_by_uid(uid)` |
| [user/routes.py](api/fathom/user/routes.py) | 13 Firestore operations | Call repos |
| [facebook/routes.py](api/fathom/facebook/routes.py) | 3 operations | Call repos |
| [google/routes.py](api/fathom/google/routes.py) | 2 operations | Call repos |
| [connector_base.py](api/fathom/components/connectors_base_class/connector_base.py) | `self.db.collection('Accounts')` on init | Accept account dict, no DB on init |
| [facebook/connector.py](api/fathom/facebook/connector.py) | 13 Firestore ops | Call repos or return data for caller to persist |
| [generate_account_benchmarks.py](api/fathom/lib/generate_account_benchmarks.py) | 3+ operations | Call repos |
| [generate_anomalies.py](api/fathom/lib/generate_anomalies.py) | 5 operations | Call repos |
| [rankings.py](api/fathom/lib/rankings.py) | 3 operations | Call repos |
| [intelligence/routes_brand_narrative.py](api/fathom/intelligence/routes_brand_narrative.py) | 5 operations | Call repos |

**Delete**: `FireStoreWrapper` (`api/fathom/components/firestore_wrapper/`) — replaced by repositories.

**Why first**: Once all Firestore access goes through repositories, the Supabase swap becomes changing 5 repository files instead of 30+ scattered call sites.

**Testing**: Each repository tested with MockFirestore. When Supabase comes, swap mock to test Supabase instance.

### 0.2 Frontend: Auth Adapter

**Create** `src/lib/auth.js` — the ONLY file that imports Firebase:

```javascript
// src/lib/auth.js
import { firebase, facebookAuthProvider } from "../Components/Firebase";

export function getCurrentUser() { return firebase.auth().currentUser; }
export async function getIdToken() {
  const user = getCurrentUser();
  return user ? user.getIdToken(true) : null;
}
export function onAuthStateChanged(cb) { return firebase.auth().onAuthStateChanged(cb); }
export function signOut() { return firebase.auth().signOut(); }
export function signInWithFacebook() { return firebase.auth().signInWithPopup(facebookAuthProvider); }
// ... etc for Google, Email
```

**Files to update** (8 files):

| File | Current | After |
|------|---------|-------|
| [App.jsx](src/App.jsx) | `import { firebase }` → `firebase.auth().onAuthStateChanged` | `import { onAuthStateChanged } from "../lib/auth"` |
| [Main.jsx](src/Components/Main.jsx) | `import { firebase }` → 4 `firebase.auth()` calls | `import { onAuthStateChanged, getCurrentUser } from "../lib/auth"` |
| [myFetch.js](src/Components/myFetch.js) | `import { firebase }` → `firebase.auth().currentUser.getIdToken` | `import { getIdToken } from "../lib/auth"` |
| [Logout.jsx](src/Components/Logout.jsx) | `firebase.auth().signOut()` | `import { signOut } from "../lib/auth"` |
| [Profile.js](src/Components/Profile.js) | `firebase.auth().currentUser` | `import { getCurrentUser } from "../lib/auth"` |
| [FacebookLogin.jsx](src/Components/FacebookLogin.jsx) | `firebase.auth().signInWithPopup` | `import { signInWithFacebook } from "../lib/auth"` |
| [GoogleLogin.jsx](src/Components/GoogleLogin.jsx) | Firebase credential creation | `import { signInWithGoogleCredential } from "../lib/auth"` |
| [EmailLogin.js](src/Components/EmailLogin.js) | Firebase email link | `import { sendMagicLink, signInWithEmailLink } from "../lib/auth"` |

**Why first**: When Supabase auth comes (Phase 2), you change ONE file (`auth.js`) instead of 8.

### 0.3 Phase 0 verification

- All existing tests pass (no behavior change)
- `npm start` + `npm run server` — app works identically
- `grep -r "firebase.auth()" src/` returns only `src/lib/auth.js` and `src/Components/Firebase.js`
- `grep -r "db.collection\|current_app.extensions\[.db.\]" api/fathom/` returns only `repositories/` files

---

## Phase 1: Vite + Dependency Upgrades (Frontend Only)

No infra changes. Swap build tool, upgrade React/Router/deps.

### 1.1 Dependency changes

**Remove**: `react-scripts`, `firebase-admin`, `firebase-functions`, `react-firebase-hooks`, `react-router-sitemap`, `cors`, `fbgraph`, `install`, `babel-preset-es2015`, `babel-preset-react`, `babel-register`

**Upgrade**: `react` → 18.x, `react-dom` → 18.x, `react-router-dom` → 6.x, `@testing-library/react` → 14.x

**Add**: `vite` (~5.x), `@vitejs/plugin-react` (~4.x)

**Keep**: `bootstrap` 4.5.3, `react-bootstrap` 1.5.2, `d3` 6.2.0, `moment`, FontAwesome, `mathjs`, `cross-env`

### 1.2 Vite config

**Create** `vite.config.js`:
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, https: true,
    proxy: {
      '/user': 'http://localhost:8000',
      '/facebook': 'http://localhost:8000',
      '/google': 'http://localhost:8000',
      '/insights': 'http://localhost:8000',
      '/cache_benchmarks': 'http://localhost:8000',
      '/keep_alive': 'http://localhost:8000',
    },
  },
  envPrefix: 'VITE_',
})
```

**GOTCHA**: CRA's `"proxy"` in [package.json:5](package.json#L5) is a catch-all. Vite requires explicit route prefixes. New backend routes need to be added to the proxy list.

### 1.3 index.html to root

Move `public/index.html` → `index.html`. Replace `%PUBLIC_URL%` with empty string. Add `<script type="module" src="/src/index.jsx"></script>` before `</body>`.

### 1.4 React 18 entry point

Rename `src/index.js` → `src/index.jsx`:
```jsx
import { createRoot } from "react-dom/client";
const root = createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_OAUTH_CLIENT_ID}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>
);
```

**Pre-requisite fix**: `firebase.auth().onAuthStateChanged()` at [App.jsx:31](src/App.jsx#L31) is called outside `useEffect` — registers a new listener every render. Wrap in `useEffect` with cleanup. (Uses `onAuthStateChanged` from `auth.js` since Phase 0 is done.)

### 1.5 Env vars `REACT_APP_*` → `VITE_*`

Rename in `.env`:
- `REACT_APP_API_KEY` → `VITE_API_KEY`
- `REACT_APP_AUTH_DOMAIN` → `VITE_AUTH_DOMAIN`
- `REACT_APP_PROJECT_ID` → `VITE_PROJECT_ID`
- `REACT_APP_MESSAGING_SENDER_ID` → `VITE_MESSAGING_SENDER_ID`
- `REACT_APP_GOOGLE_OAUTH_CLIENT_ID` → `VITE_GOOGLE_OAUTH_CLIENT_ID`

Update code: `process.env.REACT_APP_*` → `import.meta.env.VITE_*` in [Firebase.js](src/Components/Firebase.js), [index.jsx](src/index.js). `process.env.NODE_ENV === "production"` → `import.meta.env.PROD` in [myFetch.js](src/Components/myFetch.js).

### 1.6 React Router v5 → v6

Most invasive part. Every routing file changes.

**[App.jsx](src/App.jsx)**: `Switch` → `Routes`, `component={X}` → `element={<X />}`, remove `exact`, route arrays → two `<Route>` elements, `Redirect` → `Navigate`.

**[Main.jsx](src/Components/Main.jsx)**: `props.history.push()` → `useNavigate()` + `navigate()`.

**[EmailLogin.js](src/Components/EmailLogin.js)**: `props.history.push("/")` → `navigate("/")`.

**[Profile.js](src/Components/Profile.js)**: `useHistory()` → `useNavigate()`, `history.goBack()` → `navigate(-1)`.

**No changes needed**: [Home.jsx](src/Components/Home.jsx) (`useLocation`), [Benchmark.jsx](src/Components/Benchmark.jsx) (`useParams`), [BenchmarksList.jsx](src/Components/BenchmarksList.jsx) (`Link`, `useParams`), [Insights.jsx](src/Components/Insights.jsx) (`useParams`).

**Route ordering**: v6 ranks static > dynamic. `/:providerName/insights` won't be swallowed by `/:selectedCompanyId/:selectedFilterId`. Verify with tests.

### 1.7 Build scripts

**[cacheBenchmarks.js](src/cacheBenchmarks.js)**: Plain Node/CJS — no changes needed.

**[buildSitemap.js](buildSitemap.js)**: Rename to `.mjs`, update import to `"./src/Components/filters.js"`, run with `node buildSitemap.mjs`. Drop Babel 6 devDeps.

### 1.8 Package.json scripts

```json
"start": "vite",
"build": "vite build",
"preview": "vite preview",
"test": "react-scripts test",
"cache": "cross-env NODE_ENV=production node ./src/cacheBenchmarks",
"build-sitemap": "node buildSitemap.mjs",
"server": "cd api && docker-compose up --build"
```

### 1.9 Phase 1 verification

- `npm start` — app loads at localhost:3000, no console errors
- Navigate every route: `/`, `/about`, `/join`, `/profile`, `/logout`, `/:providerName/insights`, `/:providerName/benchmarks`, `/:providerName/:metric/:benchmark`, `/embed/...`, `/privacy`, `/terms`, `/*`
- API proxy: dev requests to `/user/...`, `/facebook/...`, `/google/...` reach localhost:8000
- `npm run build` — production build succeeds (no `--openssl-legacy-provider`)
- Chart.jsx D3 rendering works

---

## Phase 2: Frontend Modularization + Supabase Auth

Two things happen in parallel: extract hooks from Main.jsx AND swap Firebase → Supabase auth.

### 2.1 Hook Extraction from Main.jsx (Pattern 5)

**Create** `src/hooks/`:

```
src/hooks/
    useCompanies.js       # company list fetching + selection + localStorage cache
    useBenchmarkData.js   # benchmark data fetching + processing
    useMetricData.js      # user metric data fetching
    useChartData.js       # data transformation (the useMemo blocks)
```

**`useCompanies.js`** — extracts from Main.jsx lines 386-559:
```javascript
export function useCompanies(user) {
  // Returns: { companiesList, selectedCompany, selectCompany, isLoading }
  // Owns: localStorage cache for selectedCompany, /user/get_my_companies fetch
}
```

**`useMetricData.js`** — extracts from Main.jsx lines 613-663:
```javascript
export function useMetricData(selectedCompany, providerId) {
  // Returns: { allRawData, dates, isLoading, refresh }
  // Owns: /user/get_data fetch, raw data state
}
```

**`useBenchmarkData.js`** — extracts from Main.jsx lines 561-611:
```javascript
export function useBenchmarkData(selectedCompany, selectedBenchmarks) {
  // Returns: { benchmarkRawData, similarRawData, isLoading }
  // Owns: benchmark + similar company fetch
}
```

**`useChartData.js`** — extracts from Main.jsx lines 216-293, 757-835:
```javascript
export function useChartData(allRawData, benchmarkRawData, similarRawData, dates, conversionEvent) {
  // Returns: { data, similarData, benchmarkData, averages }
  // Owns: all useMemo transformation logic
}
```

**Main.jsx after** — ~150-200 lines, thin shell composing hooks + rendering:
```jsx
const Main = ({ user, setUser, logout }) => {
  const { companiesList, selectedCompany, selectCompany, isLoading } = useCompanies(user);
  const { allRawData, dates, isLoading: isLoadingData } = useMetricData(selectedCompany, providerId);
  const { benchmarkRawData, similarRawData } = useBenchmarkData(selectedCompany, benchmarks);
  const { data, similarData, benchmarkData, averages } = useChartData(...);
  // JSX only — no business logic
};
```

### 2.2 Chart Props Object (Pattern 6)

Replace 15+ individual Chart props with 4 structured objects:

```jsx
<Chart
  data={{ allData, dates, averages, selectedCharts }}
  display={{ title, metric, ySuffix, currency, isLowGood }}
  filters={{ hasConversionEvent, selectedConversionEvent, conversionEvents, allBenchmarks }}
  callbacks={{ handleSelectConversionEvent, handleSelectCharts, setStartDate }}
  isLoading={isLoadingData}
/>
```

### 2.3 Supabase Auth Setup

- Create Supabase project, enable Google/Facebook/Email providers
- Add to `.env`: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
- Add dep: `@supabase/supabase-js ^2.x`

### 2.4 Swap auth.js implementation (Firebase → Supabase)

**This is where the Phase 0 auth adapter pays off.** Change ONE file:

```javascript
// src/lib/auth.js — swap implementation
import { createClient } from '@supabase/supabase-js'
const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY);

export async function getIdToken() {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token ?? null;
}
export function onAuthStateChanged(cb) {
  const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
    cb(session?.user ?? null);
  });
  return () => subscription.unsubscribe();
}
export function signOut() { return supabase.auth.signOut(); }
export function signInWithFacebook() {
  return supabase.auth.signInWithOAuth({ provider: 'facebook', options: { scopes: 'ads_read', redirectTo: window.location.origin } });
}
// ... etc
```

**No other frontend files change** — they all import from `auth.js`.

### 2.5 Auth flow specifics

| Flow | Implementation |
|------|---------------|
| **Google** | Keep custom auth-code flow: `@react-oauth/google` gets code → backend exchanges → `supabase.auth.signInWithIdToken()`. Needed for Google Ads refresh tokens. |
| **Facebook** | `supabase.auth.signInWithOAuth({ provider: 'facebook' })` — redirect flow. UX change: redirect instead of popup. |
| **Email** | `supabase.auth.signInWithOtp({ email })` — Supabase handles magic link callback. |

**GOTCHA — provider tokens**: Supabase only exposes `provider_token` at initial sign-in, not on refresh. Backend already stores tokens via `/user/upsert` — no change needed. Capture in `onAuthStateChange` when `event === 'SIGNED_IN'`.

**GOTCHA — UID format**: Firebase UIDs are short strings, Supabase UIDs are UUIDs. Match by email during dual-auth, update `uid` field in `/user/upsert`.

### 2.6 Backend dual-auth shim

Update [decor_authenticate.py](api/fathom/lib/decor_authenticate.py) to accept both Firebase and Supabase JWTs (uses `users_repo` from Phase 0):

```python
def authenticate(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        id_token = request.headers.get('Authorization', '').split(" ")[-1]
        uid = None
        # Try Supabase first
        supabase_secret = os.environ.get('SUPABASE_JWT_SECRET')
        if supabase_secret:
            try:
                decoded = pyjwt.decode(id_token, supabase_secret, algorithms=["HS256"], audience="authenticated")
                uid = decoded.get('sub')
            except pyjwt.InvalidTokenError:
                pass
        # Fallback to Firebase
        if uid is None:
            decoded = current_app.extensions['auth'].verify_id_token(id_token)
            uid = decoded['uid']
        _, user = users_repo.get_by_uid(uid)
        return func(user, *args, **kwargs)
    return wrapper
```

Add `PyJWT>=2.0.0` to `api/requirements.txt`.

### 2.7 Phase 2 verification

- All 3 auth flows work: email magic link, Google OAuth, Facebook OAuth
- API calls include valid Supabase JWT, backend accepts
- Legacy Firebase JWT still works (dual-auth)
- Hook extraction: Main.jsx < 200 lines, each hook independently testable
- Chart props: structured objects, no 15+ individual props

---

## Phase 3: Backend Modularization + Firestore → Postgres

### 3.1 Service Layer (Pattern 2)

Extract business logic from route handlers into service functions. Services call repositories, not Firestore directly.

**Create** service files alongside routes:
```
api/fathom/user/services.py
api/fathom/facebook/services.py
api/fathom/google/services.py
```

**Example — extracting `get_data`** from [user/routes.py:69-202](api/fathom/user/routes.py):

```python
# api/fathom/user/services.py
from fathom.repositories import accounts_repo, benchmarks_repo

def assemble_company_data(user, company_id, provider_id, selected_benchmarks):
    """Pure business logic. No request/response objects."""
    # Authorization BEFORE data fetch (fixes current bug)
    account_ids = _get_account_ids_for_provider(user, provider_id)
    if not user.get('is_god') and company_id not in account_ids:
        return {"error": "Insufficient permissions"}

    account = accounts_repo.get_by_id(provider_id, company_id)
    if not account:
        return {"error": "Account not found"}

    metrics = accounts_repo.get_metrics(provider_id, company_id)
    benchmarks = {b: benchmarks_repo.get_with_metrics(b) for b in selected_benchmarks}
    # ... return assembled data dict
```

```python
# api/fathom/user/routes.py (thin handler)
@user.route('/get_data', methods=['POST'])
@authenticate
def get_data(user):
    data = request.get_json()
    result = assemble_company_data(user, data['companyId'], data['providerId'], data.get('selectedBenchmarks', []))
    return jsonify(result)
```

**Route handlers to extract** (6 critical ones):

| Handler | File | Current lines | Service function |
|---------|------|--------------|-----------------|
| `upsert_user` | user/routes.py | 76 lines | `user_services.upsert_user(uid, provider_data)` |
| `get_data` | user/routes.py | 133 lines | `user_services.assemble_company_data(...)` |
| `get_my_companies` | user/routes.py | 21 lines | `user_services.get_companies_for_user(user)` |
| `load_metrics` | facebook/routes.py | 45 lines | `fb_services.sync_all_accounts(provider_id)` |
| `set_conversion_event` | facebook/routes.py | 19 lines | `fb_services.set_conversion_event(...)` |
| `load_metrics` | google/routes.py | 40 lines | `google_services.sync_all_accounts(provider_id)` |

**Key fix**: Authorization checked BEFORE data fetch (currently checked after in `get_data` line 118).

### 3.2 Connector Decoupling (Pattern 3)

Split each connector into API client (pure) + data sync (uses repos):

**Before** ([connector_base.py](api/fathom/components/connectors_base_class/connector_base.py)):
```python
class BaseConnector:
    def __init__(self, account_id, ...):
        self.db = current_app.extensions["db"]          # DB on init
        self.account_ref = self.db.collection('Accounts').document(...)  # Firestore ref
        self.account = self.account_ref.get().to_dict()  # Reads on init
```

**After**:
```python
class BaseConnector:
    def __init__(self, account_id, access_token, account_data, ...):
        # No self.db, no self.account_ref — accept data, don't fetch it
        self.account_id = account_id
        self.access_token = access_token
        self.account = account_data  # passed in by caller
```

**Data sync moves to services**:
```python
# api/fathom/facebook/services.py
def sync_facebook_metrics(account_id, access_token):
    account = accounts_repo.get_by_id('fb', account_id)
    connector = FacebookConnector(account_id, access_token, account_data=account)
    raw_metrics = connector.fetch_from_api()  # pure API call, no Firestore
    for date, data in raw_metrics.items():
        accounts_repo.save_metrics('fb', account_id, date, data)
```

### 3.3 Postgres schema

```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT, provider_id TEXT, first_name TEXT, last_name TEXT,
  is_subscribed BOOLEAN DEFAULT FALSE, is_god BOOLEAN DEFAULT FALSE,
  access_token TEXT, facebook_access_token TEXT, google_access_token TEXT,
  refresh_token TEXT, facebook_refresh_token TEXT, google_refresh_token TEXT,
  intelligence_enabled BOOLEAN DEFAULT FALSE,
  company TEXT, competitors TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_accounts (
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  account_id TEXT NOT NULL,
  account_type TEXT NOT NULL CHECK (account_type IN ('facebook','facebook_fake','google','google_fake')),
  PRIMARY KEY (user_id, account_id, account_type)
);

CREATE TABLE accounts (
  id TEXT PRIMARY KEY,  -- "{provider_id}-{account_id}"
  account_id TEXT NOT NULL, name TEXT, currency TEXT,
  provider_id TEXT NOT NULL, login_id TEXT,
  has_completed_questionnaire BOOLEAN DEFAULT FALSE,
  last_date_saved TEXT, similar_companies TEXT[],
  conversion_event TEXT, industry TEXT, property TEXT, model TEXT, spend TEXT, location TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE metrics (
  account_id TEXT REFERENCES accounts(id) ON DELETE CASCADE,
  date TEXT NOT NULL,
  impressions DOUBLE PRECISION DEFAULT 0, clicks DOUBLE PRECISION DEFAULT 0,
  spend DOUBLE PRECISION DEFAULT 0, link_click DOUBLE PRECISION DEFAULT 0,
  conversion_events JSONB DEFAULT '{}',
  PRIMARY KEY (account_id, date)
);

CREATE TABLE benchmarks (id TEXT PRIMARY KEY, date_saved TEXT);

CREATE TABLE benchmark_metrics (
  benchmark_id TEXT REFERENCES benchmarks(id) ON DELETE CASCADE,
  date TEXT NOT NULL, accounts INTEGER DEFAULT 0,
  impressions DOUBLE PRECISION DEFAULT 0, clicks DOUBLE PRECISION DEFAULT 0,
  spend DOUBLE PRECISION DEFAULT 0, link_click DOUBLE PRECISION DEFAULT 0,
  PRIMARY KEY (benchmark_id, date)
);

CREATE TABLE commentary (
  benchmark_id TEXT REFERENCES benchmarks(id) ON DELETE CASCADE,
  year_month TEXT NOT NULL, accounts INTEGER DEFAULT 0,
  impressions DOUBLE PRECISION DEFAULT 0, clicks DOUBLE PRECISION DEFAULT 0,
  spend DOUBLE PRECISION DEFAULT 0, link_click DOUBLE PRECISION DEFAULT 0,
  PRIMARY KEY (benchmark_id, year_month)
);

CREATE TABLE rankings (
  id TEXT PRIMARY KEY, account_id TEXT, account_name TEXT, month TEXT,
  provider_id TEXT, clicks DOUBLE PRECISION, spend DOUBLE PRECISION,
  impressions DOUBLE PRECISION, cpc DOUBLE PRECISION, ctr DOUBLE PRECISION,
  cpm DOUBLE PRECISION, cpc_rank INTEGER, ctr_rank INTEGER, cpm_rank INTEGER
);

CREATE TABLE anomalies (
  id SERIAL PRIMARY KEY, account_id TEXT REFERENCES accounts(id) ON DELETE CASCADE,
  date TEXT NOT NULL, value DOUBLE PRECISION, provider_id TEXT, metric TEXT
);

CREATE TABLE intelligence_brand_narrative (
  user_id UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
  narrative TEXT, company_highlights JSONB DEFAULT '[]'
);
```

### 3.4 Swap Repository Implementations (Firestore → Supabase)

**This is where the Phase 0 repository layer pays off.** Change repository internals only:

```python
# api/fathom/repositories/accounts.py — Supabase version
from fathom.lib.db import get_db

class AccountsRepository:
    def get_by_id(self, provider_id, account_id):
        result = get_db().table('accounts').select('*').eq('id', f'{provider_id}-{account_id}').execute()
        return result.data[0] if result.data else None

    def get_metrics(self, provider_id, account_id):
        result = get_db().table('metrics').select('*').eq('account_id', f'{provider_id}-{account_id}').order('date').execute()
        return result.data

    def save_metrics(self, provider_id, account_id, date, data):
        get_db().table('metrics').upsert({
            'account_id': f'{provider_id}-{account_id}', 'date': date, **data
        }).execute()
```

**No service or route changes needed** — they call repository methods, not Firestore directly.

### 3.5 Data migration

~400K documents total. Create `api/scripts/migrate_firestore_to_postgres.py`:
- Initialize Firebase Admin SDK (read-only) + Supabase client (write)
- Migrate order: profiles → user_accounts → accounts → metrics → benchmarks → benchmark_metrics → commentary → rankings → anomalies → intelligence
- Batch inserts (100 rows), ON CONFLICT DO NOTHING for idempotent reruns
- **GOTCHA**: Supabase returns max 1000 rows — use `.range(from, to)` for large tables
- **GOTCHA**: `user_accounts` junction table: iterate `account_ids[]`, `fake_account_ids[]`, `google_account_ids[]`, `google_fake_account_ids[]` arrays

### 3.6 Lib file migrations

Business logic files that currently mix fetch + calculate + write. With repositories + services in place, these become cleaner:

| File | Current | After |
|------|---------|-------|
| [generate_account_benchmarks.py](api/fathom/lib/generate_account_benchmarks.py) | Streams Accounts + Metrics, writes Benchmarks | Reads via `accounts_repo`, writes via `benchmarks_repo` |
| [generate_anomalies.py](api/fathom/lib/generate_anomalies.py) | Reads Accounts + Metrics + Anomalies, writes Anomalies | Reads/writes via repos. Pure detection logic stays as-is. |
| [rankings.py](api/fathom/lib/rankings.py) | Reads Accounts + Metrics, writes Rankings | Reads/writes via repos |
| [generate_commentary.py](api/fathom/lib/generate_commentary.py) | Reads Benchmarks + Metrics, writes Commentary | Reads/writes via repos |
| [get_benchmark_data.py](api/fathom/lib/get_benchmark_data.py) | Reads Benchmarks/Metrics | Reads via `benchmarks_repo` |
| [update_company_data.py](api/fathom/lib/update_company_data.py) | Reads/writes users + Accounts | Uses repos |
| [send_anomaly_emails.py](api/fathom/lib/send_anomaly_emails.py) | Reads users + Anomalies | Uses repos |

### 3.7 Phase 3 verification

- Data migration: row counts match Firestore doc counts
- Spot-check: 10 random accounts, compare metrics Postgres vs Firestore
- API regression: every endpoint returns same response shapes
- Cron jobs: `generate_benchmarks`, `generate_anomalies`, `generate_commentary`, `generate_rankings`
- Full user flow: sign up → create company → fetch data → view benchmarks → view insights
- Remove `firebase-admin` from `requirements.txt`; add `supabase>=2.0.0`

---

## Phase 4: Deploy to Vercel + Railway

### 4.1 Vercel (frontend)

**Create** `vercel.json`:
```json
{
  "framework": "vite",
  "buildCommand": "npm run cache && npm run build-sitemap && npm run build",
  "outputDirectory": "dist",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

**Env vars**: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_GOOGLE_OAUTH_CLIENT_ID`, `VITE_API_URL`

**Update** [myFetch.js](src/Components/myFetch.js): `url = (import.meta.env.VITE_API_URL || "") + url`

**GOTCHA**: [buildSitemap.mjs](buildSitemap.js) fetches from `localhost:8000` — add production URL fallback.

### 4.2 Railway (backend)

- Connect GitHub repo, subdirectory `api/`
- Uses existing `api/Dockerfile`
- Health check: `/keep_alive`

**Env vars**: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_JWT_SECRET`, FB/Google API keys, `POSTMARK_SERVER_API_TOKEN`, `CORS_ORIGINS`

**Update CORS** in [app.py](api/fathom/app.py):
```python
cors_origins = os.environ.get('CORS_ORIGINS', 'https://growthbenchmarks.com').split(',')
CORS(app, origins=cors_origins)
```

### 4.3 DNS cutover

1. Deploy backend to Railway, verify
2. Add `api.growthbenchmarks.com` custom domain in Railway
3. Deploy frontend to Vercel, verify
4. Add `growthbenchmarks.com` + `www.growthbenchmarks.com` in Vercel
5. TTL 60s before cutover, keep GCP running 1 week as fallback

### 4.4 Cleanup

Delete: `firebase.json`, `.firebaserc`, Firebase service account JSON. Update deploy scripts.

### 4.5 Phase 4 verification

- `curl https://api.growthbenchmarks.com/` returns time + revision
- `https://growthbenchmarks.com` loads, all routes work
- Full user flow: login (3 methods) → select company → view chart → insights → profile → logout
- Cron jobs run successfully

---

## What NOT to do (anti-patterns to avoid)

- **No abstract factory for repositories** — just plain classes, there are only 4-5 collections
- **No Redux/Zustand** — React hooks + context is sufficient for ~500 users
- **No GraphQL** — ~15 endpoints total, REST is fine
- **No ORM** — use Supabase client directly in repositories
- **No event bus** — direct function calls between services and repositories
- **Don't refactor Chart.jsx** (992 lines) in this migration — it's D3 rendering, mostly stable, and not causing coupling problems. Address later if needed.

---

## Risk Matrix

| Risk | Impact | Mitigation |
|------|--------|------------|
| React Router v6 route conflicts | Medium | Test every route; v6 ranks static > dynamic |
| Provider tokens lost on Supabase refresh | High if unhandled | Backend stores tokens via `/user/upsert` (already does) |
| Supabase UUID vs Firebase UID mismatch | High | Match by email during dual-auth; update uid |
| Firestore→Postgres data loss | Low | Verify checksums; keep Firestore read-only 30 days |
| Facebook popup→redirect UX change | Low | Standard OAuth, acceptable |
| Repository layer adds overhead | Low | Repositories are thin, no perf impact |

## Execution order summary

```
Phase 0: Decoupling prep (pure refactors)
  ├── 0.1 Backend repository layer (10 files)
  └── 0.2 Frontend auth adapter (8 files)

Phase 1: Vite + deps (frontend only)
  ├── 1.1-1.2 Vite config + index.html
  ├── 1.3-1.5 React 18 + env vars
  └── 1.6 React Router v6

Phase 2: Frontend modularization + Supabase auth
  ├── 2.1 Extract hooks from Main.jsx
  ├── 2.2 Chart props restructure
  ├── 2.3-2.4 Supabase auth (swap auth.js only)
  └── 2.5-2.6 Backend dual-auth shim

Phase 3: Backend modularization + Firestore → Postgres
  ├── 3.1 Service layer extraction
  ├── 3.2 Connector decoupling
  ├── 3.3-3.4 Postgres schema + swap repo implementations
  └── 3.5-3.6 Data migration + lib file updates

Phase 4: Deploy
  ├── 4.1-4.2 Vercel + Railway
  └── 4.3-4.4 DNS cutover + cleanup
```
