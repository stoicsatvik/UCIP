"""Unit tests for conservative UCIP replay-candidate path triage."""
import unittest

from research.field_validation.classify_upstream_replay_candidates import classify_paths


class CandidatePathClassificationTests(unittest.TestCase):
    def test_research_only_commit(self):
        result = classify_paths(["research/field_validation/analyze.py"], "research: add phase-a analysis")
        self.assertEqual(result["category"], "research_only")
        self.assertEqual(result["path_roots"], ["research"])

    def test_research_and_pipeline_commit_is_mixed(self):
        result = classify_paths(["research/analyze.py", "pipeline/run.py"], "fix research pipeline")
        self.assertEqual(result["category"], "research_mixed")
        self.assertEqual(result["path_roots"], ["pipeline", "research"])

    def test_pipeline_only_commit_is_not_research_only(self):
        result = classify_paths(["pipeline/run.py"], "fix pipeline")
        self.assertEqual(result["category"], "pipeline_only")

    def test_product_and_infrastructure_commit_is_not_research(self):
        result = classify_paths(["frontend/app.tsx", "supabase/migrations/001.sql"], "redesign")
        self.assertEqual(result["category"], "product_or_infrastructure")

    def test_preflight_tooling_is_separated_from_research_payload(self):
        result = classify_paths(["research/field_validation/preflight.sh"], "ci: add upstream replay preflight")
        self.assertEqual(result["category"], "preflight_tooling")

    def test_preflight_workflow_is_classified_by_path(self):
        result = classify_paths(
            [".github/workflows/upstream-replay-preflight.yml"],
            "ci(research): classify replay candidates without modifying refs",
        )
        self.assertEqual(result["category"], "preflight_tooling")

    def test_research_replay_workflow_is_classified_as_preflight_tooling(self):
        result = classify_paths(
            [".github/workflows/upstream-research-replay.yml"],
            "ci: add isolated upstream replay validation",
        )
        self.assertEqual(result["category"], "preflight_tooling")

    def test_candidate_classifier_and_its_tests_are_tooling(self):
        result = classify_paths(
            [
                "research/field_validation/classify_upstream_replay_candidates.py",
                "tests/test_ucip_replay_classification.py",
            ],
            "research: classify UCIP replay candidates without replaying",
        )
        self.assertEqual(result["category"], "preflight_tooling")

    def test_ucip_field_pilot_research_doc_is_classified_separately(self):
        result = classify_paths(
            ["docs/UCIP_FIELD_PILOT.md"],
            "docs(research): record identifier guard and validation limits",
        )
        self.assertEqual(result["category"], "research_documentation")

    def test_migration_audit_doc_is_preflight_tooling(self):
        result = classify_paths(
            ["docs/upstream-rewrite-migration-audit-20261110.md"],
            "docs: record UCIP preservation evidence and replay gate",
        )
        self.assertEqual(result["category"], "preflight_tooling")

    def test_empty_commit_is_explicit(self):
        result = classify_paths([], "empty commit")
        self.assertEqual(result["category"], "empty")


if __name__ == "__main__":
    unittest.main()
