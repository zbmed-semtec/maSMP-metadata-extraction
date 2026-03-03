# CoMET-RS Frontend (Nuxt 3)

This is the **CoMET-RS** web UI for running metadata extraction against the maSMP backend. It is a Nuxt 3 + Tailwind CSS application that talks to the `backend-migration` FastAPI service.

---

## Prerequisites

- **Node.js** ≥ 18 (last tested with Node v20.20.0)
- **npm** (last tested with npm v10.8.2)
- The **backend** running locally (from `backend-migration`), typically on `http://127.0.0.1:8000`

Backend quick reminder:

```bash
cd backend-migration
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 1. Install dependencies

From the repo root or directly in this folder:

```bash
cd frontend-migration

# npm
npm install

# pnpm
pnpm install

# yarn
yarn install

# bun
bun install
```

---

## 2. Configure API base URL (optional)

By default the frontend expects the backend at:

```ts
// nuxt.config.ts
runtimeConfig: {
  public: {
    apiBase: process.env.API_BASE_URL || 'http://127.0.0.1:8000'
  }
}
```

If your backend runs on a **different host/port**, set `API_BASE_URL` before starting Nuxt:

```bash
export API_BASE_URL="http://localhost:9000"  # example
```

If you are running the backend from `backend-migration` on port `8000` as above, you do **not** need to set this; the default works.

You can also use a `.env` file (e.g. copy from `.env.example`) and set:

```env
API_BASE_URL=http://127.0.0.1:8000
```

---

## 3. Run the development server

Start the Nuxt dev server with hot-reload:

```bash
cd frontend-migration

# npm
npm run dev

# pnpm
pnpm dev

# yarn
yarn dev

# bun
bun run dev
```

By default this serves the app on **http://localhost:3000**. You can change the port if needed:

```bash
npm run dev -- --port 8080
```

Make sure:
- Backend is running on `http://127.0.0.1:8000` (or the URL in `API_BASE_URL`)
- Frontend dev server is running on `http://localhost:3000` (or your chosen port)

---

## 4. Production build & preview

Build an optimized production bundle:

```bash
cd frontend-migration

# npm
npm run build

# pnpm
pnpm build

# yarn
yarn build

# bun
bun run build
```

Preview the production build locally:

```bash
# npm
npm run preview

# pnpm
pnpm preview

# yarn
yarn preview

# bun
bun run preview
```

By default this also serves on port **3000** (use `--port` to change it).

Check out the [Nuxt deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.

---

## 5. Project structure

Key paths:

- `app/pages/dashboard.vue` – main dashboard page (form + results)
- `components/atoms`, `components/molecules`, `components/organisms` – UI components
- `composables/useApi.ts` – API client and streaming extraction logic
- `nuxt.config.ts` – Nuxt configuration, runtime config (`API_BASE_URL`), Tailwind, Pinia

---

## 6. Troubleshooting

- **“Extraction failed” or no results**  
  Check that the backend from `backend-migration` is running and reachable from the browser at the URL in `API_BASE_URL` (default `http://127.0.0.1:8000`).

- **CORS errors in the browser console**  
  Ensure you are using the backend’s public host/port in `API_BASE_URL` and that the backend is listening on `0.0.0.0` (as in the example `uvicorn` command).

- **Port already in use**  
  Run Nuxt on a different port, e.g. `npm run dev -- --port 8080`.
