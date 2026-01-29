# GrowthBenchmarks Design Patterns

**Last Updated**: 2026-01-29
**Purpose**: Formalized design patterns for consistent development across the codebase

---

## Backend Patterns (Python/Flask)

### 1. Connector Base Class Pattern

**Location**: `api/fathom/components/connectors_base_class/`

All API connectors (Facebook, Google) inherit from a base class that provides:
- Standard error handling via `errors.py`
- Common authentication flow
- Retry logic with exponential backoff

**Usage**:
```python
from fathom.components.connectors_base_class import ConnectorBase

class FacebookConnector(ConnectorBase):
    def __init__(self, access_token: str):
        super().__init__()
        self.access_token = access_token

    def fetch_metrics(self, account_id: str, date_range: tuple):
        # Implementation using base class utilities
        pass
```

**When to use**: Any new external API integration (TikTok, LinkedIn, etc.)

---

### 2. Firestore Wrapper Pattern

**Location**: `api/fathom/components/firestore_wrapper/`

Database operations are abstracted through a wrapper class:
- `firestore_base.py` - Core CRUD operations
- `errors.py` - Database-specific exceptions

**Usage**:
```python
from fathom.components.firestore_wrapper import FirestoreBase

class AccountRepository(FirestoreBase):
    collection_name = "Accounts"

    def get_by_provider(self, provider: str):
        return self.query(where=("provider", "==", provider))
```

**When to use**: All Firestore database operations

---

### 3. Route Blueprint Pattern

**Location**: `api/fathom/{domain}/routes.py`

Routes are organized by domain:
- `facebook/routes.py` - Facebook-specific endpoints
- `google/routes.py` - Google Ads endpoints
- `user/routes.py` - User management endpoints

**Structure**:
```python
from flask import Blueprint

facebook_bp = Blueprint('facebook', __name__, url_prefix='/facebook')

@facebook_bp.route('/metrics/<account_id>')
@authenticate
def get_metrics(account_id):
    pass
```

**When to use**: Always organize new routes by domain, never add to `app.py` directly

---

### 4. Decorator Pattern for Cross-Cutting Concerns

**Location**: `api/fathom/lib/decor_*.py`

**Available Decorators**:
| Decorator | File | Purpose |
|-----------|------|---------|
| `@authenticate` | `decor_authenticate.py` | Validates Firebase auth token |
| `@log_request` | `decor_logging.py` | Logs request/response for debugging |

**Usage**:
```python
from fathom.lib.decor_authenticate import authenticate
from fathom.lib.decor_logging import log_request

@facebook_bp.route('/metrics')
@authenticate  # Always outermost
@log_request
def get_metrics():
    pass
```

**Rule**: `@authenticate` MUST be applied to all endpoints that access user data or perform mutations.

---

### 5. Email Template Pattern

**Location**: `api/fathom/lib/email_templates/`

Email templates are Python modules that return HTML strings:

**Structure**:
```python
# email_templates/my_template.py

def render(context: dict) -> str:
    return f"""
    <html>
        <body>
            <h1>Hello {context['user_name']}</h1>
            <!-- Template content -->
        </body>
    </html>
    """
```

**Usage**:
```python
from fathom.lib.email_templates import my_template
from fathom.lib.util_send_email import send_email

html = my_template.render({"user_name": "Sam"})
send_email(to=email, subject="Subject", html=html)
```

---

### 6. Utility Module Pattern

**Location**: `api/fathom/lib/util_*.py`

Pure utility functions are prefixed with `util_`:
- `util_days.py` - Date range calculations
- `util_send_email.py` - Email sending via Postmark
- `util_identify_outliers.py` - Statistical anomaly detection
- `util_parse_params.py` - Request parameter parsing

**Rule**: Utilities must be stateless and have no side effects beyond their explicit purpose.

---

## Frontend Patterns (React)

### 1. Component Organization

**Current**: `src/Components/` (flat structure)
**Target for Phase C+**: Domain-based organization

```
src/Components/
├── common/           # Shared UI components
│   ├── Chart.jsx
│   ├── Legend.jsx
│   ├── Tooltip.jsx
│   └── Footer.jsx
├── auth/             # Authentication components
│   ├── FacebookLogin.jsx
│   ├── GoogleLogin.jsx
│   ├── EmailLogin.js
│   └── Logout.jsx
├── benchmarks/       # Benchmark display
│   ├── Benchmark.jsx
│   ├── BenchmarksList.jsx
│   └── Insights.jsx
├── signup/           # New signup flow (Phase C)
│   ├── SignupContext.jsx
│   ├── Step1LeadCapture.jsx
│   ├── Step2OAuthConnect.jsx
│   ├── Step3ReportView.jsx
│   └── Step4Booking.jsx
└── embed/            # Embeddable components (Phase B)
    └── EmbedBenchmark.jsx
```

---

### 2. Firebase Abstraction

**Location**: `src/Components/Firebase.js`

All Firebase operations go through a single abstraction:

```javascript
import { firebase, db, auth } from './Firebase';

// Authentication
auth.signInWithPopup(provider);

// Database
db.collection('Accounts').doc(accountId).get();
```

**Rule**: Never import `firebase` directly in components - always use the abstraction.

---

### 3. Data Fetching Pattern

**Location**: `src/Components/myFetch.js`

API calls use a centralized fetch wrapper:

```javascript
import { myFetch } from './myFetch';

const data = await myFetch('/facebook/metrics/123', {
    method: 'GET',
    auth: true  // Automatically adds auth header
});
```

---

### 4. Provider Configuration

**Location**: `src/Components/providers.js`

Provider-specific configuration (Facebook, Google) is centralized:

```javascript
import { PROVIDERS } from './providers';

const config = PROVIDERS['facebook'];
// { name: 'Facebook', metrics: [...], benchmarks: [...] }
```

---

### 5. Cached Data Pattern

**Location**: `src/Components/cachedBenchmarks.js`

Static benchmark data is cached at build time for performance:

```javascript
// Generated by: npm run cache
import { cachedBenchmarks } from './cachedBenchmarks';

// Use for initial render, then fetch fresh data
const benchmarks = cachedBenchmarks['facebook'] || await fetchBenchmarks();
```

---

## Data Patterns

### 1. Collection Naming

| Collection | ID Format | Purpose |
|------------|-----------|---------|
| `Users` | Firebase Auth UID | User profiles |
| `Accounts` | `{provider}-{account_id}` | Connected ad accounts |
| `Benchmarks` | `{provider}-{benchmark_type}.{value}` | Aggregated benchmark data |
| `Rankings` | `{year}-{month}` | Monthly performance rankings |

### 2. Metrics Structure

```javascript
// Stored in Accounts/{id}/metrics/{date}
{
    date: "2026-01-29",
    spend: 1234.56,
    impressions: 100000,
    clicks: 2500,
    conversions: 125,
    // Calculated fields
    cpm: 12.35,
    cpc: 0.49,
    ctr: 0.025,
    cpa: 9.88
}
```

---

## New Patterns for Phase D (AI Audit)

### 1. Audit Pipeline Pattern

**Planned Location**: `api/fathom/lib/audit_pipeline.py`

```
Rules Engine → LLM Narrative → RAG Enhancement → Output Generation
     ↓              ↓                ↓                  ↓
audit_rules.py  audit_llm.py   audit_rag.py    generate_audit_report.py
```

### 2. RAG Pattern

**Planned Location**: `api/fathom/lib/audit_rag.py`

```python
class AuditRAG:
    def __init__(self, chroma_client, embeddings):
        self.collection = chroma_client.get_collection("playbooks")

    def get_relevant_context(self, finding: str, k: int = 3) -> list:
        """Retrieve relevant playbook snippets for a finding."""
        pass
```

---

## Anti-Patterns to Avoid

| Don't | Do Instead |
|-------|------------|
| Add routes to `app.py` | Create domain-specific blueprint in `{domain}/routes.py` |
| Import Firebase directly | Use `src/Components/Firebase.js` abstraction |
| Hardcode API keys | Use environment variables via `api/fathom/config.py` |
| Skip `@authenticate` | Always protect user data endpoints |
| Create flat component files | Organize by domain in subdirectories |
| Write inline SQL/queries | Use Firestore wrapper patterns |

---

## Adding New Features Checklist

- [ ] Review this document for applicable patterns
- [ ] Check if base class/abstraction exists for your use case
- [ ] Follow route blueprint pattern for new endpoints
- [ ] Apply `@authenticate` to protected endpoints
- [ ] Place components in appropriate domain directory
- [ ] Update this document if introducing new patterns
