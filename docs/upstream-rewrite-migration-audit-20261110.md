# UCIP upstream rewrite: preservation and replay audit (2026-11-10)

## Scope and evidence
Upstream maintainer reported rewriting history on 2026-10-17 to remove accidentally committed presentation files (AnayDhawan/UCIP discussion #264). A previous GitHub comparison of upstream commit `3295908` and fork `research/uncertainty-gate-20261015` reported 190 ahead, 331 behind, merge base `616a4e1`. These are history-divergence counts, **not** counts of unique research patches or proof of incompatibility.

Preserved branch references (do not force-push or delete):
- `preservation/uncertainty-gate-pre-upstream-rewrite-20261110`
- `preservation/field-validation-pre-upstream-rewrite-20261110`
- `preservation/dashboard-pre-upstream-rewrite-20261110`

On 2026-11-10 the uncertainty-gate preservation branch compared **identical** to `research/uncertainty-gate-20261015` (0 ahead, 0 behind, 0 changed files). This validates branch-tip equivalence for that pair only. Other preservation branches were created in the prior run; their tip equivalence has not been rechecked in this audit.

## Falsifiable migration experiment (not yet executed)
1. Record exact SHAs of all preservation refs and the current rewritten upstream default branch. Export immutable backups before any rewrite.
2. Identify fork-only work using `git log --cherry-pick --right-only --no-merges <upstream>...<preserved>` plus `git range-diff`; inspect patches manually because rewritten SHAs can make commit-count comparisons misleading.
3. Create an isolated replay branch from rewritten upstream. Cherry-pick *only* verified unique, relevant changes, ordered by dependency. Record every conflict and skipped patch. Never reset or force-push preservation branches.
4. Run repository test commands on both preserved and replay branches in the same environment; capture exit codes, failures, dependency versions, and relevant output. Compare schema and analysis behavior on identical fixtures, including negative/edge cases.
5. Accept replay only if expected research files and tests survive, no unexpected tracked files are removed, and regression tests pass. Otherwise retain the original preserved branches and document failed cases.

## Current result and limitations
**Preservation equivalence: PASS** for uncertainty-gate source vs preservation ref.
**Upstream replay: NOT RUN.** **Runtime tests: NOT RUN.** **Unique-patch classification: NOT DONE.**
No compatibility or scientific validity claim follows from preservation alone.

Next decision: inspect rewritten upstream tree and identify unique patches before constructing a replay branch.