# GrowthBenchmarks - Claude Code Instructions

## Required Reading Before Implementation

**IMPORTANT**: Before making any code changes, read these documents:

1. **Design Patterns** - `claudedocs/DESIGN_PATTERNS.md`
   - Backend patterns (connectors, decorators, routes)
   - Frontend patterns (components, Firebase, data fetching)
   - Anti-patterns to avoid

2. **Project Revival Plan** - `claudedocs/todos/2026-01-23-project-zeus-revival.md`
   - Phased implementation roadmap
   - Security priorities (P0)
   - Task acceptance criteria

## Project Overview

**GrowthBenchmarks.com** - Advertising benchmark comparison tool for Facebook and Google Ads

### Tech Stack
- **Frontend**: React 17, Bootstrap 4, D3.js, Firebase Auth
- **Backend**: Python Flask, deployed to `api.growthbenchmarks.com`
- **Database**: Firebase Firestore
- **Hosting**: Firebase Hosting (client), Google Cloud Run (API)

### Key Commands
```bash
# Development
npm start              # Run React client (HTTPS)
npm run server         # Run Flask API via Docker
npm run cache          # Cache benchmark data for build

# Deployment
npm run deploy         # Deploy client to Firebase
cd api && ./deploy.sh  # Deploy API to Cloud Run
```

## Architecture Rules

### Backend (api/fathom/)

1. **Routes**: Always use domain blueprints, never add routes to `app.py`
   - `facebook/routes.py` - Facebook endpoints
   - `google/routes.py` - Google Ads endpoints
   - `user/routes.py` - User management

2. **Authentication**: ALL user-data endpoints MUST use `@authenticate` decorator
   ```python
   from fathom.lib.decor_authenticate import authenticate

   @blueprint.route('/protected')
   @authenticate
   def protected_endpoint():
       pass
   ```

3. **Connectors**: Extend `ConnectorBase` for new API integrations
   - Location: `components/connectors_base_class/`

4. **Database**: Use Firestore wrapper, never raw Firebase calls
   - Location: `components/firestore_wrapper/`

### Frontend (src/Components/)

1. **Firebase**: Always import from `./Firebase.js`, never directly
2. **API Calls**: Use `myFetch.js` wrapper for authenticated requests
3. **New Components**:
   - Phase C+ should use domain subdirectories (see DESIGN_PATTERNS.md)
   - Current flat structure is legacy

## Security Requirements

**Critical** - These MUST be followed:

- [ ] No hardcoded API keys or secrets in source code
- [ ] All credentials in environment variables
- [ ] `@authenticate` on all data-access endpoints
- [ ] CORS configured for specific origins only
- [ ] Never commit `.env` files

## Current Priorities (Project Zeus)

| Phase | Focus | Status |
|-------|-------|--------|
| P0 | Security & Compliance | **BLOCKING** |
| A | API Updates (FB v21, Google v24) | Pending |
| B | Embeddable Reports + SEO | Pending |
| C | 4-Step Signup Flow | Pending |
| D | AI-Powered Audit | Pending |
| E | Email Webhook | Pending |

## File Organization

```
api/
├── fathom/
│   ├── facebook/      # Facebook connector & routes
│   ├── google/        # Google Ads connector & routes
│   ├── user/          # User management
│   ├── components/    # Base classes & wrappers
│   ├── lib/           # Utilities & decorators
│   └── app.py         # Flask app entry (routes registered here)

src/
├── Components/        # React components (flat, legacy)
├── App.jsx           # Main router
└── config.js         # Client configuration

claudedocs/
├── DESIGN_PATTERNS.md # Architecture patterns
└── todos/            # Task tracking
```

## Testing

```bash
# Backend
cd api && pytest

# Frontend
npm test
```

## Before Committing

1. Ensure no secrets in code (`grep -r "api_key\|secret\|password" --include="*.py" --include="*.js"`)
2. Run linting if available
3. Test affected endpoints manually
4. Update DESIGN_PATTERNS.md if introducing new patterns
