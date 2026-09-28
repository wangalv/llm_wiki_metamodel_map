#!/usr/bin/env bash
# Point this repository's git hooks at the vault's .githooks/ folder.
# Safe to re-run. Undo with: git config --unset core.hooksPath
set -euo pipefail

vault="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
repo="$(git -C "$vault" rev-parse --show-toplevel)"

# core.hooksPath is relative to the repo root; the vault may be a subfolder.
rel="${vault#"$repo"}"
rel="${rel#/}"
hooks_path="${rel:+$rel/}.githooks"
# If the repo has a root dispatcher (several vaults in one repo), use it instead:
# it runs every vault's own .githooks/pre-commit.
if [ -x "$repo/.githooks/pre-commit" ] && [ -n "$rel" ]; then
    hooks_path=".githooks"
fi

chmod +x "$vault/.githooks/"* "$vault/scripts/"*.py "$vault/scripts/"*.sh
git -C "$repo" config core.hooksPath "$hooks_path"
echo "Installed git hooks: core.hooksPath = $hooks_path"
echo "Pre-commit runs: wiki_tool.py build, lint, source-lint; audit_public.py"
