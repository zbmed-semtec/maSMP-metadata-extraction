from app.domain.services.fairness_evaluator import evaluate_fairness


def test_evaluate_fairness_all_fields_present_codemeta():
    jsonld = {
        "license": {"name": "MIT"},
        "documentation": "https://example.com/docs",
        "identifier": ["https://doi.org/10.1234/example"],
        "codeRepository": "https://github.com/example/repo",
        "softwareVersion": "1.2.3",
        "keywords": ["example"],
        "softwareRequirements": ["python>=3.10"],
    }

    report = evaluate_fairness(jsonld, schema="CODEMETA")

    # At least some reusable indicators (license, usage docs, requirements) are present
    assert report.reusable > 0.0
    # Findable indicators (description/readme, DOI, metadata) are present
    assert report.findable > 0.0
    # Accessible indicators (download URL and semver-like version) are present
    assert report.accessible == 1.0
    # Usage documentation contributes to interoperability, so it should be > 0
    assert report.interoperable > 0.0
    assert report.overall_score > 0.0

    # We expose 10 indicators (BP1–BP10)
    assert len(report.indicators) == 10


def test_evaluate_fairness_no_fields_present():
    jsonld = {}

    report = evaluate_fairness(jsonld, schema="CODEMETA")

    assert report.reusable == 0.0
    assert report.findable == 0.0
    assert report.accessible == 0.0
    assert report.overall_score == 0.0


def test_evaluate_fairness_masmp_uses_software_source_code_profile():
    jsonld = {
        "hasRelease": True,
        "maSMP:SoftwareSourceCode": {
            "license": {"name": "MIT"},
            "identifier": ["https://doi.org/10.1234/example"],
        },
        "maSMP:SoftwareApplication": {},
    }

    report = evaluate_fairness(jsonld, schema="maSMP")

    # Only license (R) and DOI (F) are present
    assert report.reusable > 0.0
    assert report.findable > 0.0
    # Accessible and interoperable remain 0
    assert report.accessible == 0.0
    assert report.interoperable == 0.0


def test_evaluate_fairness_accessible_scores_from_download_and_version():
    # Both download URL (codeRepository) and semver-like version contribute to A
    jsonld = {
        "codeRepository": "https://github.com/example/repo",
        "softwareVersion": "1.2.3",
    }

    report = evaluate_fairness(jsonld, schema="CODEMETA")
    assert report.accessible == 1.0

    # With only one of the indicators present, A should be between 0 and 1
    jsonld_only_repo = {"codeRepository": "https://github.com/example/repo"}
    report_repo = evaluate_fairness(jsonld_only_repo, schema="CODEMETA")
    assert 0.0 < report_repo.accessible < 1.0

    jsonld_only_version = {"softwareVersion": "1.2.3"}
    report_version = evaluate_fairness(jsonld_only_version, schema="CODEMETA")
    assert 0.0 < report_version.accessible < 1.0
    # Both partial cases should contribute equally
    assert report_repo.accessible == report_version.accessible


def test_evaluate_fairness_multiprinciple_indicators_affect_f_i_r():
    # Documentation and metadata should contribute to multiple principles via BP5/BP8
    jsonld = {
        "documentation": "https://example.com/docs",
        "keywords": ["example"],
    }

    report = evaluate_fairness(jsonld, schema="CODEMETA")

    # No A indicators present
    assert report.accessible == 0.0
    # Keywords → F and R, documentation → I and R
    assert report.findable > 0.0
    assert report.interoperable > 0.0
    assert report.reusable > 0.0
    assert report.overall_score > 0.0

