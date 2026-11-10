#!/usr/bin/env bash
# Read-only upstream rewrite preflight. Run from a UCIP clone with upstream remote configured.
# Does not fetch, checkout, reset, rebase, cherry-pick, push, or modify tracked files.
set -euo pipefail
if [[ $# -ne 2 ]]; then
  echo "usage: $0 <rewritten-upstream-ref> <preserved-research-ref>" >&2
  exit 2
fi
upstream="$1"
preserved="$2"
git rev-parse --is-inside-work-tree >/dev/null
for ref in "$upstream" "$preserved"; do
  if ! git rev-parse --verify --quiet "${ref}^{commit}" >/dev/null; then
    echo "missing commit ref: $ref (fetch manually after verifying remote)" >&2
    exit 2
  fi
done
printf 'upstream_sha=%s\n' "$(git rev-parse "${upstream}^{commit}")"
printf 'preserved_sha=%s\n' "$(git rev-parse "${preserved}^{commit}")"
printf '\n=== divergence (not unique-patch counts) ===\n'
git rev-list --left-right --count "$upstream...$preserved"
printf '\n=== patch-equivalent candidate commits (review manually) ===\n'
git log --cherry-pick --right-only --no-merges --format='%H %s' "$upstream...$preserved"
printf '\n=== changed paths (not a replay plan) ===\n'
git diff --name-status "$upstream" "$preserved"
printf '\nNo changes made. Review candidates and dependencies before isolated replay.\n'
