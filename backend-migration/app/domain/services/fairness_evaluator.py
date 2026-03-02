"""
Layer 2: Domain Service
FAIRness evaluator – computes FAIR scores from JSON-LD.

The indicators are inspired by the 10 FAIR best practices for research
software (BP1–BP10) described in:

Hummel et al., "Assessing the FAIRness of Software Repositories Using
RDF and SHACL", 2024.
"""
from collections import defaultdict
import re
from typing import Any, Dict, List

from app.core.entities.fairness import FairnessIndicator, FairnessReport, FairPrinciple
from app.core.entities.repository_metadata import RepositoryMetadata


def _bool_to_score(value: bool) -> float:
    return 1.0 if value else 0.0


def _get_profile_view(jsonld_document: Dict[str, Any], schema: str) -> Dict[str, Any]:
    """
    Return a flattened view of the main profile to inspect for FAIR indicators.

    For maSMP we primarily look at the SoftwareSourceCode profile.
    For CODEMETA we can use the JSON-LD document directly.
    """
    if schema == "maSMP":
        profile = jsonld_document.get("maSMP:SoftwareSourceCode")
        if isinstance(profile, dict):
            return profile
        return {}
    return jsonld_document


_SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z\.-]+)?$")


def _looks_like_semver(version: str | None) -> bool:
    if not isinstance(version, str):
        return False
    return bool(_SEMVER_PATTERN.match(version.strip()))


def _has_doi(identifiers: Any) -> bool:
    if isinstance(identifiers, str):
        values = [identifiers]
    elif isinstance(identifiers, list):
        values = identifiers
    else:
        return False

    for v in values:
        if not isinstance(v, str):
            continue
        if "doi.org" in v or v.startswith("10."):
            return True
    return False


def evaluate_fairness(jsonld_document: Dict[str, Any], schema: str) -> FairnessReport:
    """
    Compute a FAIRness report from a maSMP/CODEMETA JSON-LD document.

    Indicators are coarse operationalizations of the FAIR best practices.
    They are intentionally simple and can be refined over time.
    """
    indicators: List[FairnessIndicator] = []

    profile = _get_profile_view(jsonld_document, schema)

    # ------------------------------------------------------------------
    # BP1 – Description available (F)
    # ------------------------------------------------------------------
    has_description = bool(profile.get("description") or profile.get("codemeta:readme"))
    indicators.append(
        FairnessIndicator(
            id="bp1_description_present",
            title="Description / README available",
            principle="F",
            score=_bool_to_score(has_description),
            details={
                "description_present": bool(profile.get("description")),
                "codemeta_readme_present": bool(profile.get("codemeta:readme")),
            },
        )
    )

    # ------------------------------------------------------------------
    # BP2 – Persistent identifier (e.g. DOI) available (F)
    # ------------------------------------------------------------------
    identifiers = profile.get("identifier")
    has_persistent_id = _has_doi(identifiers)
    indicators.append(
        FairnessIndicator(
            id="bp2_persistent_identifier",
            title="Persistent identifier (e.g. DOI) available",
            principle="F",
            score=_bool_to_score(has_persistent_id),
            details={"identifier": identifiers},
        )
    )

    # ------------------------------------------------------------------
    # BP3 – Download URL available (A)
    # We approximate this as: repository has a codeRepository or downloadUrl.
    # ------------------------------------------------------------------
    has_download = bool(profile.get("codeRepository") or profile.get("downloadUrl"))
    indicators.append(
        FairnessIndicator(
            id="bp3_download_url_available",
            title="Download URL / code repository available",
            principle="A",
            score=_bool_to_score(has_download),
            details={
                "codeRepository": profile.get("codeRepository"),
                "downloadUrl": profile.get("downloadUrl"),
            },
        )
    )

    # ------------------------------------------------------------------
    # BP4 – Semantic versioning followed (A)
    # We approximate this by checking whether version/softwareVersion
    # fields look like semantic versions.
    # ------------------------------------------------------------------
    version_fields = [
        profile.get("softwareVersion"),
        profile.get("version"),
    ]
    has_semver = any(_looks_like_semver(v) for v in version_fields)
    indicators.append(
        FairnessIndicator(
            id="bp4_semver_like_version",
            title="Version field resembles semantic versioning",
            principle="A",
            score=_bool_to_score(has_semver),
            details={"version_fields": version_fields},
        )
    )

    # ------------------------------------------------------------------
    # BP5 – Usage documentation available (I, R)
    # We approximate via developer/user docs or general documentation URL.
    # In the FAIR best practices this contributes to both I and R. We
    # assign the primary principle "I" here and take care of the extra
    # R contribution when aggregating scores.
    # ------------------------------------------------------------------
    usage_keys = [
        "documentation",
        "maSMP:developerDocumentation",
        "maSMP:userDocumentation",
        "maSMP:learningResource",
    ]
    has_usage_docs = any(key in profile for key in usage_keys)
    indicators.append(
        FairnessIndicator(
            id="bp5_usage_documentation",
            title="Usage / user documentation available",
            principle="I",
            score=_bool_to_score(has_usage_docs),
            details={"keys_checked": usage_keys},
        )
    )

    # ------------------------------------------------------------------
    # BP6 – License declared (R)
    # ------------------------------------------------------------------
    has_license = bool(profile.get("license"))
    indicators.append(
        FairnessIndicator(
            id="bp6_license_declared",
            title="License is declared",
            principle="R",
            score=_bool_to_score(has_license),
            details={"license": profile.get("license")},
        )
    )

    # ------------------------------------------------------------------
    # BP7 – Explicit citation provided (R)
    # ------------------------------------------------------------------
    has_citation = bool(
        profile.get("citation")
        or profile.get("codemeta:referencePublication")
    )
    indicators.append(
        FairnessIndicator(
            id="bp7_explicit_citation",
            title="Explicit citation information available",
            principle="R",
            score=_bool_to_score(has_citation),
            details={
                "citation": profile.get("citation"),
                "referencePublication": profile.get("codemeta:referencePublication"),
            },
        )
    )

    # ------------------------------------------------------------------
    # BP8 – Software metadata available (F, R)
    # We approximate via keywords or programmingLanguage.
    # ------------------------------------------------------------------
    has_software_metadata = bool(profile.get("keywords") or profile.get("programmingLanguage"))
    indicators.append(
        FairnessIndicator(
            id="bp8_software_metadata",
            title="Software metadata (keywords / language) available",
            principle="F",
            score=_bool_to_score(has_software_metadata),
            details={
                "keywords": profile.get("keywords"),
                "programmingLanguage": profile.get("programmingLanguage"),
            },
        )
    )

    # ------------------------------------------------------------------
    # BP9 – Installation instructions available (R)
    # ------------------------------------------------------------------
    install_keys = [
        "maSMP:installInstructions",
        "codemeta:buildInstructions",
    ]
    has_install_instructions = any(key in profile for key in install_keys)
    indicators.append(
        FairnessIndicator(
            id="bp9_install_instructions",
            title="Installation instructions available",
            principle="R",
            score=_bool_to_score(has_install_instructions),
            details={"keys_checked": install_keys},
        )
    )

    # ------------------------------------------------------------------
    # BP10 – Software requirements available (R)
    # ------------------------------------------------------------------
    has_requirements = bool(profile.get("softwareRequirements"))
    indicators.append(
        FairnessIndicator(
            id="bp10_software_requirements",
            title="Software requirements specified",
            principle="R",
            score=_bool_to_score(has_requirements),
            details={"softwareRequirements": profile.get("softwareRequirements")},
        )
    )

    # Aggregate scores per FAIR principle.
    # Some indicators contribute to multiple principles according to
    # Hummel et al. (BP5 → I,R; BP8 → F,R). We keep a single
    # indicator object per best practice and expand it here for
    # aggregation so that UI stays at 10 indicators but scoring
    # respects the original mapping.
    scores_by_principle: Dict[FairPrinciple, List[float]] = defaultdict(list)

    multi_principle_mapping: Dict[str, List[FairPrinciple]] = {
        "bp5_usage_documentation": ["I", "R"],
        "bp8_software_metadata": ["F", "R"],
    }

    for indicator in indicators:
        principles = multi_principle_mapping.get(indicator.id, [indicator.principle])
        for principle in principles:
            scores_by_principle[principle].append(indicator.score)

    def _avg(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    f_score = _avg(scores_by_principle.get("F", []))
    a_score = _avg(scores_by_principle.get("A", []))
    i_score = _avg(scores_by_principle.get("I", []))
    r_score = _avg(scores_by_principle.get("R", []))

    non_zero_principle_scores = [s for s in [f_score, a_score, i_score, r_score] if s > 0]
    overall = _avg(non_zero_principle_scores) if non_zero_principle_scores else 0.0

    return FairnessReport(
        overall_score=overall,
        findable=f_score,
        accessible=a_score,
        interoperable=i_score,
        reusable=r_score,
        indicators=indicators,
    )


def evaluate_fairness_from_metadata(metadata: RepositoryMetadata) -> FairnessReport:
    """
    Compute a FAIRness report directly from the internal RepositoryMetadata entity.

    This makes FAIRness assessment invariant to the exported schema (maSMP/CODEMETA),
    because it works on the unified view of all extracted information.
    """
    indicators: List[FairnessIndicator] = []

    # BP1 – Description / README available (F)
    has_description = bool(metadata.description or metadata.codemeta_readme)
    indicators.append(
        FairnessIndicator(
            id="bp1_description_present",
            title="Description / README available",
            principle="F",
            score=_bool_to_score(has_description),
            details={
                "description_present": bool(metadata.description),
                "codemeta_readme_present": bool(metadata.codemeta_readme),
            },
        )
    )

    # BP2 – Persistent identifier (e.g. DOI) available (F)
    identifier_values: List[str] = []
    if metadata.identifier:
        identifier_values.extend(metadata.identifier)
    if metadata.doi:
        identifier_values.append(metadata.doi)
    if metadata.codemeta_referencePublication and metadata.codemeta_referencePublication.id:
        identifier_values.append(metadata.codemeta_referencePublication.id)
    has_persistent_id = _has_doi(identifier_values)
    indicators.append(
        FairnessIndicator(
            id="bp2_persistent_identifier",
            title="Persistent identifier (e.g. DOI) available",
            principle="F",
            score=_bool_to_score(has_persistent_id),
            details={"identifier": identifier_values},
        )
    )

    # BP3 – Download URL / code repository available (A)
    has_download = bool(metadata.codeRepository or metadata.downloadUrl)
    indicators.append(
        FairnessIndicator(
            id="bp3_download_url_available",
            title="Download URL / code repository available",
            principle="A",
            score=_bool_to_score(has_download),
            details={
                "codeRepository": metadata.codeRepository,
                "downloadUrl": metadata.downloadUrl,
            },
        )
    )

    # BP4 – Semantic versioning followed (A)
    version_fields = [
        metadata.softwareVersion,
        metadata.version,
    ]
    has_semver = any(_looks_like_semver(v) for v in version_fields)
    indicators.append(
        FairnessIndicator(
            id="bp4_semver_like_version",
            title="Version field resembles semantic versioning",
            principle="A",
            score=_bool_to_score(has_semver),
            details={"version_fields": version_fields},
        )
    )

    # BP5 – Usage documentation available (I, R)
    has_usage_docs = bool(
        metadata.documentation
        or metadata.masmp_developerDocumentation
        or metadata.masmp_userDocumentation
        or metadata.masmp_learningResource
    )
    indicators.append(
        FairnessIndicator(
            id="bp5_usage_documentation",
            title="Usage / user documentation available",
            principle="I",
            score=_bool_to_score(has_usage_docs),
            details={
                "documentation": bool(metadata.documentation),
                "masmp_developerDocumentation": bool(metadata.masmp_developerDocumentation),
                "masmp_userDocumentation": bool(metadata.masmp_userDocumentation),
                "masmp_learningResource": bool(metadata.masmp_learningResource),
            },
        )
    )

    # BP6 – License declared (R)
    has_license = bool(metadata.license)
    indicators.append(
        FairnessIndicator(
            id="bp6_license_declared",
            title="License is declared",
            principle="R",
            score=_bool_to_score(has_license),
            details={"license": metadata.license.dict(exclude_none=True) if metadata.license else None},
        )
    )

    # BP7 – Explicit citation provided (R)
    has_citation = bool(metadata.citation or metadata.codemeta_referencePublication)
    indicators.append(
        FairnessIndicator(
            id="bp7_explicit_citation",
            title="Explicit citation information available",
            principle="R",
            score=_bool_to_score(has_citation),
            details={
                "citation": metadata.citation,
                "referencePublication": (
                    metadata.codemeta_referencePublication.dict(exclude_none=True)
                    if metadata.codemeta_referencePublication
                    else None
                ),
            },
        )
    )

    # BP8 – Software metadata (keywords / language) available (F, R)
    has_software_metadata = bool(metadata.keywords or metadata.programmingLanguage)
    indicators.append(
        FairnessIndicator(
            id="bp8_software_metadata",
            title="Software metadata (keywords / language) available",
            principle="F",
            score=_bool_to_score(has_software_metadata),
            details={
                "keywords": metadata.keywords,
                "programmingLanguage": metadata.programmingLanguage,
            },
        )
    )

    # BP9 – Installation instructions available (R)
    has_install_instructions = bool(
        metadata.masmp_installInstructions or metadata.codemeta_buildInstructions
    )
    indicators.append(
        FairnessIndicator(
            id="bp9_install_instructions",
            title="Installation instructions available",
            principle="R",
            score=_bool_to_score(has_install_instructions),
            details={
                "masmp_installInstructions": bool(metadata.masmp_installInstructions),
                "codemeta_buildInstructions": bool(metadata.codemeta_buildInstructions),
            },
        )
    )

    # BP10 – Software requirements available (R)
    has_requirements = bool(metadata.softwareRequirements)
    indicators.append(
        FairnessIndicator(
            id="bp10_software_requirements",
            title="Software requirements specified",
            principle="R",
            score=_bool_to_score(has_requirements),
            details={"softwareRequirements": metadata.softwareRequirements},
        )
    )

    # Aggregate scores per FAIR principle with the same multi-principle mapping
    scores_by_principle: Dict[FairPrinciple, List[float]] = defaultdict(list)
    multi_principle_mapping: Dict[str, List[FairPrinciple]] = {
        "bp5_usage_documentation": ["I", "R"],
        "bp8_software_metadata": ["F", "R"],
    }

    for indicator in indicators:
        principles = multi_principle_mapping.get(indicator.id, [indicator.principle])
        for principle in principles:
            scores_by_principle[principle].append(indicator.score)

    def _avg(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    f_score = _avg(scores_by_principle.get("F", []))
    a_score = _avg(scores_by_principle.get("A", []))
    i_score = _avg(scores_by_principle.get("I", []))
    r_score = _avg(scores_by_principle.get("R", []))

    non_zero_principle_scores = [s for s in [f_score, a_score, i_score, r_score] if s > 0]
    overall = _avg(non_zero_principle_scores) if non_zero_principle_scores else 0.0

    return FairnessReport(
        overall_score=overall,
        findable=f_score,
        accessible=a_score,
        interoperable=i_score,
        reusable=r_score,
        indicators=indicators,
    )

