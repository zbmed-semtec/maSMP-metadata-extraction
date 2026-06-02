"""
Software-domain extraction source identifiers and confidence defaults.

Keep this domain-local so future domains (e.g. training materials) can have
their own provenance vocabulary without mixing rules.
"""

# Source identifiers (used in enriched_metadata.source)
SOURCE_GITHUB_API = "github_api"
SOURCE_GITLAB_API = "gitlab_api"
SOURCE_CITATION_CFF = "citation_cff"
SOURCE_LICENSE_FILE = "license_file"
SOURCE_README_PARSER = "readme_parser"
SOURCE_ZENODO_BADGE = "zenodo_badge"
SOURCE_WAYBACK = "wayback"
SOURCE_SOFTWARE_HERITAGE = "software_heritage"
SOURCE_OPENALEX = "openalex"
SOURCE_LLM = "llm"  # for future LLM extraction

# Confidence per source (0.0-1.0). Single place to tune trust.
CONFIDENCE_PLATFORM = 1.0      # Official platform API (GitHub, GitLab)
CONFIDENCE_CITATION = 0.95     # Structured CITATION.cff
CONFIDENCE_LICENSE = 0.9       # Parsed from LICENSE file
CONFIDENCE_README = 0.80     # Unstructured README parsing
CONFIDENCE_ARCHIVE = 0.85      # Zenodo badge / Wayback
CONFIDENCE_OPENALEX = 0.9      # OpenAlex API
CONFIDENCE_LLM = 0.7           # LLM extraction (when implemented)
