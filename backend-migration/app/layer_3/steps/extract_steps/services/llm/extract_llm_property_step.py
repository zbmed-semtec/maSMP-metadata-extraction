"""Placeholder step for future LLM-based property extraction."""
from __future__ import annotations

from typing import Optional

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep
from app.layer_3.steps.extract_steps.services.files.helpers.repository_files import (
    repository_file_content,
)
import re
from app.config import readme_llm_settings
import yaml
from pathlib import Path

# Cached prompts loaded from YAML
_PROMPTS_CACHE: dict | None = None


def _load_prompts() -> dict:
    global _PROMPTS_CACHE
    if _PROMPTS_CACHE is not None:
        return _PROMPTS_CACHE
    prompts_path = Path(__file__).parents[4] / "config" / "readme_llm_prompts.yaml"
    if not prompts_path.exists():
        _PROMPTS_CACHE = {}
        return _PROMPTS_CACHE
    with prompts_path.open("r", encoding="utf8") as fh:
        _PROMPTS_CACHE = yaml.safe_load(fh) or {}
    return _PROMPTS_CACHE


class ExtractLlmPropertyStep:
    """Lightweight LLM-step shim: uses config and simple heuristics to extract
    README-derived properties. This is intentionally deterministic so tests
    can run offline until a provider integration is added.
    """

    name = "llm.extract_property"

    DOI_URL_PATTERN = re.compile(r"https://(?:doi\.org/([^
\s\)\]\"']+)|zenodo\.org/records?/(\d+))", re.IGNORECASE)

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # prefer explicit args, fallback to config
        self.api_key = api_key or readme_llm_settings.api_key
        self.model = model or readme_llm_settings.model

    def _extract_doi_urls(self, text: str) -> list[str]:
        results: list[str] = []
        for m in self.DOI_URL_PATTERN.finditer(text):
            doi = m.group(1) if m.group(1) else f"10.5281/zenodo.{m.group(2)}"
            doi_url = f"https://doi.org/{doi}"
            if doi_url not in results:
                results.append(doi_url)
        return results

    def _extract_keywords(self, text: str) -> list[str]:
        # look for a 'Keywords:' line with comma-separated words
        kws: list[str] = []
        for line in text.splitlines():
            if line.strip().lower().startswith("keywords:"):
                _, rest = line.split(":", 1)
                parts = [p.strip() for p in rest.split(",") if p.strip()]
                kws.extend(parts)
                break
        return kws

    def _extract_authors(self, text: str) -> list[dict]:
        # simple heuristics: lines like 'Author: Jane Doe' or 'Authors: A and B'
        authors: list[dict] = []
        for line in text.splitlines():
            l = line.strip()
            if l.lower().startswith("author:") or l.lower().startswith("authors:"):
                _, rest = l.split(":", 1)
                rest = rest.strip()
                # split on ' and ' or comma
                parts = [p.strip() for p in re.split(r",| and ", rest) if p.strip()]
                for p in parts:
                    names = p.split()
                    family = names[0] if names else ""
                    given = " ".join(names[1:]) if len(names) > 1 else None
                    authors.append({"@type": "Person", "familyName": family, "givenName": given})
                break
        return authors

    def run(self, context: StepContext, state: StepState) -> StepState:
        # Respect config toggle
        if not readme_llm_settings.enabled:
            return state

        # Ensure readme content is available
        content = repository_file_content(
            context, state, "readme_content", ("README.md", "README.rst", "README.txt", "README")
        )

        if not content:
            return state

        # Load prompts from YAML (prompt engineering file) and fall back to settings
        prompts = _load_prompts()
        prompt_template = prompts.get("default_prompt") or readme_llm_settings.prompt_template
        hints = prompts.get("hints") or readme_llm_settings.hints

        # Build a lightweight prompt (for future provider use)
        prompt = f"{prompt_template}\nHints: {', '.join(hints)}\n\n{content}"

        # Heuristic extraction (deterministic)
        doi_urls = self._extract_doi_urls(content)
        keywords = self._extract_keywords(content)
        authors = self._extract_authors(content)

        # License detection via YAML rules if present
        license_info: dict | None = None
        license_cfg = prompts.get("license_detection") if prompts else None
        if license_cfg:
            spdx_pat = license_cfg.get("spdx_pattern")
            copyright_pat = license_cfg.get("copyright_pattern")
            lic_id = None
            lic_holder = None
            if spdx_pat:
                m = re.search(spdx_pat, content)
                if m:
                    lic_id = m.group(0)
            if not lic_holder and copyright_pat:
                m2 = re.search(copyright_pat, content)
                if m2:
                    # named group 'holder' expected in pattern
                    try:
                        lic_holder = m2.group("holder").strip()
                    except Exception:
                        # fallback to first captured group
                        lic_holder = m2.group(1).strip() if m2.groups() else None
            if lic_id or lic_holder:
                license_info = {"identifier": lic_id, "holder": lic_holder}

        # Apply results directly into metadata to make them available without
        # modifying merge steps yet. This is a small, explicit bridge until
        # merge steps are extended to consume llm-specific keys.
        if doi_urls:
            identifier_values = list(state.metadata.identifier or [])
            for d in doi_urls:
                if d not in identifier_values:
                    identifier_values.append(d)
            state.metadata.identifier = identifier_values

        if keywords:
            kw_values = list(state.metadata.keywords or [])
            for k in keywords:
                if k not in kw_values:
                    kw_values.append(k)
            state.metadata.keywords = kw_values

        if authors:
            merged = list(state.metadata.author or [])
            seen = {(a.get("familyName"), a.get("givenName")) for a in merged if isinstance(a, dict)}
            for a in authors:
                key = (a.get("familyName"), a.get("givenName"))
                if key not in seen:
                    merged.append(a)
                    seen.add(key)
            state.metadata.author = merged

        # provide the prompt and a placeholder for provider response for future
        state.data["llm_prompt"] = prompt
        state.data["llm_extracted_properties"] = {
            "identifier": doi_urls,
            "keywords": keywords,
            "author": authors,
        }
        # put license info into state for downstream merge/steps
        if license_info:
            # mirror the license content extraction key used elsewhere
            if license_info.get("holder"):
                state.data["extracted_license_copyright_holder"] = license_info.get("holder")
            if license_info.get("identifier"):
                state.data["extracted_license_identifier"] = license_info.get("identifier")

        return state


__all__ = ["ExtractLlmPropertyStep"]

