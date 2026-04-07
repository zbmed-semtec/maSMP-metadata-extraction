"""CLI utility to compare legacy and pipeline extraction outputs."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from app.framework.api.metadata_runtime import compare_legacy_and_pipeline_extraction


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare legacy and pipeline extraction outputs for parity.",
    )
    parser.add_argument("repo_url", help="Repository URL to evaluate")
    parser.add_argument(
        "--schema",
        default="maSMP",
        choices=["maSMP", "CODEMETA"],
        help="Schema to extract (default: maSMP)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Optional platform access token",
    )
    parser.add_argument(
        "--with-enrichment",
        action="store_true",
        help="Include enriched metadata parity checks",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full diagnostics JSON",
    )
    return parser


def _print_summary(result: Dict[str, Any]) -> None:
    print(f"schema={result['schema']}")
    print(f"jsonld_keys_match={result['jsonld_keys_match']}")
    print(f"jsonld_exact_match={result['jsonld_exact_match']}")
    print(f"enriched_profiles_match={result['enriched_profiles_match']}")
    print(f"enriched_exact_match={result['enriched_exact_match']}")

    if result["jsonld_keys_match"] and result["enriched_profiles_match"]:
        return

    if not result["jsonld_keys_match"]:
        print("--- legacy_jsonld_keys")
        print(", ".join(result["legacy_jsonld_keys"]))
        print("--- pipeline_jsonld_keys")
        print(", ".join(result["pipeline_jsonld_keys"]))

    if not result["enriched_profiles_match"]:
        print("--- legacy_enriched_profiles")
        print(", ".join(result["legacy_enriched_profiles"]))
        print("--- pipeline_enriched_profiles")
        print(", ".join(result["pipeline_enriched_profiles"]))


def main() -> int:
    args = _build_parser().parse_args()
    result = compare_legacy_and_pipeline_extraction(
        repo_url=args.repo_url,
        schema=args.schema,
        access_token=args.token,
        with_enrichment=args.with_enrichment,
    )

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        _print_summary(result)

    if result["jsonld_exact_match"] and result["enriched_exact_match"]:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
