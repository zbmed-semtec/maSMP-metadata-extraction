"""LLM-backed README property extraction step."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import requests
import yaml

from app.config import readme_llm_settings
from app.config.settings import settings as app_settings
from app.layer_1.entities.shared_primitives import License, ReferencePublication
from app.layer_1.provenance.software.defaults import CONFIDENCE_LLM, SOURCE_LLM
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.helpers.repository_files import (
    repository_file_content,
)
from app.layer_3.extraction_metadata.record import record_field_provenance

_PROMPTS_CACHE: dict[str, Any] | None = None
_SECTION_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
_DOI_URL_RE = re.compile(
    r"https?://(?:doi\.org/([^\s\)\]\"']+)|zenodo\.org/(?:records?|record)/?(\d+))",
    re.IGNORECASE,
)
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_URL_RE = re.compile(r"https?://[^\s<>()\[\]\"'`]+", re.IGNORECASE)


@lru_cache(maxsize=1)
def _default_license_url(spdx: str | None) -> str | None:
    if not spdx:
        return None
    normalized = spdx.strip()
    if not normalized:
        return None
    return f"https://spdx.org/licenses/{normalized}.html"


def _load_prompts() -> dict[str, Any]:
    global _PROMPTS_CACHE
    if _PROMPTS_CACHE is not None:
        return _PROMPTS_CACHE

    prompts_path = Path(__file__).parents[5] / "config" / "readme_llm_prompts.yaml"
    if not prompts_path.exists():
        _PROMPTS_CACHE = {}
        return _PROMPTS_CACHE

    with prompts_path.open("r", encoding="utf8") as fh:
        _PROMPTS_CACHE = yaml.safe_load(fh) or {}
    return _PROMPTS_CACHE


def _normalize_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        items = [value]

    normalized: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item is None:
            continue
        text = str(item).strip()
        if not text:
            continue
        if text not in seen:
            seen.add(text)
            normalized.append(text)
    return normalized


def _split_name(name: str) -> tuple[str | None, str | None]:
    text = name.strip()
    if not text:
        return None, None
    if "," in text:
        family, given = [part.strip() for part in text.split(",", 1)]
        return given or None, family or None
    parts = text.split()
    if len(parts) == 1:
        return None, parts[0]
    return " ".join(parts[:-1]) or None, parts[-1] or None


def _normalize_people(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        items = [value]

    normalized: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for item in items:
        if isinstance(item, dict):
            name = item.get("name") or item.get("fullName")
            given_name = item.get("givenName")
            family_name = item.get("familyName")
            if not given_name and not family_name and isinstance(name, str):
                given_name, family_name = _split_name(name)
            url = item.get("url") or item.get("github_url")
            email = item.get("email")
        else:
            text = str(item).strip()
            if not text:
                continue
            name = text
            given_name, family_name = _split_name(text)
            url = None
            email = None

        key = (name, given_name, family_name, url, email)
        if key in seen:
            continue
        seen.add(key)

        entry: dict[str, Any] = {"@type": "Person"}
        if name:
            entry["name"] = name
        if given_name:
            entry["givenName"] = given_name
        if family_name:
            entry["familyName"] = family_name
        if url:
            entry["url"] = url
        if email:
            entry["email"] = email
        normalized.append(entry)

    return normalized


def _normalize_license(value: Any) -> License | None:
    if value is None:
        return None
    if isinstance(value, dict):
        name = value.get("name") or value.get("identifier") or value.get("spdx")
        url = value.get("url")
    elif isinstance(value, str):
        name = value.strip() or None
        url = None
    elif isinstance(value, list) and value:
        return _normalize_license(value[0])
    else:
        name = str(value).strip() or None
        url = None

    if not name and not url:
        return None

    if not url:
        url = _default_license_url(name)

    return License(name=name, url=url)


def _normalize_citations(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        items = [value]

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        if isinstance(item, dict):
            data = dict(item)
        else:
            text = str(item).strip()
            if not text:
                continue
            data = {"name": text}
        fingerprint = json.dumps(data, sort_keys=True, ensure_ascii=False)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        normalized.append(data)
    return normalized


def _normalize_links(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        items = [value]

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        if isinstance(item, dict):
            url = str(item.get("url") or "").strip()
            title = item.get("title")
            relevance = item.get("relevance") or "other"
            is_working = item.get("is_working")
            status_code = item.get("status_code")
        else:
            url = str(item).strip()
            title = None
            relevance = "other"
            is_working = None
            status_code = None

        if not url:
            continue

        canonical = url.rstrip(").,;")
        if canonical in seen:
            continue
        seen.add(canonical)
        normalized.append(
            {
                "title": title,
                "url": canonical,
                "relevance": relevance,
                "is_working": is_working,
                "status_code": status_code,
            }
        )
    return normalized


class ExtractLlmPropertyStep:
    """Prompt-driven README property extraction with provider fallback."""

    name = "llm.extract_property"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        self.api_key = api_key or readme_llm_settings.api_key or getattr(app_settings, "llm_api_key", None)
        self.model = model or readme_llm_settings.model
        self.provider = (provider or readme_llm_settings.provider or getattr(app_settings, "llm_provider", "vllm")).strip().lower()
        self.base_url = base_url or readme_llm_settings.base_url
        self.timeout = timeout or readme_llm_settings.request_timeout
        self.temperature = readme_llm_settings.temperature if temperature is None else temperature
        self.max_tokens = readme_llm_settings.max_tokens if max_tokens is None else max_tokens

    def _resolve_base_url(self) -> str:
        if self.base_url:
            return self.base_url
        if self.provider == "ollama":
            return "http://127.0.0.1:11435"
        return "http://localhost:8000"

    def _extract_doi_urls(self, text: str) -> list[str]:
        results: list[str] = []
        for match in _DOI_URL_RE.finditer(text):
            doi = match.group(1) if match.group(1) else f"10.5281/zenodo.{match.group(2)}"
            url = f"https://doi.org/{doi}"
            if url not in results:
                results.append(url)
        return results

    def _extract_keywords(self, text: str) -> list[str]:
        keywords: list[str] = []
        for line in text.splitlines():
            if line.strip().lower().startswith("keywords:"):
                _, rest = line.split(":", 1)
                parts = [part.strip() for part in rest.split(",") if part.strip()]
                keywords.extend(parts)
                break
        return keywords

    def _extract_authors(self, text: str) -> list[dict[str, Any]]:
        authors: list[dict[str, Any]] = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("author:") or stripped.lower().startswith("authors:"):
                _, rest = stripped.split(":", 1)
                parts = [part.strip() for part in re.split(r",| and ", rest) if part.strip()]
                for part in parts:
                    given_name, family_name = _split_name(part)
                    authors.append({"@type": "Person", "givenName": given_name, "familyName": family_name, "name": part})
                break
        return authors

    def _extract_license(self, text: str) -> tuple[License | None, str | None]:
        prompts = _load_prompts()
        patterns = prompts.get("license_patterns") or []
        if not isinstance(patterns, list):
            patterns = []

        normalized_patterns: list[tuple[str, str]] = []
        for item in patterns:
            if isinstance(item, dict):
                pattern = item.get("pattern")
                spdx = item.get("spdx") or item.get("value")
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                pattern, spdx = item[0], item[1]
            else:
                continue
            if pattern and spdx:
                normalized_patterns.append((str(pattern), str(spdx)))

        low = text.lower()
        for pattern, spdx in normalized_patterns:
            match = re.search(pattern, low, flags=re.IGNORECASE)
            if match:
                start = max(0, match.start() - 80)
                end = min(len(text), match.end() + 80)
                evidence = text[start:end].replace("\n", " ").strip()
                return License(name=spdx, url=_default_license_url(spdx)), evidence
        return None, None

    def _split_sections(self, text: str) -> list[dict[str, str]]:
        sections: list[dict[str, str]] = []
        current_heading: str | None = None
        current_lines: list[str] = []
        for line in text.splitlines():
            match = _SECTION_HEADING_RE.match(line.strip())
            if match:
                if current_lines:
                    sections.append({"heading": current_heading or "", "content": "\n".join(current_lines).strip()})
                current_heading = match.group(2).strip()
                current_lines = []
            else:
                current_lines.append(line)
        if current_lines:
            sections.append({"heading": current_heading or "", "content": "\n".join(current_lines).strip()})
        return sections

    def _select_context(self, text: str, property_name: str, prompts: dict[str, Any], top_k: int = 3) -> str:
        terms = prompts.get("property_queries", {}).get(property_name, [])
        if not isinstance(terms, list):
            terms = []
        sections = self._split_sections(text)
        if not sections:
            return text[:6000]

        scored_sections: list[tuple[float, dict[str, str]]] = []
        for section in sections:
            heading = section["heading"].lower()
            content = section["content"].lower()
            score = 0.0
            for term in terms:
                needle = str(term).lower()
                if needle and needle in heading:
                    score += 2.0
                if needle and needle in content:
                    score += 1.0
            scored_sections.append((score, section))

        scored_sections.sort(key=lambda item: item[0], reverse=True)
        selected = [section for score, section in scored_sections[:top_k] if score > 0]
        if not selected:
            selected = sections[:top_k]

        rendered: list[str] = []
        for section in selected:
            heading = section["heading"].strip()
            content = section["content"].strip()
            if heading:
                rendered.append(f"## {heading}\n{content}")
            else:
                rendered.append(content)
        context = "\n\n".join(part for part in rendered if part).strip()
        return context[:7000] if context else text[:6000]

    def _build_prompt(self, property_name: str, context: str, prompts: dict[str, Any]) -> str:
        prompt_templates = prompts.get("prompts", {}) if isinstance(prompts.get("prompts", {}), dict) else {}
        property_prompt = prompt_templates.get(property_name) or prompts.get("default_prompt") or f"Extract {property_name} from the README."
        schema_hint = prompts.get("property_schema_hints", {}).get(property_name, "null if unknown")
        rule_hint = prompts.get("property_rules", {}).get(property_name, prompts.get("property_rules", {}).get("default", "Return concise value and evidence quote if available."))
        return (
            f"{property_prompt}\n\n"
            f"Rules: {rule_hint}\n"
            f"Expected value shape: {schema_hint}\n\n"
            "No guessing. Return JSON only with keys: value, evidence, confidence.\n"
            "- value: extracted value or null\n"
            "- evidence: exact short quote from context or null\n"
            "- confidence: number from 0 to 1\n\n"
            f"Context:\n{context}"
        )

    def _extract_json(self, text: str) -> dict[str, Any]:
        cleaned = (text or "").strip()
        if not cleaned:
            return {"value": None, "evidence": None, "confidence": 0.0}

        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()

        def normalize(parsed: Any) -> dict[str, Any]:
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        return item
            return {"value": parsed, "evidence": None, "confidence": 0.0}

        try:
            return normalize(json.loads(cleaned))
        except Exception:
            pass

        try:
            decoder = json.JSONDecoder()
            parsed, _ = decoder.raw_decode(cleaned)
            return normalize(parsed)
        except Exception:
            pass

        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return normalize(json.loads(match.group(0)))
            except Exception:
                pass

        return {"value": cleaned, "evidence": None, "confidence": 0.0}

    def _call_llm(self, prompt: str) -> str:
        base_url = self._resolve_base_url().rstrip("/")
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if self.provider == "ollama":
            endpoint = f"{base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
            }
            response = requests.post(endpoint, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return str(data.get("response", ""))

        endpoint = f"{base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        response = requests.post(endpoint, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _merge_unique_strings(self, existing: Optional[list[str]], additions: list[str]) -> list[str]:
        merged: list[str] = list(existing or [])
        seen = {item for item in merged if item}
        for item in additions:
            if item and item not in seen:
                merged.append(item)
                seen.add(item)
        return merged

    def _merge_people(self, existing: Optional[list[dict[str, Any]]], additions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = list(existing or [])
        seen = {
            (item.get("name"), item.get("givenName"), item.get("familyName"), item.get("url"), item.get("email"))
            for item in merged
            if isinstance(item, dict)
        }
        for item in additions:
            key = (item.get("name"), item.get("givenName"), item.get("familyName"), item.get("url"), item.get("email"))
            if key not in seen:
                merged.append(item)
                seen.add(key)
        return merged

    def _normalize_identifier(self, value: Any) -> list[str]:
        raw_items = _normalize_text_list(value)
        normalized: list[str] = []
        for item in raw_items:
            text = item.strip().rstrip(".,;")
            match = _DOI_URL_RE.search(text)
            if match:
                doi = match.group(1) if match.group(1) else f"10.5281/zenodo.{match.group(2)}"
                url = f"https://doi.org/{doi}"
            elif text.startswith("10."):
                url = f"https://doi.org/{text}"
            else:
                url = text
            if url not in normalized:
                normalized.append(url)
        return normalized

    def _apply_property(self, state: StepState, property_name: str, value: Any, evidence: str | None) -> None:
        if property_name == "identifier":
            state.metadata.identifier = self._merge_unique_strings(state.metadata.identifier, self._normalize_identifier(value))
            record_field_provenance(state, "identifier", SOURCE_LLM, CONFIDENCE_LLM)
            return

        if property_name == "keywords":
            state.metadata.keywords = self._merge_unique_strings(state.metadata.keywords, _normalize_text_list(value))
            record_field_provenance(state, "keywords", SOURCE_LLM, CONFIDENCE_LLM)
            return

        if property_name == "alternateName":
            state.metadata.alternateName = self._merge_unique_strings(state.metadata.alternateName, _normalize_text_list(value))
            record_field_provenance(state, "alternateName", SOURCE_LLM, CONFIDENCE_LLM)
            return

        if property_name in {"author", "contributors"}:
            people = _normalize_people(value)
            if property_name == "author":
                state.metadata.author = self._merge_people(state.metadata.author, people)
                record_field_provenance(state, "author", SOURCE_LLM, CONFIDENCE_LLM)
            else:
                state.metadata.contributor = self._merge_people(state.metadata.contributor, people)
                record_field_provenance(state, "contributor", SOURCE_LLM, CONFIDENCE_LLM)
            return

        if property_name == "license":
            normalized_license = _normalize_license(value)
            if normalized_license is not None:
                state.metadata.license = normalized_license
                if evidence:
                    state.data["extracted_license_evidence"] = evidence
                record_field_provenance(state, "license", SOURCE_LLM, CONFIDENCE_LLM)
            return

        if property_name == "description":
            text_values = _normalize_text_list(value)
            if text_values:
                state.metadata.description = text_values[0]
                record_field_provenance(state, "description", SOURCE_LLM, CONFIDENCE_LLM)
            return

        if property_name == "installation":
            text_values = _normalize_text_list(value)
            if text_values:
                state.metadata.masmp_installInstructions = text_values[0]
                record_field_provenance(state, "masmp_installInstructions", SOURCE_LLM, CONFIDENCE_LLM)
            return

        if property_name == "contact":
            text_values = _normalize_text_list(value)
            if text_values:
                contact_value = text_values[0]
                state.data["llm_contact"] = contact_value
                if _EMAIL_RE.fullmatch(contact_value):
                    person = {"@type": "Person", "email": contact_value}
                    state.metadata.maintainer = self._merge_people(state.metadata.maintainer, [person])
                    record_field_provenance(state, "maintainer", SOURCE_LLM, CONFIDENCE_LLM)
                elif contact_value.startswith("http"):
                    state.metadata.documentation = contact_value
                    record_field_provenance(state, "documentation", SOURCE_LLM, CONFIDENCE_LLM)
            return

        if property_name == "links":
            links = _normalize_links(value)
            state.data["llm_links"] = links
            docs_links = [item for item in links if str(item.get("relevance") or "").lower() == "docs" and item.get("url")]
            paper_links = [item for item in links if str(item.get("relevance") or "").lower() == "paper" and item.get("url")]
            tutorial_links = [item for item in links if str(item.get("relevance") or "").lower() == "tutorial" and item.get("url")]
            if docs_links and not state.metadata.documentation:
                state.metadata.documentation = docs_links[0]["url"]
                record_field_provenance(state, "documentation", SOURCE_LLM, CONFIDENCE_LLM)
            if paper_links:
                existing = list(state.metadata.citation or [])
                for item in paper_links:
                    citation_item = {"title": item.get("title"), "url": item.get("url"), "relevance": "paper"}
                    if citation_item not in existing:
                        existing.append(citation_item)
                state.metadata.citation = existing
                record_field_provenance(state, "citation", SOURCE_LLM, CONFIDENCE_LLM)
            if tutorial_links and not state.metadata.masmp_learningResource:
                state.metadata.masmp_learningResource = tutorial_links[0]["url"]
                record_field_provenance(state, "masmp_learningResource", SOURCE_LLM, CONFIDENCE_LLM)
            return

        if property_name == "citation":
            citations = _normalize_citations(value)
            if citations:
                existing = list(state.metadata.citation or [])
                for item in citations:
                    if item not in existing:
                        existing.append(item)
                state.metadata.citation = existing

                first = citations[0]
                reference_name = first.get("name") or first.get("title")
                authors = _normalize_people(first.get("author") or first.get("authors"))
                reference_kwargs: dict[str, Any] = {}
                if reference_name:
                    reference_kwargs["name"] = reference_name
                if authors:
                    reference_kwargs["author"] = authors
                if reference_kwargs:
                    try:
                        state.metadata.codemeta_referencePublication = ReferencePublication(**reference_kwargs)
                    except Exception:
                        pass
                record_field_provenance(state, "citation", SOURCE_LLM, CONFIDENCE_LLM)
                if state.metadata.codemeta_referencePublication:
                    record_field_provenance(state, "codemeta_referencePublication", SOURCE_LLM, CONFIDENCE_LLM)
            return

    def _extract_with_llm(self, property_name: str, context: str, prompts: dict[str, Any]) -> dict[str, Any]:
        prompt = self._build_prompt(property_name, context, prompts)
        raw = ""
        error: str | None = None
        try:
            raw = self._call_llm(prompt)
        except Exception as exc:
            error = str(exc)

        parsed = self._extract_json(raw)
        value = parsed.get("value")
        evidence = parsed.get("evidence")
        confidence = parsed.get("confidence")

        if property_name == "license":
            heuristic_license, heuristic_evidence = self._extract_license(context)
            if not value and heuristic_license is not None:
                value = {"name": heuristic_license.name, "url": str(heuristic_license.url) if heuristic_license.url else None}
                evidence = heuristic_evidence or evidence
                confidence = confidence or 0.95
        elif property_name == "identifier":
            heuristic_identifiers = self._extract_doi_urls(context)
            if not value and heuristic_identifiers:
                value = heuristic_identifiers
                evidence = evidence or "Found DOI/Zenodo identifiers in README content."
                confidence = confidence or 0.95
        elif property_name == "keywords":
            heuristic_keywords = self._extract_keywords(context)
            if not value and heuristic_keywords:
                value = heuristic_keywords
                evidence = evidence or "Found README keywords line."
                confidence = confidence or 0.8
        elif property_name == "author":
            heuristic_authors = self._extract_authors(context)
            if not value and heuristic_authors:
                value = heuristic_authors
                evidence = evidence or "Found author line in README content."
                confidence = confidence or 0.8

        if value is None:
            value = [] if property_name in {"identifier", "keywords", "alternateName", "author", "contributors", "citation", "links"} else None

        return {
            "value": value,
            "evidence": evidence,
            "confidence": confidence if confidence is not None else (0.0 if error else 0.7),
            "raw": raw,
            "error": error,
            "prompt": prompt,
        }

    def run(self, context: StepContext, state: StepState) -> StepState:
        if not readme_llm_settings.enabled:
            return state

        content = repository_file_content(
            context,
            state,
            "readme_content",
            ("README.md", "README.rst", "README.txt", "README"),
        )
        if not content:
            return state

        state.data["llm_used"] = True

        prompts = _load_prompts()
        property_type = readme_llm_settings.property_type
        property_names = prompts.get("property_types", {}).get(property_type, [])
        if not isinstance(property_names, list) or not property_names:
            property_names = list(readme_llm_settings.property_types.get(property_type, []))
        if not property_names:
            property_names = ["identifier", "author", "alternateName", "keywords", "citation", "license"]

        extracted: dict[str, Any] = {}
        prompts_used: dict[str, str] = {}
        raw_outputs: dict[str, Any] = {}

        for property_name in property_names:
            context_text = self._select_context(content, property_name, prompts)
            result = self._extract_with_llm(property_name, context_text, prompts)
            extracted[property_name] = {
                "value": result.get("value"),
                "evidence": result.get("evidence"),
                "confidence": result.get("confidence", 0.0),
            }
            raw_outputs[property_name] = {
                "raw": result.get("raw"),
                "error": result.get("error"),
            }
            prompts_used[property_name] = result.get("prompt", "")
            self._apply_property(state, property_name, result.get("value"), result.get("evidence"))

        state.data["llm_prompt"] = prompts_used
        state.data["llm_extracted_properties"] = extracted
        state.data["llm_raw_outputs"] = raw_outputs
        return state


__all__ = ["ExtractLlmPropertyStep"]
