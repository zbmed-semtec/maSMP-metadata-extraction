import argparse
import json
import os
import sys
from typing import Any, Dict, List, Tuple

from fastapi.encoders import jsonable_encoder

from app.adapters.github.github_client import GitHubRateLimitError
from app.adapters.gitlab.gitlab_client import GitLabRateLimitError
from app.api.services.metadata_service import run_extraction


def _print_json(data: Any) -> None:
    """Print JSON-safe data to stdout."""
    safe_data = jsonable_encoder(data)
    json.dump(safe_data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def _extract_command(args: argparse.Namespace) -> None:
    jsonld_document, enriched = run_extraction(
        repo_url=args.url,
        schema=args.schema,
        access_token=args.token,
        with_enrichment=args.with_enrichment,
    )

    result = {
        "schema": args.schema,
        "code_url": args.url,
        "results": jsonld_document,
        "enriched_metadata": enriched or {},
    }
    _print_json(result)


def _normalize_property_key(property_name: str) -> Tuple[str, str]:
    """
    Return a tuple of (jsonld_style, entity_style) keys for flexible matching.

    Example:
        "codemeta:readme" -> ("codemeta:readme", "codemeta_readme")
        "codemeta_readme" -> ("codemeta:readme", "codemeta_readme")
        "name"            -> ("name", "name")
    """
    if ":" in property_name:
        jsonld_key = property_name
        entity_key = property_name.replace(":", "_")
    else:
        entity_key = property_name
        jsonld_key = property_name.replace("_", ":")
    return jsonld_key, entity_key


def _collect_property_results(
    schema: str,
    code_url: str,
    jsonld_document: Dict[str, Any],
    enriched_metadata: Dict[str, Any],
    property_name: str,
) -> Dict[str, Any]:
    jsonld_key, _ = _normalize_property_key(property_name)

    matches: List[Dict[str, Any]] = []

    if schema == "maSMP":
        profiles = ("maSMP:SoftwareSourceCode", "maSMP:SoftwareApplication")
        skip_keys = {"@context", "@type"}

        for profile in profiles:
            profile_data = jsonld_document.get(profile)
            if not isinstance(profile_data, dict):
                continue

            value = None
            if jsonld_key in profile_data and jsonld_key not in skip_keys:
                value = profile_data[jsonld_key]

            if value is None:
                continue

            meta_for_profile = enriched_metadata.get(profile, {})
            meta = meta_for_profile.get(jsonld_key, {}) if isinstance(meta_for_profile, dict) else {}

            matches.append(
                {
                    "profile": profile,
                    "property": jsonld_key,
                    "value": value,
                    "source": meta.get("source"),
                    "confidence": meta.get("confidence"),
                    "category": meta.get("category"),
                }
            )
    else:  # CODEMETA schema – single JSON-LD document
        value = jsonld_document.get(jsonld_key)
        if value is not None:
            meta = enriched_metadata.get(jsonld_key, {}) if isinstance(enriched_metadata, dict) else {}
            matches.append(
                {
                    "profile": "SoftwareSourceCode",
                    "property": jsonld_key,
                    "value": value,
                    "source": meta.get("source"),
                    "confidence": meta.get("confidence"),
                    "category": meta.get("category"),
                }
            )

    return {
        "schema": schema,
        "code_url": code_url,
        "property": jsonld_key,
        "matches": matches,
    }


def _extract_property_command(args: argparse.Namespace) -> None:
    jsonld_document, enriched = run_extraction(
        repo_url=args.url,
        schema=args.schema,
        access_token=args.token,
        with_enrichment=True,
    )

    result = _collect_property_results(
        schema=args.schema,
        code_url=args.url,
        jsonld_document=jsonld_document,
        enriched_metadata=enriched or {},
        property_name=args.property,
    )

    if not result["matches"]:
        message = (
            f"No matches found for property '{args.property}' "
            f"in schema '{args.schema}' for URL '{args.url}'."
        )
        print(message, file=sys.stderr)
        sys.exit(1)

    # Single flat dict: property_name, property_value, source(s), confidence
    first = result["matches"][0]
    source = first.get("source")
    # Keep list when multiple sources contributed; single value when one
    output = {
        "property_name": first["property"],
        "property_value": first["value"],
        "source": source,
        "confidence": first.get("confidence"),
    }
    _print_json(output)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="comet-rs",
        description=(
            "Extract maSMP/CODEMETA metadata (and per-property sources) "
            "from code repositories."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # comet-rs extract {GIT_URL} {SCHEMA}
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract full JSON-LD metadata for a repository.",
    )
    extract_parser.add_argument("url", help="Repository URL (GitHub, GitLab).")
    extract_parser.add_argument(
        "schema",
        choices=["maSMP", "CODEMETA"],
        help="Schema to analyze against.",
    )
    extract_parser.add_argument(
        "--token",
        help="GitHub/GitLab token (or set GITHUB_TOKEN / GITLAB_TOKEN). Raises rate limits when unset.",
    )
    extract_parser.add_argument(
        "--with-enrichment",
        action="store_true",
        help="Include per-property enrichment (source, confidence, category) when available.",
    )
    extract_parser.set_defaults(func=_extract_command)

    # comet-rs extract_property {GIT_URL} {PROPERTY_NAME} [--schema maSMP|CODEMETA]
    extract_prop_parser = subparsers.add_parser(
        "extract_property",
        help=(
            "Extract a single property (value and source) for a repository. "
            "Schema defaults to maSMP if not given."
        ),
    )
    extract_prop_parser.add_argument("url", help="Repository URL (GitHub, GitLab).")
    extract_prop_parser.add_argument(
        "property",
        help=(
            "Property name to extract, e.g. 'name', 'identifier', "
            "'codemeta:referencePublication' or 'codemeta_referencePublication'."
        ),
    )
    extract_prop_parser.add_argument(
        "--schema",
        choices=["maSMP", "CODEMETA"],
        default="maSMP",
        help="Schema to use (default: maSMP).",
    )
    extract_prop_parser.add_argument(
        "--token",
        help="GitHub/GitLab token (or set GITHUB_TOKEN / GITLAB_TOKEN). Raises rate limits when unset.",
    )
    extract_prop_parser.set_defaults(func=_extract_property_command)

    args = parser.parse_args()

    # Use env token if --token not provided; pick by repo URL so GitLab URLs get GITLAB_TOKEN
    if getattr(args, "token", None) is None:
        repo_url = (getattr(args, "url", None) or "").lower()
        if "gitlab" in repo_url:
            args.token = os.environ.get("GITLAB_TOKEN") or os.environ.get("GITHUB_TOKEN")
        else:
            args.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITLAB_TOKEN")

    try:
        args.func(args)
    except (GitHubRateLimitError, GitLabRateLimitError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

