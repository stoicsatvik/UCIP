# UCIP upstream rewrite: preservation and replay audit (2026-11-10)

## Scope and evidence

The upstream maintainer reported rewriting history on 2026-10-17 to remove accidentally committed presentation files (AnayDhawan/UCIP discussion #264). The migration audit compares preserved research history with rewritten upstream. Ancestry counts are not unique-patch counts and do not prove incompatibility.

**Current status (10 November 2026):** the reviewed 21-commit research chain has now been replayed in an isolated runner against rewritten upstream `500c3d793b89a538aac7680a270f4ef19c722685`. The current artifact-only workflow passed 33/33 Phase A tests, Python compilation, `git diff --check`, path allowlist and clean-worktree checks. No remote replay branch was pushed. See [the updated replay result](../research/field_validation/UPSTREAM_REPLAY_RESULT_20261110.md) and [draft PR #3](https://github.com/stoicsatvik/UCIP/pull/3). The earlier failed publication attempt is retained below as a separate negative result.

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

## Historical pre-replay gate — superseded by the 10 November isolated replay

Historical plan before the replay: manually inspect the 17 research-only, 3 research-documentation, and 1 mixed candidate diffs in dependency order. Record prerequisites, shared files, and behavior coupled to product/pipeline code.
2. Compare rewritten-upstream tree contents and candidate patch contents; path classification alone is insufficient.
3. Create an isolated replay branch from rewritten upstream. Cherry-pick only verified, relevant patches in dependency order. Record conflicts and skipped patches.
4. Run preserved and replayed research tests in the same environment; capture dependency versions, exit codes, and negative/edge-case outputs.
5. Accept replay only if expected research files and tests survive, no unexpected tracked files are removed, and the same fixtures produce equivalent analysis behavior.

At the time of this historical snapshot, preservation branches remained untouched and replay/runtime tests had not yet been run. The later isolated replay result is recorded above and in the linked result document. No scientific-validity claim follows from preservation or path triage alone.

Current next decision: review the artifact and exact replay tree, then obtain independent review before any remote publication. Do not merge, force-push, or modify the three preservation branches.


## Follow-up: 10 November 2026 — refreshed candidate set and dependency review

The latest read-only preflight is GitHub Actions run [#42854776440](https://github.com/stoicsatvik/UCIP/actions/runs/42854776440), against upstream `0ee822ded7e19a627934bcf4d499400ee99aea7e` and preserved/audit snapshot `e1ccf2e6c21b55e9679cfd7668a367f2bcdba774`.

- Ancestry divergence: 345 upstream-only and 204 preserved-only commits. These are graph counts, not unique-patch counts.
- Patch-non-equivalent candidates: 43 total.
- Path classification: 17 research-only, 3 research-documentation, 1 research-mixed, 14 preflight-tooling, and 8 product/infrastructure.
- The 21 research-related candidates form one linear dependency chain from `202cfc2e2349df60164f1373d5650ad2929799ee` through `7975bba4280ff257d7d781043f84f25681dbcb8f`. Parent links were checked commit by commit.
- The one mixed commit, `ca4efc17746029c3bd0bbc8b8ae9f733de3b6c32`, changes only the Phase A research workflow, research schema, analyzer, and research tests. It does not touch product/frontend/pipeline code. It is included in the isolated replay set because later research commits depend on its manifest and pair-mapping changes.
- The three documentation candidates are confined to the Phase A field-pilot and deployment-manifest research documents. The 17 research-only candidates modify the analyzer and its tests.

A new read-only CI workflow, `.github/workflows/upstream-research-replay.yml`, now tests this exact 21-commit chain on a temporary branch based on the current rewritten upstream main. It verifies the linear parent chain and path allowlist, cherry-picks in dependency order, runs the Phase A regression suite, and pushes a separate fork branch only if every check passes. It does not modify main or any preservation branch.

The first workflow attempt, run [#42859498812](https://github.com/stoicsatvik/UCIP/actions/runs/42859498812), failed before replay because one manifest SHA was missing its final character. The artifact was retained; the SHA and shell escaping were corrected in commit `fbc628ca0e22953e9422097c00cecd912b198e74`. The corrected run [#42859637487](https://github.com/stoicsatvik/UCIP/actions/runs/42859637487) is the authoritative replay attempt and is pending at the time of this update.

No destructive sync, force push, merge, or change to the three preserved branch tips has been performed. A clean software replay would establish patch compatibility only, not scientific validity or permission to submit/merge the research into upstream.


### Isolated replay attempt 2: code passes, push authorization blocked

Run [#42859637487](https://github.com/stoicsatvik/UCIP/actions/runs/42859637487) applied all 21 source commits in dependency order onto the fetched rewritten upstream main. There were no cherry-pick conflicts or empty commits. The replayed Phase A suite passed **33 tests in 0.90 seconds**, Python compilation passed, the final diff stayed within the research allowlist, and the local worktree was clean. The runner created replay commit `167c09f0b07d5dc031be474e8c5b6b9b7d0df8e2`.

The remote branch push was rejected because the GitHub App token lacks the separate `workflows` permission required to push the mixed source commit's `.github/workflows/phase-a-research.yml`. This is an authorization failure after successful replay and tests, not a cherry-pick or research-test failure. Artifact [#13783024951](https://github.com/stoicsatvik/UCIP/actions/runs/42859637487) preserves the complete run receipt.

The replay workflow now path-splits that mixed commit: it retains the research schema, analyzer, and tests while omitting the dedicated Phase A workflow file. The same research suite is executed directly by the replay workflow. The resulting branch will contain no workflow-file changes, so no extra permission is needed. This keeps the compatibility experiment isolated and does not weaken the research tests.


## Follow-up: 11 November 2026 — exact preflight of all preserved branches

The previous read-only preflight workflow compared the audit/tooling branch `HEAD` with rewritten upstream. That was useful for validating the classifier, but it did **not** independently re-run the preflight against each preserved research/product branch. The workflow now fetches the three source/preservation pairs, verifies each preservation ref is exactly equal to its source branch tip, and runs the read-only preflight plus path-only candidate classifier against each preserved ref. It does not checkout, reset, rebase, cherry-pick, push, or modify any preserved ref.

Exact-head workflow: [#42951221494](https://github.com/stoicsatvik/UCIP/actions/runs/42951221494). The workflow and Phase A PR checks passed; the classifier suite passed **11/11**. Artifact [#13825192105](https://github.com/stoicsatvik/UCIP/actions/runs/42951221494/artifacts/13825192105), SHA-256 `82266e6ee3e6782ce38d7682404b7d4158f3a0811375172f8750f2dbdfdd8ba6`, contains one preflight log and one machine-readable candidate report for each preserved branch.

The upstream main SHA was `500c3d793b89a538aac7680a270f4ef19c722685`. All three preservation refs still exactly match their source branch tips:

| Source branch | Preserved branch | Preserved SHA | Source-tip comparison |
|---|---|---|---|
| `research/field-validation-protocol-20261013` | `preservation/field-validation-pre-upstream-rewrite-20261110` | `aa208482a9cc92bfd8a116c228b43d501aab27f3` | identical, 0 ahead / 0 behind |
| `research/uncertainty-gate-20261015` | `preservation/uncertainty-gate-pre-upstream-rewrite-20261110` | `7975bba4280ff257d7d781043f84f25681dbcb8f` | identical, 0 ahead / 0 behind |
| `codex/ucip-dashboard-issues` | `preservation/dashboard-pre-upstream-rewrite-20261110` | `22d5fe9a3d2e650ec4735250c4a86eba922b39b3` | identical, 0 ahead / 0 behind |

Current preserved-branch preflight results (ancestry counts are not unique-patch counts):

| Preserved branch | Upstream-only | Preserved-only | Patch-non-equivalent candidates | Path-only candidate categories |
|---|---:|---:|---:|---|
| Field validation | 348 | 183 | 22 | 11 research-only, 3 research-documentation, 8 product/infrastructure |
| Uncertainty gate | 348 | 190 | 29 | 17 research-only, 3 research-documentation, 1 research-mixed, 8 product/infrastructure |
| Dashboard | 348 | 171 | 10 | 10 product/infrastructure |

The fork's `main` remains on the pre-rewrite history: current cross-repository comparison reports **169 fork-only / 348 upstream-only** commits. This is a graph relationship, not a unique-patch count. Do not force-sync, delete, rebase, or merge the fork's main branch. The successful 21-commit isolated Phase A replay remains a separate, artifact-only compatibility result; it does not authorize publishing or merging that replay.

The classifier's categories are path/subject triage only. The 22/29/10 candidates are not replay plans, dependency-closed sets, or proof of incompatibility. In particular, the single mixed uncertainty-gate candidate still requires path-level review, and all research-only candidates require dependency and semantic review before any isolated replay. No remote replay branch was pushed and no preservation branch was changed.

Communication note: the factual acknowledgement sent from BuildWithSatvik to the GitHub notification address `notifications@github.com` after the maintainer's Discussion #264 notice was rejected with SMTP `554 5.2.2 mailbox full`. No retry or alternate-address outreach was made. The maintainer's history-rewrite instruction was followed conservatively by preserving the old refs and avoiding force-sync.
