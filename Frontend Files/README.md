# Guard Rupee Investigation Center

A frontend-only financial intelligence platform for fraud detection, money-flow tracing, and connected-entity investigation. The experience uses the supplied Guard Rupee visual identity throughout the landing, access gateway, and investigator workspace.

## Start the application

```bash
npm install
npm run dev
```

Then open the local URL printed by Vite. Any non-empty username and password work in mock mode.

To create a production build:

```bash
npm run build
```

## Editable project identity

Change the project name, short name, tagline, and landing description in:

`src/app/config.ts`

These values are intentionally placeholders so the team can replace them without hunting through UI files.

## Environment

Copy `.env.example` to `.env` and set the values below.

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_ENABLE_MOCK_DATA=true
```

When `VITE_ENABLE_MOCK_DATA=true`, feature APIs return local realistic sample data. Set it to `false` once the backend is ready. The API files will then delegate to the central client at `src/services/api/client.ts`.

## Tech stack

- React + TypeScript + Vite
- React Router for route protection and navigation
- TanStack React Query for server-state hooks
- Recharts for dashboard visualization
- Lucide React for accessible interface icons
- Modern CSS design system, no heavyweight UI framework

## Architecture

```text
src/
  app/              app configuration, providers and routing
  assets/logo/      supplied Guard Rupee source asset
  features/         feature-owned pages, UI, API, hooks and contracts
    landing/         cinematic entry experience and network sphere
    auth/            mock authentication boundary and login
    dashboard/       KPI data and command-center charts
    transactions/    explorer and transaction detail records
    investigations/ graph workspace and evidence timeline
    entities/        connected-party profile
    alerts/          prioritized fraud signals
    reports/         report builder and export placeholders
  shared/           reusable layout, visual states, status UI and logo
  services/api/     central HTTP client and error helpers
  styles/           global tokens, layout and animations
  types/            application data contracts
```

Each screen reads through this chain:

```text
Page / component → feature hook → feature API → API client → backend
```

No visual component calls `fetch` directly. Backend handoff points are marked with `// BACKEND TODO` in the API layer.

## Routes

| Route | Purpose |
| --- | --- |
| `/` | Landing page and animated Guard Rupee network experience |
| `/login` | Mock investigator access gateway |
| `/dashboard` | KPI and fraud-monitoring command center |
| `/transactions` | Searchable transaction explorer |
| `/transactions/:id` | Funds movement, risk and related records |
| `/investigations/:id` | Pannable / zoomable intelligence network workspace |
| `/entities/:id` | Entity profile and associated relationships |
| `/alerts` | Security-alert monitoring interface |
| `/reports` | Report configuration and export placeholders |

Application routes are protected. A signed-in mock investigator is stored in local storage and can be signed out from the sidebar.

## Backend integration

1. Implement each endpoint in the feature API files, using the existing types in `src/types/common.ts`.
2. Set `VITE_ENABLE_MOCK_DATA=false` in `.env`.
3. Set `VITE_API_BASE_URL` to the deployed API base URL.
4. Replace `features/auth/api.ts` mock authentication with the real token/session flow.
5. Keep response mapping in the feature API files so the pages and UI do not need to be rewritten.

The report action and CSV/PDF controls are intentionally frontend placeholders until the corresponding backend services exist.
