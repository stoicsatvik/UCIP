# UCIP rewritten-upstream replay result (10 November 2026)

## Executed result

- Workflow run: [42860180047](https://github.com/stoicsatvik/UCIP/actions/runs/42860180047)
- Rewritten upstream base: `0ee822ded7e19a627934bcf4d499400ee99aea7e`
- Source preservation/audit snapshot: `f9b59606bc048b3f5f6b7400dd0e71cd88eb094d`
- Reviewed source chain: 21 commits; linear parent chain verified. Twenty commits applied normally and one mixed commit was path-split to retain research files while omitting its dedicated workflow file.
- Replayed tree paths: `docs/UCIP_FIELD_PILOT.md`, `research/field_validation/DEPLOYMENT_MANIFEST_SCHEMA.md`, `research/field_validation/analyze_phase_a.py`, and `research/field_validation/test_analyze_phase_a.py`.
- Replay head before the generated result note: `1b40bd9764060db31d8b3346329ad21b7fb22349`.
- Generated result-note commit in the isolated runner: `a4c23cfab72bd96558c02e47348eeb6e6c5fb8cf`.
- Validation: Python compilation passed, Phase A regression suite **33/33 passed in 1.33 s**, `git diff --check` passed, and the replay worktree was clean.
- Artifact: [ucip-isolated-research-replay.zip](https://github.com/stoicsatvik/UCIP/actions/runs/42860180047/artifacts/13785280748), SHA-256 `f6bb12f388389aa77100ddbf7da7af324caa2a240c3588f642b33eacf27f505a`.

## Preserved publication failure

The replay and regression checks passed, but the original workflow revision then attempted to push the isolated replay branch to the fork. GitHub rejected that push because the GitHub App token lacked `workflows` permission for `.github/workflows/alert-on-failure.yml`, which is present in rewritten upstream but not in the fork's main branch. The workflow run therefore ended red **after** the replay tests passed. The remote replay branch was not created.

The replay workflow was then changed to artifact-only publication: it uses read-only contents permission and never attempts the blocked push. The original publication failure remains preserved as a historical negative result; the successful rerun is recorded below.

## Successful artifact-only rerun — 10 November 2026

- Workflow run: [#42875507558](https://github.com/stoicsatvik/UCIP/actions/runs/42875507558), completed successfully.
- Current rewritten upstream base: `500c3d793b89a538aac7680a270f4ef19c722685`.
- Source preflight branch snapshot: `dcb7bfe66a95c8437ea2092c921e202e43e2ecb7`.
- The reviewed 21-commit linear research chain replayed without cherry-pick conflicts. The mixed workflow/schema commit was path-split to retain research code, schema and tests while omitting its dedicated workflow file.
- Replay head before the generated result note: `2e464b898b9c32c02f8d47a8b7c6ffc47f4eef9b`.
- Final local replay branch SHA: `42d6e0f73f54cccbb8a29119ba09e77ab058ecbf`.
- Phase A regression suite: **33 passed in 1.24 s**. Python compilation, `git diff --check`, path allowlist checks and clean-worktree verification also passed.
- Artifact: [ucip-isolated-research-replay.zip](https://github.com/stoicsatvik/UCIP/actions/runs/42875507558/artifacts/13791781928), SHA-256 `3776e1bec2edfd98e09bf4146335387ae04653a29aed5afe633ab10dc0315d84`.
- Publication remains artifact-only. No remote replay branch was pushed; all three preservation branches remain untouched.

This is a successful software-compatibility replay against the current rewritten-upstream SHA, not scientific validation, a merge, or permission to publish the replay into upstream.

## Scope and limits

- The three preservation branches were not modified.
- Product, frontend, and pipeline files were not replayed.
- The Phase A protocol, analyzer, tests, and schema were checked for software compatibility only.
- No field measurements, independent deployment provenance, empirical sensor-uncertainty calibration, or causal HVI validation were established.
- A clean synthetic regression replay is not scientific validation and is not permission to merge into upstream.

## Next gate

Use the artifact to review the exact isolated tree. If a remote replay branch is required, obtain an explicitly authorized workflow-capable token or publish a separately reviewed tree that does not introduce upstream workflow files. Do not broaden permissions automatically.
