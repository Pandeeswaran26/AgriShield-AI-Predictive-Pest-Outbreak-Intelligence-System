# AgriShield AI — Frontend

React (Vite) + Tailwind frontend for the AgriShield AI pest-prediction backend.

## Setup

```bash
npm install
```

Set your backend URL in `.env` (defaults to `http://localhost:8000`):

```
VITE_API_BASE_URL=http://localhost:8000
```

Run the dev server:

```bash
npm run dev
```

Build for production:

```bash
npm run build
```

## Structure

- `src/services/*.js` — one Axios module per backend router (auth, predict, history,
  dashboard, analytics, recommendation, assistant, weather). All requests attach the
  stored JWT automatically; a 401 clears the session and redirects to `/login`.
- `src/context/AuthContext.jsx` — session state, backed by `localStorage` +
  `GET /auth/me` on load to confirm the token is still valid.
- `src/pages/` — Landing, Login, Register (with OTP verification), Dashboard,
  Predict, Recommendation, History, Analytics, Assistant, Settings.
- `src/layouts/` — `PublicLayout` (marketing navbar) and `DashboardLayout`
  (sidebar nav) — routes are split accordingly in `App.jsx`.

## Notes

- The `/predict` endpoint returns a `prediction_id`, which the Predict page uses to
  link straight to that prediction's recommendation and PDF report.
- The Recommendation page can also be reached without a `?id=` param — it lets you
  pick any past prediction from a dropdown backed by `/history`.
- Settings currently shows read-only account info (no `PATCH /auth/me` exists on the
  backend yet) plus a client-side dark-mode toggle and logout.
