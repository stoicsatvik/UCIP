"""Read-only path triage for commits not patch-equivalent to rewritten UCIP upstream.

This is a review aid only. Path categories do not establish dependency closure,
semantic compatibility, or permission to replay a commit.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout


def classify_paths(paths: list[str], subject: str = "") -> dict:
    roots = sorted({path.split("/", 1)[0] if "/" in path else "<root>" for path in paths})
    lower = subject.lower()
    if "preflight" in lower or "candidate classifier" in lower:
        category = "preflight_tooling"
    elif not paths:
        category = "empty"
    elif roots == ["research"]:
        category = "research_only"
    elif "research" in roots:
        category = "research_mixed"
    elif roots == ["pipeline"]:
        category = "pipeline_only"
    else:
        category = "product_or_infrastructure"
    return {"category": category, "path_roots": roots, "paths": sorted(paths)}


def classify(upstream: str, preserved: str) -> dict:
    for ref in (upstream, preserved):
        git("rev-parse", "--verify", f"{ref}^{{commit}}")
    left, right = map(int, git("rev-list", "--left-right", "--count", f"{upstream}...{preserved}").split())
    raw = git("log", "--cherry-pick", "--right-only", "--no-merges",
              "--format=%H%x09%s", f"{upstream}...{preserved}")
    candidates = []
    for line in raw.splitlines():
        sha, subject = line.split("\t", 1)
        paths = git("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", sha).splitlines()
        candidates.append({
            "sha": sha,
            "subject": subject,
            **classify_paths(paths, subject),
        })
    category_counts = Counter(item["category"] for item in candidates)
    root_counts = Counter(root for item in candidates for root in item["path_roots"])
    return {
        "schema": "ucip-upstream-candidate-triage-v1",
        "upstream_ref": upstream,
        "preserved_ref": preserved,
        "ancestry_divergence": {
            "upstream_only_commits": left,
            "preserved_only_commits": right,
        },
        "patch_non_equivalent_candidate_count": len(candidates),
        "candidate_category_counts": dict(sorted(category_counts.items())),
        "candidate_path_root_counts": dict(sorted(root_counts.items())),
        "candidates": candidates,
        "claim_boundary": (
            "Path-based triage only. This does not prove dependency closure, "
            "patch applicability, semantic compatibility, or safe replay."
        ),
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m research.field_validation.classify_upstream_replay_candidates <upstream-ref> <preserved-ref>")
    print(json.dumps(classify(sys.argv[1], sys.argv[2]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
