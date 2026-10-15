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


## Frozen pair-mapping contract (15 October 2026)

The manifest now requires `preselected_pairs`, an explicit list of objects with
`pair_id` and exactly two distinct `site_ids` each. Pair IDs must be unique,
and the declared mapping must exactly match the analysis site table.
Missing, malformed, duplicate, or mismatched mappings force an inconclusive
aggregate decision while preserving descriptive results.

This prevents silently changing the sites CSV without also changing the
manifest. **It is not proof of prospective preregistration**: a party controlling
both files could rewrite both after seeing outcomes. Any field study must
publish an immutable, independently timestamped protocol/manifest hash before
data collection. Synthetic uncertainty bounds in the tests are illustrative,
not calibrated field thresholds. No field evidence or deployment is claimed.

The dedicated research CI workflow runs synthetic pytest on branch pushes.
Passing tests would establish software behavior for that exact revision only,
not scientific validity or deployment provenance.

## Opaque CSV identifiers and inferential limits (16 October 2026)

CSV `pair_id` and `site_id` are categorical identifiers. Import them as strings
without pandas' default missing-value token coercion: `001` must remain distinct
from `1`, and literal `NA`, `NULL`, `N/A`, and `nan` are valid labels.
Truly empty or whitespace-only identifiers remain invalid. The synthetic
regression suite checks identifier preservation, pair-manifest matching,
and the existing missing-ID rejection contract.

The day-block bootstrap interval is **descriptive**. A preregistered
direction-count rule can return `fail` even when an individual pair's
bootstrap interval crosses zero. That result must not be described as a
statistically significant effect or proof of causal validation. Changing the
falsification rule after observing outcomes would be post-hoc; report both
the rule-based decision and interval uncertainty, including negative results.

No field measurements, sensor calibration evidence, or independent
preregistration timestamp are supplied by these changes.
