# UCIP upstream rewrite: preservation and replay audit (2026-11-10)

## Scope and evidence

The upstream maintainer reported rewriting history on 2026-10-17 to remove accidentally committed presentation files (AnayDhawan/UCIP discussion #264). A previous GitHub comparison of upstream commit `3295908` and fork `research/uncertainty-gate-20261015` reported 190 ahead, 331 behind, merge base `616a4e1`. These are history-divergence counts, **not** counts of unique research patches or proof of incompatibility.

Preserved branch references (do not force-push or delete):

- `preservation/uncertainty-gate-pre-upstream-rewrite-20261110`
- `preservation/field-validation-pre-upstream-rewrite-20261110`
- `preservation/dashboard-pre-upstream-rewrite-20261110`

On 2026-11-10 the uncertainty-gate preservation branch compared **identically** to `research/uncertainty-gate-20261015` (0 ahead, 0 behind, 0 changed files). The field-validation and dashboard preservation refs were also rechecked against their respective source branches: both were identical, with 0 ahead, 0 behind, and 0 changed files. All three preservation branch tips are verified equivalent to their source branch tips. This verifies refs, not independently exported backups.

## Exact read-only preflight — 2026-11-10

GitHub Actions run [#42846797814](https://github.com/stoicsatvik/UCIP/actions/runs/42846797814) completed successfully on preflight branch commit `0db4a3e4cd19addc8855c5d67d1fd8ee1404a5fb`.

- Rewritten upstream SHA: `0ee822ded7e19a627934bcf4d499400ee99aea7e`
- Preserved preflight SHA: `0db4a3e4cd19addc8855c5d67d1fd8ee1404a5fb`
- Ancestry divergence: **345 upstream-only / 200 preserved-only** commits. These remain ancestry counts, not unique-patch counts.
- `git log --cherry-pick --right-only --no-merges` produced **39 commits not patch-equivalent to upstream** for manual review.
- The path classifier now reports: **17 research-only**, **1 research-mixed**, **8 preflight-tooling**, and **13 product/infrastructure** candidates.
- Exact-head preflight and classifier test workflows passed on commits `82ea3726797236923247393112cb2f101d7ce563` and `0db4a3e4cd19addc8855c5d67d1fd8ee1404a5fb` (runs [#42846791905](https://github.com/stoicsatvik/UCIP/actions/runs/42846791905) and [#42846797814](https://github.com/stoicsatvik/UCIP/actions/runs/42846797814)).

The first path-classification pass incorrectly labelled the workflow commit and classifier/test commit as product or mixed research work. The classifier was corrected to identify the preflight workflow, classifier module, and its tests by changed path. Two regression tests cover those cases. The corrected run moves those commits into `preflight_tooling`; this is a classification correction, not new scientific work.

### Research candidates requiring manual dependency review

The 17 research-only candidates are:

| Commit | Subject |
|---|---|
| `7975bba428` | test(research): regress non-string missingness site IDs |
| `036dbb4f90` | fix(research): reject non-string missingness site identifiers |
| `8f51d00460` | fix(research): preserve opaque site and pair IDs during CSV import |
| `16b8c92f91` | docs(research): record synthetic uncertainty fixture and remaining pairing debt |
| `2152d59d51` | test: supply synthetic uncertainty bounds in manifest fixture |
| `e6a81fc927` | fix(research): fail closed on unpreregistered air and LST direction uncertainty |
| `aa208482a9` | test(research): align manifest-gated fixtures and cover schema integrity |
| `1e1ede5606` | fix(research): reject contradictory manifests and treat zero contrasts as neutral |
| `ffb86aba0e` | test(research): align Phase A gate fixtures with deployment manifests |
| `8fd7606c25` | docs(research): record manifest gate implementation and unresolved regression validation |
| `c3beb40511` | research: require declared seven-day deployment provenance before conclusive Phase A gate |
| `aa0d0050c6` | docs(research): specify auditable deployment manifest gate |
| `b03cf2d4d6` | test(research): reject eight-day campaign despite four eligible pairs |
| `2c147427f0` | fix(research): make seven-calendar-day campaign window a fail-closed aggregate gate |
| `97e37b44ba` | docs(research): record identifier guard and validation limits |
| `8d04206392` | fix(research): reject missing and blank site identifiers before joins |
| `1f4a96e13c` | test(UCIP): cover calibration, missingness, negative results and burst cadence |
| `b66e73954f` | research(UCIP): add fail-closed matched-site temperature analysis |

The single research-mixed candidate is `ca4efc1774` (Phase A pair-mapping tests plus workflow/schema changes). It must be split or reviewed path-by-path before any replay decision.

The 8 preflight-tooling candidates belong to this audit branch and are not part of the UCIP research payload. The 13 product/infrastructure candidates include presentation, frontend, pipeline, and deployment changes; they are not candidates for the research-only replay.

**Classifier limitation:** categories are path/subject triage, not dependency closure, semantic equivalence, or replay safety. A research-only label does not mean a commit is independently replayable. The root-count summary counts path roots, not commits.

## Falsifiable replay gate — still not executed

1. Manually inspect the 17 research-only and one mixed candidate diffs in dependency order. Record prerequisites, shared files, and any behavior coupled to product/pipeline code.
2. Compare the rewritten upstream tree and candidate patch contents; path classification alone is insufficient.
3. Create an isolated replay branch from rewritten upstream. Cherry-pick only verified, relevant patches in dependency order. Record conflicts and skipped patches.
4. Run preserved and replayed research tests in the same environment; capture dependency versions, exit codes, and negative/edge-case outputs.
5. Accept replay only if expected research files and tests survive, no unexpected tracked files are removed, and the same fixtures produce equivalent analysis behavior.

**Preservation branches remain untouched. No replay has been performed. Runtime tests on a replay branch have not been run.** No compatibility or scientific-validity claim follows from preservation or path triage alone.

Next decision: manually review the 18 research candidates and their dependency chain before constructing any replay branch.
