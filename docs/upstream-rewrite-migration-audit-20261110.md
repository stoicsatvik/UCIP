# UCIP upstream rewrite: preservation and replay audit (2026-11-10)

## Scope and evidence

The upstream maintainer reported rewriting history on 2026-10-17 to remove accidentally committed presentation files (AnayDhawan/UCIP discussion #264). The migration audit compares preserved research history with rewritten upstream. Ancestry counts are not unique-patch counts and do not prove incompatibility.

Preserved branch references (do not force-push or delete):

- \`preservation/uncertainty-gate-pre-upstream-rewrite-20261110\`
- \`preservation/field-validation-pre-upstream-rewrite-20261110\`
- \`preservation/dashboard-pre-upstream-rewrite-20261110\`

All three preservation branch tips were rechecked against their source branches on 2026-11-10. Each comparison was identical: 0 ahead, 0 behind, 0 changed files. This verifies branch refs, not independently exported backups.

## Preflight history

### First exact preflight snapshot

GitHub Actions run [#42846797814](https://github.com/stoicsatvik/UCIP/actions/runs/42846797814) completed successfully on commit \`0db4a3e4cd19addc8855c5d67d1fd8ee1404a5fb\`.

- Ancestry divergence: 345 upstream-only / 200 preserved-only.
- Patch-non-equivalent candidates: 39.
- Path categories: 17 research-only, 1 research-mixed, 8 preflight-tooling, 13 product/infrastructure.

### Latest exact preflight snapshot

GitHub Actions run [#42849376944](https://github.com/stoicsatvik/UCIP/actions/runs/42849376944) completed successfully on preserved branch commit \`ab44d5c829f61156a2946296e580f1af026248ce\`.

- Rewritten upstream SHA: \`0ee822ded7e19a627934bcf4d499400ee99aea7e\`.
- Preserved branch SHA: \`ab44d5c829f61156a2946296e580f1af026248ce\`.
- Ancestry divergence: **345 upstream-only / 202 preserved-only**.
- Commits not patch-equivalent to upstream: **41**.
- Path categories: **17 research-only**, **3 research-documentation**, **1 research-mixed**, **12 preflight-tooling**, **8 product/infrastructure**.
- Artifact [#13780275614](https://github.com/stoicsatvik/UCIP/actions/runs/42849376944) preserves the preflight log and machine-readable candidate triage.

The earlier preflight workflow run failed because its \`tee\` output was written inside the checkout, so the read-only worktree comparison detected an untracked file. Commit \`4dc9d013e16e255b419e894e29bbc7b70ccb342d\` moved the receipt to \`$RUNNER_TEMP\`. The latest run passed and preserved the clean-worktree check.

The first path-classification pass also mislabelled some audit tooling as product or mixed research work. The classifier was corrected to identify the workflow, classifier module, and their tests by changed path. Regression tests cover those cases. This is a classification correction, not new scientific work.

## Research-related candidates requiring manual dependency review

The 17 research-only candidates are:

| Commit | Subject |
|---|---|
| \`7975bba428\` | test(research): regress non-string missingness site IDs |
| \`036dbb4f90\` | fix(research): reject non-string missingness site identifiers |
| \`8f51d00460\` | fix(research): preserve opaque site and pair IDs during CSV import |
| \`16b8c92f91\` | docs(research): record synthetic uncertainty fixture and remaining pairing debt |
| \`2152d59d51\` | test: supply synthetic uncertainty bounds in manifest fixture |
| \`e6a81fc927\` | fix(research): fail closed on unpreregistered air and LST direction uncertainty |
| \`aa208482a9\` | test(research): align manifest-gated fixtures and cover schema integrity |
| \`1e1ede5606\` | fix(research): reject contradictory manifests and treat zero contrasts as neutral |
| \`ffb86aba0e\` | test(research): align Phase A gate fixtures with deployment manifests |
| \`8fd7606c25\` | docs(research): record manifest gate implementation and unresolved regression validation |
| \`c3beb40511\` | research: require declared seven-day deployment provenance before conclusive Phase A gate |
| \`aa0d0050c6\` | docs(research): specify auditable deployment manifest gate |
| \`b03cf2d4d6\` | test(research): reject eight-day campaign despite four eligible pairs |
| \`2c147427f0\` | fix(research): make seven-calendar-day campaign window a fail-closed aggregate gate |
| \`97e37b44ba\` | docs(research): record identifier guard and validation limits |
| \`8d04206392\` | fix(research): reject missing and blank site identifiers before joins |
| \`1f4a96e13c\` | test(UCIP): cover calibration, missingness, negative results and burst cadence |
| \`b66e73954f\` | research(UCIP): add fail-closed matched-site temperature analysis |

The three research-documentation candidates are:

| Commit | Subject |
|---|---|
| \`202cfc2e23\` | docs(research): preregister UCIP matched-site heat validation protocol |
| \`3e0b267700\` | docs(research): document conservative seven-day fail-closed gate |
| \`97e37b44ba\` | docs(research): record identifier guard and validation limits |

The research-mixed candidate is \`ca4efc1774\` (Phase A pair-mapping tests plus workflow/schema changes). It must be split or reviewed path-by-path before any replay decision.

The 12 preflight-tooling candidates belong to this audit branch and are not part of the UCIP research payload. The 8 product/infrastructure candidates include presentation, frontend, pipeline, and deployment changes; they are not candidates for the research-only replay.

## Classifier limitation

Categories are path/subject triage, not dependency closure, semantic equivalence, or replay safety. A research-only label does not mean a commit is independently replayable. The root-count summary counts path roots, not commits. This document's latest numeric snapshot is pinned to run #42849376944 at commit \`ab44d5c\`; later audit-document commits may themselves appear as preflight-tooling candidates in subsequent snapshots.

## Falsifiable replay gate — still not executed

1. Manually inspect the 17 research-only, 3 research-documentation, and 1 mixed candidate diffs in dependency order. Record prerequisites, shared files, and behavior coupled to product/pipeline code.
2. Compare rewritten-upstream tree contents and candidate patch contents; path classification alone is insufficient.
3. Create an isolated replay branch from rewritten upstream. Cherry-pick only verified, relevant patches in dependency order. Record conflicts and skipped patches.
4. Run preserved and replayed research tests in the same environment; capture dependency versions, exit codes, and negative/edge-case outputs.
5. Accept replay only if expected research files and tests survive, no unexpected tracked files are removed, and the same fixtures produce equivalent analysis behavior.

**Preservation branches remain untouched. No replay has been performed. Runtime tests on a replay branch have not been run.** No compatibility or scientific-validity claim follows from preservation or path triage alone.

Next decision: manually review the 21 research-related candidates and their dependency chain before constructing any replay branch.
