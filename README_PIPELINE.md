# README: Generic README Property Extraction Pipeline

This document explains the structure, functions, and pipeline of the generic_readme_property_orchestration.ipynb notebook, which is designed to extract structured metadata from repository READMEs using a combination of heuristics and large language models (LLMs).

## Overview

The pipeline automates the extraction of key repository properties (such as license, installation instructions, contact, contributors, links, and description) from public repositories (GitHub/GitLab) by fetching their README files, chunking and indexing the content, and applying both rule-based and LLM-based extraction methods.

---

## Pipeline Structure

### 1. **Configuration Loading**
- Loads settings from `config.yaml` (model, provider, repositories, properties to extract, etc.).
- Determines the active model and provider (e.g., vLLM, Ollama) and sets up extraction parameters.

### 2. **Repository Processing**
- For each enabled repository:
  - **URL Parsing:** Extracts provider, owner, and repo name from the repository URL.
  - **README Fetching:** Attempts to download the README from common branches and filenames.
  - **Section Splitting:** Splits README into sections based on headings (Markdown or reStructuredText).
  - **Chunking:** Large sections are further split into overlapping text chunks for better retrieval.
  - **Chunk Record Preparation:** Each chunk is normalized into a record with heading, content, and metadata.
  - **Retrieval Index Building:** Optionally builds an embedding index (if `sentence-transformers` is available) for semantic search; otherwise, uses lexical (keyword) search.

### 3. **Property Extraction**
- For each property (e.g., license, installation):
  - **Heuristic Extraction:** For some properties (license, contributors, links), applies regex and pattern-based extraction directly from the README.
  - **Chunk Retrieval:** For other properties, retrieves the most relevant chunks using hybrid semantic and lexical scoring.
  - **Prompt Construction:** Builds a strict prompt for the LLM, including context and extraction rules.
  - **LLM Query:** Sends the prompt to the configured LLM backend and parses the JSON response.
  - **Result Aggregation:** Collects the extracted value, evidence, and confidence for each property.

### 4. **Result Saving**
- Aggregates all results and saves them to `generic_extraction_results.json`.

---

## Key Functions and Their Roles

### Configuration and Setup
- **CONFIG_PATH, CONFIG, MODEL, PROVIDER, etc.:** Load and store configuration settings.

### Repository Utilities
- **parse_repo_url:** Parses a repository URL into provider, owner, and repo name.
- **candidate_readme_urls:** Generates possible raw README URLs for a repo.
- **fetch_readme:** Downloads the README from the first reachable candidate URL.

### Text Processing
- **split_with_metadata:** Splits markdown text into sections, preserving heading metadata.
- **hybrid_chunking:** Splits large sections into overlapping text chunks.
- **prepare_chunk_records:** Normalizes chunk dictionaries for retrieval.

### Indexing and Retrieval
- **build_retrieval_index:** Builds a retrieval index with optional embeddings for semantic search.
- **keyword_score:** Computes lexical relevance score for a chunk.
- **retrieve_top_chunks:** Retrieves top relevant chunks for a property using hybrid scoring.

### Extraction Heuristics
- **extract_license_from_readme:** Detects SPDX-style license and evidence from README.
- **extract_contributors_from_text:** Extracts contributor names and GitHub URLs.
- **extract_links_from_text:** Extracts links, categorizes relevance, and optionally checks link health.

### LLM Interaction
- **check_provider_ready:** Checks if the LLM backend and model are available.
- **run_llm:** Sends a prompt to the LLM backend and returns the response.
- **extract_json:** Parses and normalizes JSON from model output.

### Orchestration
- **build_prompt:** Constructs a strict prompt for property extraction.
- **extract_property:** Orchestrates extraction for a single property (heuristics + LLM fallback).
- **process_repository:** Runs the full pipeline for a single repository.
- **timed_call:** Utility to time function calls.
- **run_property_test:** Helper for testing extraction of a single property.

---

## Key Factors and Design Choices

- **Hybrid Extraction:** Combines fast heuristics for simple properties with LLM-based extraction for complex or ambiguous cases.
- **Chunked Context:** Uses chunked README sections to provide focused, relevant context to the LLM, improving extraction accuracy.
- **Strict Prompting:** Prompts instruct the LLM to return only JSON with value, evidence, and confidence, ensuring structured outputs.
- **Extensibility:** New properties or extraction rules can be added by updating the configuration and property-specific logic.
- **Error Handling:** Catches and reports errors for each property extraction, ensuring robustness.
- **Semantic Search (Optional):** If `sentence-transformers` is available, enables semantic chunk retrieval for better LLM context.

---

## Example Output Structure

Each repository's extraction result includes:
```json
{
  "repo_url": "...",
  "readme_url": "...",
  "properties": {
    "license": {"value": "MIT", "evidence": "...", "confidence": 0.98},
    "installation": {"value": "pip install ...", "evidence": "...", "confidence": 0.9},
    ...
  }
}
```

---

## Usage
- Configure repositories and model settings in `config.yaml`.
- Run the notebook to extract properties for all enabled repositories.
- Use the single-property test cells to debug or validate extraction for specific properties.
- Results are saved to `generic_extraction_results.json`.

---

## Extending the Pipeline
- Add new properties to the `properties` list in `config.yaml` and update `PROPERTY_QUERIES`, `PROPERTY_SCHEMA_HINTS`, and `PROPERTY_RULES` as needed.
- Implement new heuristic extraction functions for additional property types.
- Adjust chunking or retrieval logic for different README formats or languages.

---

## Contact
For questions or contributions, see the repository's contact property or open an issue.
