# comet-rs

CLI and Python library for extracting **maSMP** / **CODEMETA** metadata (plus per‑property sources and confidence) from GitHub and GitLab repositories.

Given a repository URL, `comet-rs`:

- Calls the platform API (GitHub / GitLab)
- Parses files like `CITATION.cff`, `LICENSE`, and `README.md`
- Optionally enriches with external services (OpenAlex, archives)
- Builds a maSMP or CODEMETA JSON‑LD document
- Tracks, for each property, **which source set it** and with what **confidence**

---

## Installation

```bash
pip install comet-rs
```

Python 3.10+ is required.

---

## CLI usage

### Extract full metadata

```bash
comet-rs extract https://github.com/KnowledgeCaptureAndDiscovery/somef maSMP --with-enrichment
```

Outputs JSON with:

- `schema`: `maSMP` or `CODEMETA`
- `code_url`: repository URL
- `results`: JSON‑LD document
- `enriched_metadata`: per‑property source / confidence / category (for maSMP)

### Extract a single property (value + source)

```bash
comet-rs extract_property https://github.com/KnowledgeCaptureAndDiscovery/somef author
```

Example output:

```json
{
  "property_name": "author",
  "property_value": [
    {
      "@type": "Person",
      "familyName": "Garijo",
      "givenName": "Daniel",
      "@id": "https://orcid.org/0000-0003-0454-7145"
    }
  ],
  "source": "citation_cff",
  "confidence": 0.93
}
```

By default, `extract_property` uses the **maSMP** schema. To use CODEMETA:

```bash
comet-rs extract_property https://github.com/owner/repo name --schema CODEMETA
```

---

## Authentication & rate limits

For public repositories you can often run without a token, but GitHub and GitLab apply rate limits. For heavier use or private repos, set:

```bash
export GITHUB_TOKEN=ghp_...      # for github.com URLs
export GITLAB_TOKEN=glpat_...    # for gitlab.com URLs
```

`comet-rs` automatically picks the right token based on the repository URL, or you can pass `--token` explicitly:

```bash
comet-rs extract https://gitlab.com/owner/repo maSMP --token glpat_...
```

Tokens only need minimal read scopes (`repo` / `read:org` on GitHub, `read_api` / `read_repository` on GitLab).

---

## Python API

You can also call the extractor directly from Python.

### Full extraction

```python
import os
from app.api.services.metadata_service import run_extraction

jsonld_document, enriched = run_extraction(
    repo_url="https://github.com/KnowledgeCaptureAndDiscovery/somef",
    schema="maSMP",                              # or "CODEMETA"
    access_token=os.getenv("GITHUB_TOKEN"),     # or GITLAB_TOKEN for GitLab
    with_enrichment=True,                       # False for JSON‑LD only
)

# jsonld_document: maSMP/CODEMETA JSON‑LD (dict)
# enriched: per‑property source/confidence/category (or None)
```

### Extract a single property in Python

For maSMP:

```python
profile = jsonld_document.get("maSMP:SoftwareSourceCode", {})
prop_name = "author"
value = profile.get(prop_name)
meta = (enriched or {}).get("maSMP:SoftwareSourceCode", {}).get(prop_name, {})

source = meta.get("source")
confidence = meta.get("confidence")
```

---

## Project links & docs

- Source code: GitHub / GitLab repository where `comet-rs` is developed
- Backend architecture and development docs:
  - `README.md` in the repo root (architecture & local FastAPI server)
  - `docs/DEVELOPER_GUIDE.md`
  - `docs/ADDING_NEW_PLATFORM.md`

Use those documents if you want to contribute, run the FastAPI backend locally, or add support for new code hosting platforms.

