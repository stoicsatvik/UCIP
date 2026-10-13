# UCIP field-validation pilot: external validity before causal claims

**Status:** Proposed research protocol. No sensors deployed, measurements collected, permissions obtained, or intervention effects estimated. This proposal is not endorsed by any correspondent.

## Question and design

Phase A tests whether satellite land-surface temperature (LST) preserves the direction of near-ground air-temperature contrasts in four preselected matched pairs of Mumbai sites. HVI combines multiple exposure and vulnerability variables, so this is **not** validation of HVI or a causal study.

Preselect eight sites in four matched pairs before looking at temperature outcomes. Record location, ward, canopy, surface type, traffic, wall proximity, logger placement and the satellite composite/overpass date. Co-locate and calibrate identical shielded temperature/RH loggers for 24 hours. Record offset, drift, clock sync and disruptions; stop if calibration is unstable. Deploy at approximately 1.5 m with appropriate permission and safety review for seven days, targeting ten-minute observations. Retain rain/cloud and missingness logs.

For each pair, compare exactly simultaneous corrected air temperatures between 12:00 and 16:00 Asia/Kolkata. Require at least 18 matched ten-minute intervals per pair-day and at least four valid days per pair. Analyze day-level paired contrasts and day-block bootstrap uncertainty, not hundreds of correlated intervals as independent observations. Publish all four pairs, including contradictions, missingness, and equal-LST cases. The aggregate direction gate is **inconclusive** unless all four pairs are eligible; with four eligible pairs, two or more contrary directions fail the feasibility gate. Passing does not establish ward-level or HVI accuracy.

Phase B is separate and optional, **only after permissions and safety review**: randomized AB/BA temporary-shade crossover at two suitable micro-sites, with characterized globe-temperature or another prespecified radiant-heat metric as the primary outcome. Record wind, cloud, solar exposure, geometry, spillover, failures and block assignments. Compare shaded versus concurrent unshaded radiant exposure using block-level randomization inference; ambient air temperature is secondary. Without successful randomization, label findings observational, not causal.

Freeze sites, inclusion/exclusion criteria, sensor calibration, time handling, script revision, randomization seed and raw-data storage before collecting observations. Do not publish sensitive site details. Preserve null/negative outcomes. No external outreach reply should claim this protocol is an endorsement.

## Reproducibility

Research-only implementation and synthetic tests: `research/field_validation/`. Run `python -m pytest -q research/field_validation/test_analyze_phase_a.py` after installing `numpy`, `pandas`, and `pytest`. No real-world results are bundled.
