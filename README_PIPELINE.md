# README: Generic README Property Extraction Pipeline

This document explains the structure, functions, and pipeline of the generic_readme_property_orchestration.ipynb notebook, which is designed to extract structured metadata from repository READMEs using a combination of heuristics and large language models (LLMs).

## Overview

The pipeline automates the extraction of key repository properties (such as license, installation instructions, contact, contributors, links, and description) from public repositories (GitHub/GitLab) by fetching their README files, chunking and indexing the content, and applying both rule-based and LLM-based extraction methods.

The notebook has also been extended with stronger property-specific rules, link health checks, runtime model resolution, and single-property smoke tests so the extraction flow is easier to validate and tune.

## Additional Changes in the Notebook

- Property-specific configuration is centralized through `PROPERTY_QUERIES`, `PROPERTY_SCHEMA_HINTS`, and `PROPERTY_RULES` so each target field has its own search terms, expected JSON shape, and prompt guidance.
- `extract_property` now short-circuits high-confidence heuristics for `license`, `contributors`, and `links` before falling back to the LLM.
- Link extraction now filters low-signal or noisy URLs, prioritizes paper/docs/repo/tutorial links, and can optionally validate URL health with HTTP status checks.
- The notebook includes helper cells for selecting enabled repositories and resolving the active runtime model from `config.yaml`.
- `timed_call` and `run_property_test` make it easy to benchmark and debug one property at a time.
- The final notebook cells provide property smoke tests for `license`, `installation`, `contact`, `contributors`, `links`, and `description`.

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
- **PROPERTY_QUERIES:** Keyword sets used to rank chunks for each property.
- **PROPERTY_SCHEMA_HINTS:** Expected output shape for each property.
- **PROPERTY_RULES:** Prompt-level rules that constrain the model response.

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
- **check_url_health:** Verifies whether a URL is reachable and returns its HTTP status code.

### LLM Interaction
- **check_provider_ready:** Checks if the LLM backend and model are available.
- **run_llm:** Sends a prompt to the LLM backend and returns the response.
- **extract_json:** Parses and normalizes JSON from model output.

### Orchestration
- **build_prompt:** Constructs a strict prompt for property extraction.
- **extract_property:** Orchestrates extraction for a single property (heuristics + LLM fallback).
- **process_repository:** Runs the full pipeline for a single repository.
- **print_property_summary:** Prints a cross-repository confidence and ranking summary.
- **timed_call:** Utility to time function calls.
- **resolve_selected_repos_from_config:** Resolves the enabled repositories to process from config.
- **resolve_runtime_model_from_config:** Resolves the active provider, model, and base URL at runtime.
- **run_property_test:** Helper for testing extraction of a single property.

---

## Key Factors and Design Choices

- **Hybrid Extraction:** Combines fast heuristics for simple properties with LLM-based extraction for complex or ambiguous cases.
- **Chunked Context:** Uses chunked README sections to provide focused, relevant context to the LLM, improving extraction accuracy.
- **Strict Prompting:** Prompts instruct the LLM to return only JSON with value, evidence, and confidence, ensuring structured outputs.
- **Property-Aware Rules:** The README extraction logic now tailors behavior per field, especially for license, contributors, links, and description.
- **Link Quality Filtering:** Extracted links are de-duplicated, cleaned, and filtered before being returned to reduce noise in the output.
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

## Local LLM and model setup

- The pipeline consults `maSMP-metadata-extraction/config.yaml` for the active model and backend. Set `active_model: deepseek_vllm` to use the local vLLM service defined in the config.
- Recommended vLLM command (runs model on port 8001):

```bash
vllm serve "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B" --dtype bfloat16 --port 8001 --max-model-len 32768
```

- If you run vLLM on a different port (e.g., 8000 default), update `models.deepseek_vllm.base_url` in `config.yaml` to match (e.g., `http://localhost:8000`).
- Ollama alternative: the config also contains a `deepseek` entry (provider `ollama`) — if you prefer Ollama, ensure its API is reachable at `models.deepseek.base_url`.

## Running the pipeline (notebook)

- Ensure environment tokens are set when processing private repos:

```bash
export GITHUB_TOKEN=ghp_...
export GITLAB_TOKEN=glpat_...
```

- Start the notebook server and open `generic_readme_property_orchestration.ipynb`, then run the cells. The notebook will use the `active_model` from `config.yaml` to call the running LLM backend.

- If you prefer a script/CLI, use the package CLI (when installed):

```bash
comet-rs extract https://github.com/owner/repo maSMP --with-enrichment
```

---

## Extending the Pipeline
- Add new properties to the `properties` list in `config.yaml` and update `PROPERTY_QUERIES`, `PROPERTY_SCHEMA_HINTS`, and `PROPERTY_RULES` as needed.
- Implement new heuristic extraction functions for additional property types.
- Adjust chunking or retrieval logic for different README formats or languages.

---

## Contact
For questions or contributions, see the repository's contact property or open an issue.
