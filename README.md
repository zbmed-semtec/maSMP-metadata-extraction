# Automated Metadata Extraction for Machine-Actionable Software Management Plan

This project is designed to automate the extraction of metadata from GitHub repositories to generate a **Machine-Actionable Software Management Plan (SMP)**. It consists of two main components:

1. **Backend** - A FastAPI-based service that extracts metadata from GitHub and external sources.
2. **Frontend** - A Vue 3 application providing a user-friendly interface to interact with the backend.

---

## Setting Up and Running the Project

### 1. Running Backend Service
The backend service is responsible for fetching and processing metadata from GitHub repositories and external sources. Follow the instructions in the [Backend README](./backend/README.md) to install and run the backend server.

### 2. Running Frontend Application
The frontend application provides a web interface for users to input repository details and view extracted metadata. Follow the steps in the [Frontend README](./frontend/README.md) to set up and start the frontend application.

---

## Running the Project with Docker
To simplify deployment, you can use **Docker** and **Docker Compose** to run the entire project (Nuxt frontend + FastAPI backend from `frontend-migration` and `backend-migration`).

### 1. Install Docker
Ensure you have Docker installed on your system. You can download and install it from [Docker’s official website](https://www.docker.com/get-started).

### 2. Build and Run the Containers
From the project root, build and start both services:

```sh
docker compose up --build
```

This will:
- Build and start the **backend** (FastAPI) and **frontend** (Nuxt) containers.
- Set up networking so the frontend can call the backend API.

### 3. Access the Application
Once the containers are running:
- **Frontend UI:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8001](http://localhost:8001)
- **API docs (Swagger):** [http://localhost:8001/docs](http://localhost:8001/docs)

### 4. Stopping the Containers
To stop the running containers:

```sh
docker compose down
```

This shuts down and removes the containers but keeps the built images.

---

## Contributing
If you want to contribute to this project, feel free to fork the repository, create a new branch, and submit a pull request with your changes.

## License
This project is licensed under the MIT License.

