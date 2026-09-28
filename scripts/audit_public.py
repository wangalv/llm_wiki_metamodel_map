#!/usr/bin/env python3
"""Fail if files that would be published contain obvious secrets or local state.

Scans every file git would publish: tracked files, plus untracked files that
.gitignore doesn't exclude. Without git, it scans the vault folder instead.

Checks:
- private keys, and API tokens/keys with well-known formats
- generic `api_key = "..."` style assignments
- machine-local paths, e.g. a home directory under /Users/ or /home/, or file:// URLs
- absolute symlink targets
- Obsidian plugin/workspace/cache state, OS junk, .env files, key files

To accept a false positive, add `audit-public: allow` to that line.
Standard library only. Exit code 1 means findings.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()
MAX_BYTES = 2_000_000
ALLOW_MARKER = "audit-public: allow"

PATH_RULES = [
    ("obsidian-workspace", re.compile(r"(^|/)\.obsidian/workspaces?(-mobile)?\.json$")),
    ("obsidian-plugin-data", re.compile(r"(^|/)\.obsidian/plugins/[^/]+/data\.json$")),
    ("obsidian-cache", re.compile(r"(^|/)\.obsidian/cache(/|$)")),
    ("obsidian-trash", re.compile(r"(^|/)\.trash/")),
    ("os-junk", re.compile(r"(^|/)(\.DS_Store|Thumbs\.db|desktop\.ini)$")),
    ("python-cache", re.compile(r"(^|/)__pycache__/|\.py[co]$")),
    ("tool-cache", re.compile(r"(^|/)(\.cache|node_modules|\.venv|venv)/")),
    ("env-file", re.compile(r"(^|/)\.env(\.(?!example$)[^/]+)?$")),
    ("key-file", re.compile(r"\.(pem|key|p12|pfx|keystore|jks)$")),
    ("ssh-key", re.compile(r"(^|/)id_(rsa|dsa|ecdsa|ed25519)$")),
]

CONTENT_RULES = [
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("openai-key", re.compile(r"\bsk-(?!ant-)(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("stripe-key", re.compile(r"\b[rs]k_live_[0-9A-Za-z]{16,}")),
    ("generic-secret", re.compile(
        r"(?i)\b(?:api[_-]?key|secret(?:[_-]?key)?|access[_-]?token|auth[_-]?token|password|passwd)\b"
        r"[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_\-/+=.]{16,}")),
    ("local-path", re.compile(r"(?:/Users/|/home/)[A-Za-z0-9._-]+/|\b[A-Za-z]:\\Users\\|file:///")),  # audit-public: allow (pattern text, not a real path)
]


def repo_root() -> Path | None:
    try:
        out = subprocess.run(["git", "-C", str(VAULT), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return Path(out.stdout.strip()) if out.returncode == 0 and out.stdout.strip() else None


def candidate_files(root: Path, use_git: bool) -> list[str]:
    if use_git:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             capture_output=True, timeout=60, check=True)
        return sorted({p for p in out.stdout.decode("utf-8", "replace").split("\0") if p})
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        files += [(Path(dirpath) / f).relative_to(root).as_posix() for f in filenames]
    return sorted(files)


def redact(text: str) -> str:
    return text[:6] + "…" if len(text) > 6 else text


def audit(root: Path, files: list[str]) -> list[tuple[str, int, str, str]]:
    findings = []
    for rel in files:
        path = root / rel
        for rule, rx in PATH_RULES:
            if rx.search(rel):
                findings.append((rel, 0, rule, "file should not be published"))
        if path.is_symlink():
            target = os.readlink(path)
            if os.path.isabs(target):
                findings.append((rel, 0, "absolute-symlink", f"points to {target}"))
            continue
        if not path.is_file() or path.resolve() == SELF or path.stat().st_size > MAX_BYTES:
            continue
        data = path.read_bytes()
        if b"\0" in data[:8192]:
            continue  # binary
        for lineno, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            if ALLOW_MARKER in line:
                continue
            for rule, rx in CONTENT_RULES:
                m = rx.search(line)
                if m:
                    findings.append((rel, lineno, rule, redact(m.group(0))))
    return findings


def main() -> int:
    root = repo_root()
    use_git = root is not None
    root = root or VAULT
    files = candidate_files(root, use_git)
    findings = audit(root, files)
    for rel, line, rule, detail in findings:
        loc = f"{rel}:{line}" if line else rel
        print(f"FAIL {rule:20} {loc}  {detail}")
    scope = "git-publishable files" if use_git else "files under the vault"
    print(f"audit_public: {len(findings)} finding(s) in {len(files)} {scope}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
