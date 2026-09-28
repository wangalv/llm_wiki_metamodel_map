# LLM Wiki Metamodel Mapper

An Obsidian vault that an LLM agent turns into a cited knowledge base: it reads organisational technical documents (architecture descriptions, design documents, data dictionaries) and compiles them into notes structured by the TOGAF 9.2 Content Metamodel's 23 core objects, plus a `domain` grouping kind the engine itself requires.

Three rules hold throughout (the full rules are in `AGENTS.md`):
- `Raw/` is source material. The agent reads it but never rewrites it.
- Compiled knowledge goes only in `Wiki/`.
- Every claim in `Wiki/` cites a Raw source.

**Read `scripts/profiles/togaf-core/togaf-core-profile.md` before ingesting anything.** It defines every note type (what it means, when to use it, what to record), how notes link to each other, and a "no representative sampling" rule: if a document names five distinct instances of the same type, that's five notes, not one.

## Status

This vault ships empty: no sources ingested yet, ready for a first real document.

## What you need

- Python 3.9 or later. The tools use only the standard library.
- Git.
- An LLM agent that reads `AGENTS.md` and the skills in `.agents/skills/`, such as Claude Code or Codex.
- Obsidian, to browse the wiki (optional).

## Structure

```
./
├── Raw/                 ← source material; the agent reads but doesn't rewrite it
│   ├── Sources/         ← one Markdown file per document, YYYY-MM-DD-kebab-slug.md
│   └── Files/           ← attachments
├── Wiki/                ← agent-maintained notes, one folder per TOGAF type
│   ├── catalog.jsonl    ← generated: one JSON line per note (search this first)
│   ├── index.md         ← generated: human-readable index
│   ├── log.md           ← append-only activity log
│   └── Generated/
│       ├── Catalogue.md      ← generated: every note, one table
│       └── Review Queue.md   ← generated: notes with status: seed, pending your review
├── Schema/              ← wiki-config.json (the 24 kinds, the rule, the two generators), plus reference docs
├── _templates/          ← note templates (generated from wiki-config.json)
├── .agents/skills/      ← agent skills: llm-wiki-ingest, llm-wiki-query, llm-wiki-lint, llm-wiki-maintain, and Obsidian-format skills
├── .githooks/           ← pre-commit hook (build, lint, source-lint, public audit)
├── scripts/             ← wiki_tool.py (the engine), audit_public.py, install_hooks.sh, profiles/togaf-core/
└── AGENTS.md            ← rules for AI agents
```

## Daily use

Run these from this folder.

```bash
python3 scripts/wiki_tool.py doctor        # health check
python3 scripts/wiki_tool.py source-lint   # check a new source in Raw/Sources/
python3 scripts/wiki_tool.py build         # rebuild indexes and the two generated tables
python3 scripts/wiki_tool.py lint          # check the notes
python3 scripts/wiki_tool.py search-catalog --query "plain-language question" [--tag <kind>]
python3 scripts/wiki_tool.py source-scan --update --accept-covered   # mark a source processed
python3 scripts/wiki_tool.py log --title "ingest | <title>" --details "<notes>"
```

## Add and ingest a document

1. Save it in `Raw/Sources/` as `YYYY-MM-DD-kebab-slug.md`, starting from `_templates/source-note.md`, with `Processed: false`.
2. Check it: `source-lint`, then `build`.
3. Ask the agent to ingest it, following `togaf-core-profile.md`'s note types and its "no representative sampling" rule. The `llm-wiki-ingest` skill applies the general rules.
4. Every new note starts `status: seed`. After ingest, run `build`, `lint`, `source-scan --update --accept-covered`, `source-lint`, then `log`.
5. Open `Wiki/Generated/Review Queue.md`: one row per note pending review, with its type and `classification_basis`. For each, confirm it (`status: stable`, or `growing` if more sources are still expected), fix its type or fields, merge it into an existing note if it's a duplicate, or delete it.
6. Commit only once the queue is clear, or you've consciously left something in `seed`.

## Ask questions

Use the `llm-wiki-query` skill, or `search-catalog` directly — it searches `Wiki/catalog.jsonl` first, and only opens Raw sources to confirm details.

## Change the configuration

Edit `Schema/wiki-config.json`, then run `sync-schema`, `build` and `lint`.

| After you… | Also do this |
|---|---|
| Add a kind | `sync-schema` creates its template, `build` creates its folder and index |
| Add a required field | Fill it in on existing notes of that kind (`lint` reports F2) |
| Add a rule | Fix what it reports, or start it at `"level": "warn"` |
| Remove a generator | Delete its old output file by hand |

## Commit

```bash
bash scripts/install_hooks.sh   # once per clone
git add -A && git commit -m "<message>"
```

The pre-commit hook runs `build`, `lint`, `source-lint` and `audit_public.py` (checks for secrets, local paths, plugin/cache state). If `build` changed a generated file, stage it and commit again.

## Troubleshooting

| Message | Meaning | Fix |
|---|---|---|
| `configuration error: …` (exit 2) | `wiki-config.json` is invalid; the message names the key | Fix that key |
| `K1 … generated file is out of date` | A generated file was hand-edited, or its inputs changed | `build`. Never edit generated files. |
| `K5 … out of date with Schema/wiki-config.json` | Templates or the field reference don't match the config | `sync-schema` |
| `F2 missing field(s)` | A required field is missing | Add it — see `Schema/field-reference.md` |
| `F9 field '…'` | A typed field has the wrong type, value, pattern or link target | Fix the value, or the field definition |
| `L2 filename is not unique` | Two Markdown files share a name | Rename one |
| A finding under rule `TM1` | A citation doesn't point at an exact heading or block | Fix the citation |

## Where to look

| Question | File |
|---|---|
| What note types exist, and how do I classify something? | `scripts/profiles/togaf-core/togaf-core-profile.md` |
| What must every note and source contain? | `Schema/field-reference.md` (generated) |
| What does each command and config key do? | `Schema/command-reference.md` |
| What are the hard rules for agents? | `AGENTS.md` |
| What does each check code mean? | `Schema/lint-checklist.md` |

## What's not committed

`.gitignore` keeps these out: per-device Obsidian state (`workspace.json`, `graph.json`, cache, `.trash/`), plugin `data.json` files, and secrets (`.env`, `*.key`, `*.pem`).
