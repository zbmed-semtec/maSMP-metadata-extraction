# Automated Metadata Extraction for Machine-Actionable Software Management Plan

This project focuses on extracting metadata from GitHub repositories to generate a **Machine-Actionable Software Management Plan (SMP)**.

This README is specifically for the **frontend component**, which utilizes **Vue 3** for the user interface.

## Prerequisites
Before running the frontend, ensure the **backend service is up and running**. Follow the instructions in the [Backend README](../backend/README.md) to set up and start the backend server.

## Project Setup
To set up and run the frontend, follow these steps:

### 1. Navigate to the frontend folder
Ensure you're inside the `frontend` directory of the project before proceeding with the setup.

   ```sh
   cd frontend
   ```

### 2. Install Dependencies
Make sure you have **Node.js** installed. Then, run the following command to install the required dependencies:

```sh
npm install
```

### 3. Start the Development Server
To start the development server with hot-reloading:

```sh
npm run serve
```

## Configuration
By default, the frontend is configured to communicate with the backend running at `http://127.0.0.1:8000`. If your backend is running on a different URL, update the API endpoint in the `.env` file.

## Accessing the UI
Once the frontend is running, open your browser and go to:

```
http://localhost:8080
```

## Features
- User-friendly UI for entering repository details
- Calls backend API to extract metadata
- Displays extracted metadata in a structured format



