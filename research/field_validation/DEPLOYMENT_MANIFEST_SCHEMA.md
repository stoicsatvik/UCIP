# Phase A deployment provenance: proposed manifest (not yet implemented)

**Status:** Research design note, not a claim of deployment, validation, or
approval. The current analyzer infers a campaign window from observed timestamps.
This cannot distinguish four days of deployment from seven days with three days
of missing measurements.

Before interpreting the aggregate feasibility gate as conclusive, require a
versioned JSON deployment manifest recording:

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

Synthetic regression requirements: missing manifest is inconclusive; a
four-day declared deployment is inconclusive; four observed days inside a
declared seven-day deployment require explicit logs for absent site-days;
observations outside the declared window invalidate the manifest; a valid
seven-day declaration retains existing four-pair direction-gate behavior.

No real measurements or field permissions exist in this repository.
