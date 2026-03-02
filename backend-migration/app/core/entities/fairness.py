from dataclasses import dataclass
from typing import Any, Dict, List, Literal


FairPrinciple = Literal["F", "A", "I", "R"]


@dataclass(frozen=True)
class FairnessIndicator:
    """
    Single FAIRness indicator result.

    Each indicator contributes a score to one FAIR principle.
    """

    id: str
    title: str
    principle: FairPrinciple
    score: float
    details: Dict[str, Any]


@dataclass(frozen=True)
class FairnessReport:
    """
    Aggregated FAIRness assessment for a repository.
    """

    overall_score: float
    findable: float
    accessible: float
    interoperable: float
    reusable: float
    indicators: List[FairnessIndicator]
    model_version: str = "1.0.0"

