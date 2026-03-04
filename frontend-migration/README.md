# CoMET-RS Frontend (Nuxt 3)

This is the **CoMET-RS** web UI for running metadata extraction against the maSMP backend. It is a Nuxt 3 + Tailwind CSS application that talks to the `backend` FastAPI service.

---

## Prerequisites

- **Node.js** v20.20.0
- **npm** v10.8.2
- The **backend** running locally (from `backend`), typically on `http://127.0.0.1:8000`

---

## Installation & Setup

### 1. Install Node Version Manager (NVM)

Install NVM using the official installation script:

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

### 2. Source the terminal

```bash
source ~/.bashrc
```

### 3. Install Node v20.20.0

```bash
nvm install 20.20.0
nvm use 20.20.0
```

### 4. Set npm version to 10.8.2

```bash
npm install -g npm@10.8.2
```

### 5. Verify versions

```bash
node -v
npm -v
```

### 6. Install dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd /home/lil-e-va/zb_med/maSMP-metadata-extraction/frontend-migration
npm install
```

---

## Configure API URL

The default API base URL is already set to `http://127.0.0.1:8000`, which matches the backend running on port 8000.

If you need to change it, you can create a `.env` file:

```bash
cp .env.example .env
```

Then set in `.env`:

```env
API_BASE_URL=http://127.0.0.1:8000
```

---

## Running the Application

### Start the frontend development server

```bash
cd /home/lil-e-va/zb_med/maSMP-metadata-extraction/frontend-migration
npm run dev
```

The app will be available at **http://localhost:3000**.

### Start the backend (in a separate terminal)

```bash
cd /home/lil-e-va/zb_med/maSMP-metadata-extraction/backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Make sure both services are running:

- Backend running on `http://127.0.0.1:8000`
- Frontend dev server running on `http://localhost:3000`

---

## Project structure

Key paths:

- `app/pages/dashboard.vue` – main dashboard page (form + results)
- `components/atoms`, `components/molecules`, `components/organisms` – UI components
- `composables/useApi.ts` – API client and streaming extraction logic
- `nuxt.config.ts` – Nuxt configuration, runtime config (`API_BASE_URL`), Tailwind, Pinia

---

## Troubleshooting

- **"Extraction failed" or no results**
  Check that the `backend-migration` is running and reachable from the browser at the URL in `API_BASE_URL` (default `http://127.0.0.1:8000`).
- **CORS errors in the browser console**
  Ensure you are using the backend's public host/port in `API_BASE_URL` and that the backend is listening on the correct address.
- **Port already in use**
  Run Nuxt on a different port, e.g. `npm run dev -- --port 8080`.
- **Node modules or Nuxt compilation errors**
  If you encounter issues with Node modules or Nuxt failing to start, try the following steps:

  ```bash
  # Clear Node modules and reinstall
  rm -rf node_modules .nuxt
  npm install

  # Try running dev server again
  npm run dev
  ```
  If the issue persists, ensure you are using the correct Node and npm versions:

  ```bash
  node -v  # should be v20.20.0
  npm -v   # should be v10.8.2
  ```
  If versions don't match, use NVM to switch:

  ```bash
  nvm use 20.20.0
  ```
