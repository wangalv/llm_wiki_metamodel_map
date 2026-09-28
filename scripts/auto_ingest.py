#!/usr/bin/env python3
"""auto_ingest.py — call an external LLM API to draft compiled notes from one Raw
source, so an ingest can run from the command line without a human driving an
interactive agent session.

Design (confirmed with the vault's maintainer before this was built):
  1. Multi-provider, switchable at the command line: Anthropic, OpenAI, or any
     OpenAI-compatible endpoint. Not locked to one vendor.
  2. Single-shot: one API call, no agentic retry/auto-fix loop. Quality control
     stays the existing human-review mechanism (status: seed + the generated
     review-queue table), not an automated one.
  3. A separate script, not a wiki_tool.py subcommand, so wiki_tool.py keeps its
     "deterministic tool, no network calls, no model judgment" design.

Usage:
    export ANTHROPIC_API_KEY=...
    python3 scripts/auto_ingest.py Raw/Sources/2026-09-27-some-source.md

    export OPENAI_API_KEY=...
    python3 scripts/auto_ingest.py Raw/Sources/...md --provider openai --model gpt-4o

    # Any OpenAI-compatible endpoint (self-hosted, a third-party host, etc.):
    python3 scripts/auto_ingest.py Raw/Sources/...md --provider openai-compatible \\
        --base-url https://your-host/v1 --model your-model --api-key-env YOUR_KEY_ENV

    python3 scripts/auto_ingest.py Raw/Sources/...md --dry-run   # preview, write nothing

Instead of exporting the key each time, copy .env.example to .env at the vault
root and fill in your own key(s) there — this script loads it automatically
(a real shell-exported variable always wins over .env). .env is gitignored and
never read by any other tool here; nothing in this vault writes to it.

What it does:
  - Reads AGENTS.md, the ingest skill, the active profile's spec, and
    Schema/field-reference.md (generated from Schema/wiki-config.json), plus the
    source file and the existing catalog, and assembles one prompt.
  - Asks the model for structured notes: only the semantic content a human/agent
    would decide (kind, title, topics, aliases, summary, body, and this kind's
    extra fields such as classification_basis) — never the mechanical frontmatter
    (tags/status/created/updated/sources/source_count), which this script derives
    itself from Schema/wiki-config.json so it can never drift from what the
    engine expects.
  - Writes one .md file per note under Wiki/<folder>/, refusing to overwrite any
    file that already exists (an existing file is skipped and reported, never
    silently replaced).
  - Runs wiki_tool.py build / lint / source-scan --update --accept-covered / log
    afterwards, the same as a human-driven ingest would, and prints the results.

This script never retries or "fixes" a bad model answer. If something looks
wrong, it prints what it would have written (or, without --dry-run, what it
skipped and why) and stops — a person reviews the rest by hand, the same way
they review any other seed note.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiki_tool as core  # reuse Config/Vault/FieldSpec/_yaml_field — never reimplement them

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-5",
    "openai": "gpt-5",
    "openai-compatible": None,  # the user must name one; there's no sane default
}
DEFAULT_API_KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openai-compatible": "OPENAI_API_KEY",
}
DEFAULT_BASE_URL = "https://api.openai.com/v1"
NOTE_FIELDS = ("kind", "title", "aliases", "topics", "summary", "body", "fields")
FILENAME_BAD_CHARS = re.compile(r'[\\/:*?"<>|#^\[\]]')


def die(message: str, code: int = 1) -> "NoReturn":
    print(f"auto_ingest.py: {message}", file=sys.stderr)
    sys.exit(code)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def load_dotenv(root: Path) -> None:
    """Load KEY=VALUE lines from a .env file at the vault root into os.environ.

    A variable already set in the real environment always wins over .env — this
    only fills in what isn't already there. .env is gitignored (see .env.example)
    and nothing else in this vault reads or writes it.
    """
    path = root / ".env"
    if not path.is_file():
        return
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            print(f"auto_ingest.py: .env:{lineno}: ignoring line without '=': {raw_line!r}", file=sys.stderr)
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------

def describe_kinds(cfg: "core.Config", topics_tag: str) -> str:
    req_word = {True: "required", "recommended": "recommended", False: "optional"}
    lines = [f"Grouping kind every note's `topics` field points into: `{topics_tag}` "
             f"(Wiki/{cfg.topics_folder}/)."]
    for k in cfg.kinds:
        if k.fields:
            extras = "; ".join(
                f"{f.name} ({f.describe_type()}, {req_word[f.required]}"
                + (f", one of {f.describe_values()}" if f.describe_values() else "") + f"): {f.description}"
                for f in k.fields
            )
        else:
            extras = "(none)"
        lines.append(f"- `{k.tag}` -> Wiki/{k.folder}/ | must cite sources: {k.requires_sources} "
                     f"| extra `fields`: {extras}")
    return "\n".join(lines)


def build_prompt(v: "core.Vault", source_rel: str, source_content: str, structured_via_tool: bool) -> str:
    cfg = v.cfg
    root = v.root
    topics_tag = cfg.by_folder[cfg.topics_folder].tag
    source_stem = Path(source_rel).stem
    profile_doc = read_text(root / "scripts" / "profiles" / cfg.profile / f"{cfg.profile}-profile.md")
    agents_md = read_text(root / "AGENTS.md")
    ingest_skill = read_text(root / ".agents" / "skills" / "llm-wiki-ingest" / "SKILL.md")
    field_reference = read_text(root / core.FIELD_REFERENCE)
    catalog = read_text(root / core.CATALOG).strip() or "(empty — this is the first ingest)"
    kind_summary = describe_kinds(cfg, topics_tag)

    format_instructions = (
        "" if structured_via_tool else
        'Return ONLY a single JSON object of the exact shape {"notes": [ ... ]} and nothing else '
        "(no prose before or after it, no code fence)."
    )

    return f"""You are doing a single ingest pass for an LLM Wiki vault: a cited knowledge base
built by turning Raw/ documents into Wiki/ notes, one Markdown file per compiled note.

Follow the rules below exactly. Read all of them before answering.

=== AGENTS.md (hard rules for agents working in this vault) ===
{agents_md}

=== Ingest skill ===
{ingest_skill}

=== Active profile ({cfg.profile}): note types, when to use each, how notes connect ===
{profile_doc}

=== Field reference (generated from Schema/wiki-config.json) ===
{field_reference}

=== Kind summary (derived directly from Schema/wiki-config.json; treat as authoritative
    over anything above if they ever disagree) ===
{kind_summary}

=== Notes already in the vault (Wiki/catalog.jsonl, one JSON object per line) ===
Do not recreate any of these. If something you're about to write already exists here
under a different name, put that existing title in `topics` or reference it in `body`
instead of duplicating it.
{catalog}

=== The source to ingest: {source_rel} ===
{source_content}

=== Your task ===
Read the source above in full. Identify every distinct instance of every kind listed in
the kind summary that the source names or clearly implies. Follow "no representative
sampling": if the source names five distinct instances of the same kind doing different
things, that is five notes, not one representative example — do not stop at the first
instance you find and assume that kind is "covered". Do not invent facts the source
doesn't support. Every citation must point at an exact heading that actually appears in
the source above, written as [[{source_stem}#Exact Heading Text|Exact Heading Text]] —
copy the heading text exactly, including punctuation.

Do NOT include these fields — the script reading your answer fills them in itself,
deterministically, from Schema/wiki-config.json, so they can never drift from what it
expects: tags, status, created, updated, sources, source_count.

For each note, return exactly these fields:
  - kind: one of the tags in the kind summary above
  - title: Title Case, the name other notes would already call it if it existed
  - aliases: array of other names this thing is called (may be [])
  - topics: array of titles of {topics_tag} note(s) this belongs under; reuse an
      existing one from the catalog above if it fits, otherwise you may name a new one
  - summary: one plain sentence, 200 characters or fewer, no citation in it
  - body: the rest of the note in Markdown (for example "## Explanation", "## Related"),
      with every claim cited in the [[{source_stem}#Heading|Heading]] format above
  - fields: an object holding this kind's extra fields from the kind summary above
      (for example classification_basis, where that field exists) — omit fields this
      kind doesn't have; fill in every field marked required

Return the full list of notes as structured output. {format_instructions}
""".strip() + "\n"


# ---------------------------------------------------------------------------
# Provider calls — stdlib only, no SDK dependency
# ---------------------------------------------------------------------------

NOTES_TOOL_SCHEMA = {
    "name": "emit_notes",
    "description": "Return the compiled notes to create from this source.",
    "input_schema": {
        "type": "object",
        "properties": {
            "notes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string"},
                        "title": {"type": "string"},
                        "aliases": {"type": "array", "items": {"type": "string"}},
                        "topics": {"type": "array", "items": {"type": "string"}},
                        "summary": {"type": "string"},
                        "body": {"type": "string"},
                        "fields": {"type": "object"},
                    },
                    "required": ["kind", "title", "summary", "body"],
                },
            }
        },
        "required": ["notes"],
    },
}


def _post_json(url: str, headers: dict, body: dict, timeout: int) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={**headers, "content-type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        die(f"{url} returned HTTP {e.code}:\n{detail[:4000]}")
    except urllib.error.URLError as e:
        die(f"could not reach {url}: {e.reason}")


def call_anthropic(prompt: str, model: str, api_key_env: str, max_tokens: int, timeout: int) -> list:
    api_key = os.environ.get(api_key_env)
    if not api_key:
        die(f"{api_key_env} is not set")
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [NOTES_TOOL_SCHEMA],
        "tool_choice": {"type": "tool", "name": "emit_notes"},
    }
    data = _post_json("https://api.anthropic.com/v1/messages",
                       {"x-api-key": api_key, "anthropic-version": "2023-06-01"}, body, timeout)
    for block in data.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == "emit_notes":
            notes = block.get("input", {}).get("notes")
            if isinstance(notes, list):
                return notes
    die(f"Anthropic response had no emit_notes tool call:\n{json.dumps(data, indent=2)[:4000]}")


def call_openai_compatible(prompt: str, model: str, base_url: str, api_key_env: str, timeout: int) -> list:
    api_key = os.environ.get(api_key_env)
    if not api_key:
        die(f"{api_key_env} is not set")
    if not model:
        die("--model is required for --provider openai-compatible")
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You return only valid JSON. No prose, no code fences."},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    data = _post_json(base_url.rstrip("/") + "/chat/completions",
                       {"Authorization": f"Bearer {api_key}"}, body, timeout)
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        die(f"unexpected response shape:\n{json.dumps(data, indent=2)[:4000]}")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        die(f"model did not return valid JSON ({e}):\n{content[:4000]}")
    notes = parsed.get("notes") if isinstance(parsed, dict) else None
    if not isinstance(notes, list):
        die(f"model's JSON had no 'notes' array:\n{content[:4000]}")
    return notes


# ---------------------------------------------------------------------------
# Turning one model-returned note into a real Wiki/ file
# ---------------------------------------------------------------------------

def sanitize_title(title: str) -> str:
    cleaned = FILENAME_BAD_CHARS.sub("", title).strip().rstrip(". ")
    return re.sub(r"\s+", " ", cleaned)


def render_note(cfg: "core.Config", kind: "core.Kind", title: str, aliases: list,
                 topics: list, summary: str, body: str, extra_fields: dict, source_stem: str) -> str:
    today = date.today().isoformat()
    real_values = {
        "tags": [kind.tag],
        "topics": [f"[[{t}]]" for t in topics],
        "status": cfg.statuses[0],
        "created": today,
        "updated": today,
        "sources": [f"[[{source_stem}]]"],
        "source_count": 1,
        "aliases": list(aliases),
    }
    lines = []
    for name in cfg.compiled_fields:
        bare = name in ("status", "created", "updated")
        lines += core._yaml_field(name, real_values.get(name, ""), bare=bare)
    for f in kind.fields:
        bare = f.type == "date" or (f.type == "list" and f.item == "date")
        value = extra_fields[f.name]
        if f.type == "list" and f.item == "link" and isinstance(value, list):
            value = [f"[[{x}]]" if not str(x).startswith("[[") else x for x in value]
        lines += core._yaml_field(f.name, value, bare=bare)
    frontmatter = "---\n" + "\n".join(lines) + "\n---\n"
    return frontmatter + f"\n# {title}\n\n{summary.strip()}\n\n{body.strip()}\n"


def validate_and_coerce_fields(kind: "core.Kind", raw_fields: dict) -> tuple[dict | None, list[str]]:
    """Returns (fields-ready-to-write, problems). fields is None if a required field is missing."""
    problems = []
    out = {}
    raw_fields = raw_fields or {}
    for f in kind.fields:
        if f.name not in raw_fields or raw_fields[f.name] in (None, ""):
            if f.required is True:
                problems.append(f"missing required field '{f.name}'")
                out[f.name] = None
                continue
            out[f.name] = [] if f.type == "list" else ({"bool": False, "int": 0}.get(f.type, ""))
            continue
        value = raw_fields[f.name]
        if f.enum and value not in f.enum:
            problems.append(f"field '{f.name}' = {value!r} is not one of {f.enum}")
        out[f.name] = value
    unknown = sorted(set(raw_fields) - {f.name for f in kind.fields})
    if unknown:
        problems.append(f"ignored unknown field(s) from the model: {', '.join(unknown)}")
    if any(problems and out.get(f.name) is None for f in kind.fields if f.required is True):
        return None, problems
    return out, problems


def process_note(v: "core.Vault", source_stem: str, raw: dict, dry_run: bool) -> tuple[str, str]:
    """Returns (status, message) where status is one of: written, skipped, dry-run."""
    cfg = v.cfg
    missing = [k for k in ("kind", "title", "summary", "body") if not raw.get(k)]
    if missing:
        return "skipped", f"note missing required field(s) {missing}: {json.dumps(raw)[:200]}"
    kind = cfg.by_tag.get(raw["kind"])
    if kind is None:
        return "skipped", f"{raw['title']!r}: unknown kind {raw['kind']!r}"
    title = sanitize_title(raw["title"])
    if not title:
        return "skipped", f"empty title after sanitizing {raw['title']!r}"
    rel = f"Wiki/{kind.folder}/{title}.md"
    if v.abs(rel).is_file():
        return "skipped", f"{rel}: already exists, not overwriting"
    fields, problems = validate_and_coerce_fields(kind, raw.get("fields"))
    if fields is None:
        return "skipped", f"{rel}: {'; '.join(problems)}"
    text = render_note(cfg, kind, title, raw.get("aliases") or [], raw.get("topics") or [],
                       raw["summary"], raw["body"], fields, source_stem)
    note = ""
    if problems:
        note = " (" + "; ".join(problems) + ")"
    if dry_run:
        return "dry-run", f"would write {rel}{note}"
    v.abs(rel).parent.mkdir(parents=True, exist_ok=True)
    v.abs(rel).write_text(text, encoding="utf-8")
    return "written", f"wrote {rel}{note}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="auto_ingest.py",
        description="Call an external LLM API to draft compiled notes from one Raw source "
                     "(single API call, no auto-fix loop; see the module docstring).",
    )
    p.add_argument("source", help="a Raw/Sources/ file, by path or unique filename")
    p.add_argument("--provider", choices=["anthropic", "openai", "openai-compatible"], default="anthropic")
    p.add_argument("--model", help="model name (default: a current model for --provider)")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL,
                   help=f"API base URL, openai/openai-compatible only (default {DEFAULT_BASE_URL})")
    p.add_argument("--api-key-env", help="env var to read the API key from "
                                        "(default: ANTHROPIC_API_KEY / OPENAI_API_KEY)")
    p.add_argument("--root", type=Path, default=core.VAULT, help="vault root (default: parent of scripts/)")
    p.add_argument("--dry-run", action="store_true", help="print what would be written; write nothing, "
                                                           "run no follow-up commands")
    p.add_argument("--max-tokens", type=int, default=8192, help="Anthropic max_tokens (default 8192)")
    p.add_argument("--timeout", type=int, default=600, help="HTTP timeout in seconds (default 600)")
    p.add_argument("--skip-followup", action="store_true",
                   help="don't run build/lint/source-scan/log afterwards")
    args = p.parse_args(argv)

    root = args.root.resolve()
    load_dotenv(root)
    try:
        v = core.Vault(root)
    except core.ConfigError as e:
        die(f"configuration error: {e}", 2)
    cfg = v.cfg

    source_rel = v.resolve(args.source) or args.source
    if not source_rel.startswith("Raw/Sources/") or not v.abs(source_rel).is_file():
        die(f"{args.source!r} is not a source in Raw/Sources/", 2)
    source_stem = Path(source_rel).stem
    source_content = v.abs(source_rel).read_text(encoding="utf-8")

    model = args.model or DEFAULT_MODELS[args.provider]
    api_key_env = args.api_key_env or DEFAULT_API_KEY_ENV[args.provider]

    prompt = build_prompt(v, source_rel, source_content, structured_via_tool=(args.provider == "anthropic"))

    print(f"auto_ingest.py: calling {args.provider} ({model}) for {source_rel} ...")
    if args.provider == "anthropic":
        notes = call_anthropic(prompt, model, api_key_env, args.max_tokens, args.timeout)
    else:
        base_url = args.base_url if args.provider == "openai-compatible" else DEFAULT_BASE_URL
        notes = call_openai_compatible(prompt, model, base_url, api_key_env, args.timeout)

    if not notes:
        print("auto_ingest.py: the model returned zero notes; nothing to write.")
        return 0

    print(f"auto_ingest.py: model returned {len(notes)} note(s); writing ...")
    counts = {"written": 0, "skipped": 0, "dry-run": 0}
    for raw in notes:
        status, message = process_note(v, source_stem, raw, args.dry_run)
        counts[status] += 1
        print(f"  [{status}] {message}")

    print(f"auto_ingest.py: {counts['written']} written, {counts['skipped']} skipped"
         + (f", {counts['dry-run']} would be written (dry-run)" if args.dry_run else "") + ".")

    if args.dry_run:
        print("auto_ingest.py: --dry-run, stopping before build/lint/source-scan/log.")
        return 0
    if counts["written"] == 0:
        print("auto_ingest.py: nothing written; skipping follow-up commands.")
        return 0
    if args.skip_followup:
        return 0

    print("auto_ingest.py: running follow-up commands ...")
    tool = str(Path(__file__).resolve().parent / "wiki_tool.py")
    steps = [
        [sys.executable, tool, "--root", str(root), "build"],
        [sys.executable, tool, "--root", str(root), "lint"],
        [sys.executable, tool, "--root", str(root), "source-scan", "--update", "--accept-covered"],
        [sys.executable, tool, "--root", str(root), "log", "--title", f"ingest | {source_stem} (auto_ingest.py)",
         "--details", f"{counts['written']} note(s) drafted by {args.provider} ({model}); all status: seed."],
    ]
    exit_code = 0
    for step in steps:
        print(f"$ {' '.join(step[3:])}")
        result = subprocess.run(step)
        if result.returncode != 0:
            exit_code = result.returncode
            print(f"auto_ingest.py: {' '.join(step[3:])} exited {result.returncode} — stopping here; "
                 "review by hand.", file=sys.stderr)
            break
    if exit_code == 0:
        print("auto_ingest.py: done. Review Wiki/Generated/Review Queue.md before committing.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
