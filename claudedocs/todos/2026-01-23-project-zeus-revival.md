# Todo: Project Zeus - GrowthBenchmarks Revival

**Created**: 2026-01-23 14:45
**Status**: In Progress
**Task Type**: migration + security + feature
**Context**: Complete revival of GrowthBenchmarks benchmark tool including security fixes, API updates, and new features

---

## Phase P0: Critical Security & Compliance (IMMEDIATE)

**Goal**: Fix critical security vulnerabilities and restore Facebook API access
**Prerequisites**: None - these are blocking issues
**Risk Level**: HIGH - Exposed secrets, overdue compliance deadline

### Facebook Data Use Checkup (Manual)
- [ ] **P0.1**: Complete Facebook Data Use Checkup recertification
  - **URL**: https://developers.facebook.com/apps/506749186452843/data-use-checkup/
  - **AC**: Recertification submitted, API access restored
  - **Notes**: Deadline was Jan 20, 2026 - already overdue

### Security Remediation
- [x] **P0.2**: Create comprehensive .gitignore ✅ *Completed 2026-01-29*
  - **File**: [.gitignore](.gitignore)
  - **AC**: All sensitive files excluded from git
  - **Command**: `cat .gitignore | grep -E "\.env|firebase|secret"`

- [x] **P0.3**: Move hardcoded Mailchimp credentials to env vars ✅ *Completed 2026-01-29*
  - **File**: [api/fathom/user/routes.py](api/fathom/user/routes.py)
  - **AC**: No hardcoded API keys in source code
  - **Config**: Added `MAILCHIMP_API_KEY`, `MAILCHIMP_SERVER`, `MAILCHIMP_LIST_ID` to config.py

- [x] **P0.4**: Move hardcoded Google credentials to env vars ✅ *Completed 2026-01-29*
  - **File**: [api/fathom/user/routes.py](api/fathom/user/routes.py)
  - **AC**: No hardcoded client_secret in source code
  - **Config**: Added `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET` to config.py

- [x] **P0.5**: Add authentication to /send_email endpoint ✅ *Completed 2026-01-29*
  - **File**: [api/fathom/app.py](api/fathom/app.py:53-62)
  - **AC**: Endpoint requires @authenticate decorator
  - **Change**: Changed to POST method with @authenticate

- [x] **P0.6**: Add authentication to /send_rankings endpoint ✅ *Completed 2026-01-29*
  - **File**: [api/fathom/app.py](api/fathom/app.py:64-80)
  - **AC**: Endpoint requires @authenticate decorator
  - **Change**: Changed to POST method with @authenticate

- [x] **P0.7**: Add authentication to /send_anomalies endpoint ✅ *Completed 2026-01-29*
  - **File**: [api/fathom/app.py](api/fathom/app.py:82-102)
  - **AC**: Endpoint requires @authenticate decorator
  - **Change**: Changed to POST method with @authenticate

- [x] **P0.8**: Add authentication to /cache_benchmarks endpoint ✅ *Completed 2026-01-29*
  - **File**: [api/fathom/app.py](api/fathom/app.py:104-107)
  - **AC**: Endpoint requires @authenticate decorator
  - **Change**: Changed to POST method with @authenticate

- [x] **P0.9**: Fix CORS to allow only specific origins ✅ *Completed 2026-01-29*
  - **File**: [api/fathom/app.py](api/fathom/app.py:31-32)
  - **AC**: CORS configured with explicit allowed origins
  - **Config**: Added `CORS_ORIGINS` to config.py, defaults to growthbenchmarks.com

- [ ] **P0.10**: Remove secrets from git history (DESTRUCTIVE) ⚠️ *MANUAL - Requires team coordination*
  - **Command**: `git filter-repo --path api/.env --invert-paths`
  - **AC**: Sensitive files removed from all commits
  - **Risk**: Requires force push, team coordination

- [ ] **P0.11**: Rotate all exposed credentials ⚠️ *MANUAL - Requires platform access*
  - **AC**: All API keys/secrets regenerated in respective platforms
  - **Notes**: Facebook, Google, Mailchimp, Postmark, Firebase

---

## Phase A: API Updates (Week 2-3)

**Goal**: Restore Meta and Google API connections with current versions
**Prerequisites**: P0 complete, Facebook recertification approved
**Risk Level**: MEDIUM - Breaking changes in new API versions

- [ ] **A.1**: Update Facebook API version to v21.0
  - **File**: [api/fathom/facebook/connector.py](api/fathom/facebook/connector.py:157)
  - **AC**: All Graph API calls use v21.0

- [ ] **A.2**: Update Facebook SDK in requirements.txt
  - **File**: [api/requirements.txt](api/requirements.txt)
  - **AC**: `facebook-business==21.0.0`

- [ ] **A.3**: Update attribution parameters for v21.0
  - **File**: [api/fathom/facebook/connector.py](api/fathom/facebook/connector.py:158-167)
  - **AC**: Uses `action_attribution_windows` instead of deprecated param

- [ ] **A.4**: Add rate limiting decorator
  - **File**: [api/fathom/facebook/connector.py](api/fathom/facebook/connector.py)
  - **AC**: Exponential backoff on rate limit errors

- [ ] **A.5**: Update Google Ads SDK to v24.0
  - **File**: [api/requirements.txt](api/requirements.txt)
  - **AC**: `google-ads==24.0.0`

- [ ] **A.6**: Update Google Ads connector for new SDK
  - **File**: [api/fathom/google/connector.py](api/fathom/google/connector.py)
  - **AC**: All Google Ads API calls work with new SDK

- [ ] **A.7**: Migrate react-google-login to @react-oauth/google
  - **File**: [src/Components/GoogleLogin.jsx](src/Components/GoogleLogin.jsx)
  - **AC**: Google OAuth uses new library

- [ ] **A.8**: Add token refresh mechanism for Facebook
  - **File**: [api/fathom/facebook/functions.py](api/fathom/facebook/functions.py)
  - **AC**: Long-lived tokens auto-refresh before expiry

- [ ] **A.9**: End-to-end connection testing
  - **AC**: Can login with FB/Google and fetch metrics
  - **Command**: Manual test in browser

---

## Phase B: Embeddable Reports + SEO (Week 4)

**Goal**: Enable benchmark embedding on Ladder site with SEO-friendly pages
**Prerequisites**: Phase A complete (connections working)
**Risk Level**: LOW

- [ ] **B.1**: Create EmbedBenchmark.jsx component
  - **File**: [src/Components/EmbedBenchmark.jsx](src/Components/EmbedBenchmark.jsx)
  - **AC**: Lightweight chart display without navigation

- [ ] **B.2**: Create embed.js SDK
  - **File**: [public/embed.js](public/embed.js)
  - **AC**: Third-party sites can embed with `GrowthBenchmarks.init()`

- [ ] **B.3**: Add embed API endpoint
  - **File**: [api/fathom/facebook/routes.py](api/fathom/facebook/routes.py)
  - **AC**: `GET /{provider}/{benchmark}/embed_data` returns minimal payload

- [ ] **B.4**: Add react-helmet for SEO meta tags
  - **File**: [src/Components/Benchmark.jsx](src/Components/Benchmark.jsx)
  - **AC**: Pages have proper title, description, canonical URL

- [ ] **B.5**: Add JSON-LD structured data
  - **File**: [src/Components/Benchmark.jsx](src/Components/Benchmark.jsx)
  - **AC**: Dataset schema markup for search engines

- [ ] **B.6**: Configure CORS for embed domains
  - **File**: [api/fathom/app.py](api/fathom/app.py)
  - **AC**: `try.ladder.io` can fetch embed data

---

## Phase C: 4-Step Signup Lead Flow (Week 5-6)

**Goal**: Replace Webflow with native React signup flow + Calendly
**Prerequisites**: Phase A complete
**Risk Level**: MEDIUM

- [ ] **C.1**: Create Signup directory structure
  - **AC**: `src/Components/Signup/` with all sub-components

- [ ] **C.2**: Implement SignupContext state management
  - **File**: [src/Components/Signup/SignupContext.jsx](src/Components/Signup/SignupContext.jsx)
  - **AC**: Multi-step flow state persisted to localStorage

- [ ] **C.3**: Implement Step1LeadCapture
  - **File**: [src/Components/Signup/Step1LeadCapture.jsx](src/Components/Signup/Step1LeadCapture.jsx)
  - **AC**: Email + name form creates lead in Firestore

- [ ] **C.4**: Add lead_capture API endpoint
  - **File**: [api/fathom/user/routes.py](api/fathom/user/routes.py)
  - **AC**: `POST /user/lead_capture` creates lead doc

- [ ] **C.5**: Implement Step2OAuthConnect
  - **File**: [src/Components/Signup/Step2OAuthConnect.jsx](src/Components/Signup/Step2OAuthConnect.jsx)
  - **AC**: Reuses existing FB/Google login, links to lead

- [ ] **C.6**: Implement Step3ReportView with gating
  - **File**: [src/Components/Signup/Step3ReportView.jsx](src/Components/Signup/Step3ReportView.jsx)
  - **AC**: Shows blurred/gated preview until booking complete

- [ ] **C.7**: Create GatedChart component
  - **File**: [src/Components/Signup/GatedChart.jsx](src/Components/Signup/GatedChart.jsx)
  - **AC**: Chart with blur overlay and CTA

- [ ] **C.8**: Implement Step4Booking with Calendly
  - **File**: [src/Components/Signup/Step4Booking.jsx](src/Components/Signup/Step4Booking.jsx)
  - **AC**: Calendly embed with prefilled user data

- [ ] **C.9**: Add booking webhook endpoint
  - **File**: [api/fathom/user/routes.py](api/fathom/user/routes.py)
  - **AC**: `POST /user/booking_webhook` updates lead status

- [ ] **C.10**: Add signup routes to App.jsx
  - **File**: [src/App.jsx](src/App.jsx)
  - **AC**: `/signup`, `/signup/connect`, `/signup/report`, `/signup/book`

---

## Phase D: AI-Powered Audit (Week 7-8)

**Goal**: Generate intelligent audit reports using Vertex AI/Gemini
**Prerequisites**: Phase A complete, GCP project created
**Risk Level**: MEDIUM - New infrastructure

- [ ] **D.1**: Create new GCP project
  - **AC**: Project created with billing enabled

- [ ] **D.2**: Enable Vertex AI API
  - **Command**: `gcloud services enable aiplatform.googleapis.com`
  - **AC**: API enabled and accessible

- [ ] **D.3**: Create service account for Vertex AI
  - **Command**: `gcloud iam service-accounts create vertex-ai-audit`
  - **AC**: Service account with aiplatform.user role

- [ ] **D.4**: Add AI dependencies to requirements.txt
  - **File**: [api/requirements.txt](api/requirements.txt)
  - **AC**: google-cloud-aiplatform, langchain, chromadb added

- [ ] **D.5**: Implement audit_rules.py
  - **File**: [api/fathom/lib/audit_rules.py](api/fathom/lib/audit_rules.py)
  - **AC**: Deterministic rules for CTR, CPA, creative fatigue detection

- [ ] **D.6**: Implement audit_llm.py
  - **File**: [api/fathom/lib/audit_llm.py](api/fathom/lib/audit_llm.py)
  - **AC**: Vertex AI/Gemini integration for narrative generation

- [ ] **D.7**: Implement audit_rag.py
  - **File**: [api/fathom/lib/audit_rag.py](api/fathom/lib/audit_rag.py)
  - **AC**: ChromaDB + embeddings for playbook retrieval

- [ ] **D.8**: Create playbook content for RAG
  - **AC**: Initial playbook docs derived from email templates

- [ ] **D.9**: Implement audit_pipeline.py
  - **File**: [api/fathom/lib/audit_pipeline.py](api/fathom/lib/audit_pipeline.py)
  - **AC**: Orchestrates rules → LLM → output generation

- [ ] **D.10**: Create audit API routes
  - **File**: [api/fathom/audit/routes.py](api/fathom/audit/routes.py)
  - **AC**: `POST /audit/generate`, `POST /audit/export/{format}`

---

## Phase E: Email Webhook (Week 9)

**Goal**: Automated audit delivery after booking
**Prerequisites**: Phase D complete
**Risk Level**: LOW

- [ ] **E.1**: Create generate_audit_report.py
  - **File**: [api/fathom/lib/generate_audit_report.py](api/fathom/lib/generate_audit_report.py)
  - **AC**: Aggregates metrics and generates report dict

- [ ] **E.2**: Create audit_report email template
  - **File**: [api/fathom/lib/email_templates/audit_report.py](api/fathom/lib/email_templates/audit_report.py)
  - **AC**: HTML email with performance summary

- [ ] **E.3**: Add trigger_audit endpoint
  - **File**: [api/fathom/user/routes.py](api/fathom/user/routes.py)
  - **AC**: `POST /user/trigger_audit` generates and sends email

- [ ] **E.4**: Add email delivery tracking
  - **File**: [api/fathom/user/routes.py](api/fathom/user/routes.py)
  - **AC**: Postmark webhook logs opens/clicks to Firestore

- [ ] **E.5**: Integration testing
  - **AC**: Full flow from booking → audit generation → email delivery

---

## Final Verification

- [ ] **F.1**: Security penetration testing
  - **AC**: No exposed secrets, all endpoints properly authenticated

- [ ] **F.2**: Performance testing
  - **AC**: API response times < 2s for main flows

- [ ] **F.3**: E2E user flow testing
  - **AC**: Complete signup → connect → report → booking flow works
