from app.core.entities.fairness import FairnessIndicator, FairnessReport


def test_fairness_indicator_and_report_basic():
    indicator = FairnessIndicator(
        id="license_present",
        title="License is specified",
        principle="R",
        score=1.0,
        details={"has_license": True},
    )

    report = FairnessReport(
        overall_score=1.0,
        findable=0.0,
        accessible=0.0,
        interoperable=0.0,
        reusable=1.0,
        indicators=[indicator],
    )

    assert report.overall_score == 1.0
    assert report.reusable == 1.0
    assert report.indicators[0].id == "license_present"
    assert report.indicators[0].principle == "R"

