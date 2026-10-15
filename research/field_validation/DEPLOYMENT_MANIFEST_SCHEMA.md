# Phase A deployment provenance: declared manifest gate

**Status:** Research-only prototype integrated into the analyzer on this draft branch; not a claim of deployment, field validation, or approval. Observed timestamps alone cannot distinguish four days of deployment from seven days with three days of missing measurements. The declaration is not independently verified.

The analyzer now accepts an optional JSON declaration via `--manifest`. Without a valid declaration, its aggregate gate remains inconclusive. The declaration records:

- Exact local deployment start and end (UTC offsets, seven complete days).
- The complete set of preselected site identifiers.
- A reviewed missingness log for each wholly unobserved site-day, including
  dates and a reason or an explicit "cause unknown" entry.
- A flag making clear that the manifest is a declaration, **not independent
  proof** of actual sensor operation.

A missing, incomplete, or contradictory manifest should force an
**inconclusive** aggregate gate while retaining descriptive pair contrasts,
contradictory directions, and null outcomes. Never silently exclude absent
days or infer deployment duration from the first and last observed timestamp.

Synthetic regression requirements (local prototype passed 20 tests on October 14, 2026; exact committed revision and CI not yet verified): missing manifest is inconclusive; a
four-day declared deployment is inconclusive; four observed days inside a
declared seven-day deployment require explicit logs for absent site-days;
observations outside the declared window invalidate the manifest; a valid
seven-day declaration retains existing four-pair direction-gate behavior.

No real measurements or field permissions exist in this repository.

## Validation debt (October 14, 2026)

The analyzer now requires a manifest for a conclusive four-pair gate, but the
previously committed `test_four_complete_pairs_support_a_falsification_decision`
fixture does not supply one. It therefore has an obsolete expectation and must
be updated alongside the expanded regression tests before this PR can pass its
research-specific test suite. Attempts to update that test file were blocked;
no exact-commit CI claim is made. Keep this PR in draft.

Run `python -m pytest -q research/field_validation/test_analyze_phase_a.py`
after correcting the fixture. Add dedicated CI for the research suite. No
field data or human validation is included.

## Synthetic uncertainty fixture update (15 October 2026)

The test helper now declares illustrative 0.05°C air and LST direction
uncertainty bounds with explicit synthetic-only rationale. These are not
empirical sensor uncertainty estimates and must not be used to justify field
claims. This change fixes the fixture contract but does not establish that
the exact committed branch passes tests.

The deployment manifest still does not lock the mapping of sites to matched
pairs. Reassigning the same eight sites can change the aggregate decision.
Before interpreting a field result, require a frozen pair-to-site mapping,
regression tests for reassignment, and passing exact-commit CI.
