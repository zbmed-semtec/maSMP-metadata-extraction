# Automated Metadata Extraction for Machine-Actionable Software Management Plan

This project focuses on extracting metadata from GitHub repositories to generate a **Machine-Actionable Software Management Plan (SMP)**.

# Running the FastAPI Application with Docker

This guide explains how to build and run the FastAPI application using Docker.

## Prerequisites
Ensure you have the following installed on your system:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Steps to Run the FastAPI Application

### 1. Build the Docker Image
Navigate to the root directory of your project and run:
```sh
docker-compose build
```
This will build the Docker image using the `Dockerfile` located inside the `backend/` directory.

### 2. Run the Application
Start the FastAPI application as a Docker container:
```sh
docker-compose up -d
```
The `-d` flag runs the container in detached mode.

### 3. Access the API
Once the container is running, you can access the API at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 4. Stopping the Container
To stop the running container, execute:
```sh
docker-compose down
```

### 5. Checking Logs
To view the logs of the running container, use:
```sh
docker-compose logs -f
```

## Notes
- The application runs on port `8000` inside the container and is mapped to the same port on the host.
- Any changes to the code will require rebuilding the Docker image if not using volume mounts.

This setup ensures that the FastAPI application is containerized and easily deployable. 🚀

