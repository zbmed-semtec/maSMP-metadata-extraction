# CoMET-RS Setup Guide

This README provides step-by-step instructions to install dependencies, configure the environment, and run both the frontend and backend services.

---

## Installing Node Version Manager (NVM)

### Bash Install NVM

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

### Source the terminal

```bash
source ~/.bashrc
```

---

## Install Node.js

### Install Node v20.20.0

```bash
nvm install 20.20.0
nvm use 20.20.0
```

### Set npm version to 10.8.2

```bash
npm install -g npm@10.8.2
```

### Verify versions

```bash
node -v
npm -v
```

---

## Frontend Setup

### Install dependencies

```bash
cd ~/maSMP-metadata-extraction/frontend-migration
npm install
```

---

## Environment Configuration

### Configure API URL

```bash
cp .env.example .env
```

Then edit `.env` and set:

```env
API_BASE_URL=http://127.0.0.1:8000
```

> Default is already `http://127.0.0.1:8000`, which matches your backend on port 8000.

---

## Start the Frontend Dev Server

```bash
npm run dev
```

The app will be available at:

```
http://localhost:3000
```

---

## Backend Setup (Separate Terminal)

```bash
cd ~/maSMP-metadata-extraction/backend-migration
uvicorn app.main:app --reload --host 127.0.0.1 --port 9000
```

---

## Frontend Run Command (Separate Terminal)

```bash
cd ~/maSMP-metadata-extraction/frontend-migration
npm install
npm run dev
```

---

## Notes

* Frontend runs on: **[http://localhost:3000](http://localhost:3000)**
* Backend runs on: **[http://127.0.0.1:9000](http://127.0.0.1:9000)**
* API base URL configured to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## Project Structure

```
maSMP-metadata-extraction/
├── backend-migration/
└── frontend-migration/
```
