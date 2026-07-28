# AgriShield AI — Frontend

Production React frontend for the AgriShield AI pest-outbreak prediction
system. Talks to a separately-hosted FastAPI backend (Extra Trees model +
SHAP) — no backend code lives here.

## Stack

React 19 · Vite · Tailwind CSS · React Router · Axios · Framer Motion ·
Recharts · Lucide React · React Hook Form · React Hot Toast

## Getting started

```bash
npm install
cp .env.example .env   # point VITE_API_BASE_URL at your FastAPI backend
npm run dev
```

The dev server proxies `/api/*` to `http://localhost:8000` (see
`vite.config.js`), so if your FastAPI backend runs there you don't need to
set `VITE_API_BASE_URL` at all in development.

```bash
npm run build      # production build to dist/
npm run preview    # preview the production build locally
```

## Project structure

```
src/
  api/               -> re-exported service functions (see services/)
  components/
    common/          -> AssistantWidget, ProtectedRoute
    dashboard/       -> StatCard
    layout/          -> Navbar, Footer, Sidebar, Topbar
    prediction/      -> RiskMeter
  context/           -> ThemeContext (dark mode), AuthContext
  hooks/             -> useDebounce
  layouts/           -> MainLayout (public), DashboardLayout (app shell)
  pages/             -> one file per route
  services/          -> Axios calls, grouped by domain (api.js is the base instance)
  utils/             -> risk.js (risk color/badge/format helpers)
```

## Pages implemented

| Route | Page |
|---|---|
| `/` | Landing page |
| `/login` | Farmer / Admin login |
| `/register` | Registration |
| `/dashboard` | Summary cards + trend/weather/monthly/crop charts |
| `/predict` | Prediction form + risk meter result |
| `/recommendation?predictionId=` | Actions, prevention, pesticides, yield impact |
| `/history` | Search, filter, sort, CSV export, pagination |
| `/analytics` | Trend, crop, weather-impact, location, risk-distribution charts |
| `/settings` | Profile, theme, notifications, language |

The floating AI Assistant is available on every authenticated page
(`DashboardLayout`), backed by `services/assistantService.js`.

## Backend contract

Every service file documents the endpoint shape it expects. The prediction
payload field names mirror the columns the ExtraTreesRegressor was trained
on (`train_final_model.py`): `crop`, `pest_name`, `location`,
`observation_year`, `standard_week`, `max_temperature`, `min_temperature`,
`humidity_1`, `humidity_2`, `rainfall`, `wind_speed`, `sunshine_hours`,
`evaporation`. Adjust `services/*.js` if your FastAPI route paths or field
names differ.
