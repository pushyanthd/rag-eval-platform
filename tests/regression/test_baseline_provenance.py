from pathlib import Path

import pytest

from ragops.config import load_config_bundle
from ragops.contracts import EvaluationReport
from ragops.evaluation.gate import evaluate_gate, read_baseline

ROOT = Path(__file__).parents[2]


@pytest.mark.regression
@pytest.mark.parametrize("dataset", ["scifact", "nfcorpus", "fiqa"])
def test_published_baseline_matches_its_archived_report_and_current_variants(dataset: str) -> None:
    baseline = read_baseline(ROOT / "evals" / "baselines" / f"{dataset}.json")
    report_path = ROOT / "evals" / "runs" / str(baseline.run_id) / "report.json"
    report = EvaluationReport.model_validate_json(report_path.read_text(encoding="utf-8"))
    bundle = load_config_bundle(ROOT / "config")

    assert baseline.run_id == report.run.id
    assert baseline.git_commit == report.run.git_commit
    assert baseline.variant_hashes == {
        name: bundle.variants.get(name).configuration_hash for name in report.run.spec.variants
    }
    assert baseline.metrics == {
        variant: {
            metric.metric: metric.mean for metric in report.metrics if metric.variant == variant
        }
        for variant in report.run.spec.variants
    }
    gate = evaluate_gate(report, baseline, bundle.thresholds)
    assert gate.passed
    assert len(gate.metrics) == 16
