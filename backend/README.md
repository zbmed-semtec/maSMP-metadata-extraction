# Automated Metadata Extraction for Machine-Actionable Software Management Plan

This project focuses on extracting metadata from GitHub repositories to generate a **Machine-Actionable Software Management Plan (SMP)**.

This README is specifically for the **backend component**, which utilizes **FastAPI** to extract metadata.

## Metadata Extraction Process
Metadata extraction is performed in three layers:

1. **Extraction from GitHub API** – Fetch repository metadata directly from GitHub.
2. **Parsing Git Repository Files** – Analyze repository files for relevant metadata.
3. **Extracting External Information** – Retrieve additional metadata from external sources such as:
   - OpenAlex (https://openalex.org/)
   - Software Heritage Archive (https://www.softwareheritage.org/)
   - Wayback Machine (Internet Archive) (https://web.archive.org/)

## API Endpoint
### GET `/metadata` - Extract Metadata
Extract metadata from a code repository using a specified schema.

#### Request Parameters:
| Parameter      | Type   | Required | Description |
|---------------|--------|----------|-------------|
| `repo_url`    | string | Yes      | URL of the code repository to analyze |
| `schema`      | string | Yes      | Schema to use for metadata extraction (`maSMP` or `CODEMETA`) |
| `access_token` | string | No       | Access token for private repositories and to increase API rate limits |

#### Response:
Returns a JSON object (`MetadataResponse`) containing the analysis results.

## GitHub API Rate Limits
- Without an access token: **60 API calls per hour**
- With an access token: **5000 API calls per hour**
- Using an access token is **recommended** to avoid hitting rate limits, even for public repositories.

## How to Get a GitHub Access Token
1. Go to [GitHub Developer Settings](https://github.com/settings/tokens)
2. Click **"Generate new token"** (or **"Generate new token (classic)"** if using the old system)
3. Select **expiration** (optional, but recommended for security)
4. Enable the following scopes:
   - `repo` (if accessing private repositories)
   - `read:org` (if accessing organization repositories)
5. Click **"Generate token"**
6. Copy the token and store it securely (it won't be shown again!)

To use the token, include it in the request as the `access_token` parameter.

## Installation
Before starting, make sure you have **Conda** installed. If not, you can follow the official instructions to install it from [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).

### Steps to Set Up the Backend
1. **Navigate to the backend folder**:
   Ensure you're inside the `backend` directory of the project before proceeding with the setup.

   ```sh
   cd backend
   ```

2. **Create a virtual environment with Conda**: 
   If you don't have a Conda environment yet, create one using the following command:

   ```sh
   conda create --name maplan python=3.10
   ```

3. **Activate the environment**: 
   Once the environment is created, activate it using the following command:

   ```sh
   conda activate maplan
   ```

4. **Install dependencies**: 
   Use pip to install the necessary dependencies:

   ```sh
   pip install -r requirements.txt
   ```

## Usage
```sh
# Run the FastAPI application
uvicorn main:app --reload
```

### Access the API Documentation:
Once running, visit:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---
This backend service enables automated metadata extraction for software repositories, providing a structured approach to metadata collection and software management planning.

