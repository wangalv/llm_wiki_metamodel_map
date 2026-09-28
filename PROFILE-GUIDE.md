# Profile Guide

How to set up **LLM Wiki Core** for a new business domain (a *profile*) and then work with it day to day. You don't write any code: a profile is a copy of the Core vault with its own `Schema/wiki-config.json`.

Most profiles need nothing more than the configuration. If a check, a generated file or a document converter can't be expressed in the config, a profile can add a small Python plugin instead. That is an advanced option and is covered separately in `scripts/profiles/plugin-interface.md`.

- **Part 1** creates a new profile vault.
- **Part 2** covers daily use: adding sources, ingesting, checking and changing the configuration.

## Concepts

| Term | Meaning |
|---|---|
| **Core** | This vault. Its `scripts/wiki_tool.py` is the engine: parsing, citations, catalog, lint, build. Core's own `Schema/wiki-config.json` stays the default and is never edited for a profile. |
| **Profile** | One business domain, e.g. legislation, research papers or compliance policies. It's described by a `wiki-config.json` plus a profile doc. |
| **Profile vault** | An independent vault for one profile: a copy of Core with the profile's own `Schema/wiki-config.json`, its own `Raw/` and `Wiki/`, and its own checks. |

What a profile can change, all through `wiki-config.json`:
- **Note kinds:** folders, tags and per-kind behaviour
- **Typed fields:** for notes and for sources
- **Statuses**
- **Raw file naming**
- **Rules:** from the rule library
- **Generators:** from the generator library

The full reference is `Schema/command-reference.md`, in the sections Configuration, Field types, Rules and Generators.

What a profile can't change: the hard rules in `AGENTS.md`. Raw is read-only, compiled knowledge goes only in `Wiki/`, every claim cites a Raw source, the catalog is searched first, and the checks run before every commit.

## The engine: `scripts/wiki_tool.py`

**You never modify `wiki_tool.py` to add a profile.** Everything domain-specific goes in the vault's `Schema/wiki-config.json`.

- **Each vault has its own copy.** Step 1 copies `scripts/wiki_tool.py` into the new vault.
- **It always works on the vault it sits in.** Run it from that vault's folder, as `python3 scripts/wiki_tool.py <command>`. It reads that vault's config, sources and notes, and never touches Core or another vault.
- **Every command below is a subcommand of `wiki_tool.py`**, e.g. `sync-schema`, `build`, `source-scan`, `doctor`, `lint`, `source-lint`, `log` and `search-catalog`. `python3 scripts/wiki_tool.py --help` lists them all. The only other scripts are `scripts/install_hooks.sh` and `scripts/audit_public.py`.
- **Engine updates:** when Core's engine gains a fix or feature, copy Core's `scripts/wiki_tool.py` over the vault's copy. Nothing else needs to change.

---

# Part 1 — Create a new profile

The example below creates a profile called `research-paper` in a vault called `LLM Wiki Papers`. Replace both names with your own.

| Step | What you do | Runs `wiki_tool.py`? |
|---|---|---|
| 1 | Copy Core into a new vault | no (`rsync`) |
| 2 | Create the profile folder and doc | no (by hand) |
| 3 | Write the vault's `wiki-config.json` | no (by hand) |
| 4 | Generate the vault's structure | **yes**: `sync-schema`, `build`, `source-scan`, `doctor`, `lint` |
| 5 | Write the profile doc's ingest plan | no (by hand) |
| 6 | README, open in Obsidian, install hooks | no (`install_hooks.sh`) |
| 7 | Try one source end to end | **yes**: `source-lint`, `build`, `lint`, `source-scan`, `log` |

## Step 1. Copy Core into a new vault

Run this from the repository root, the folder that contains `LLM Wiki Core/`. It copies the engine, the skills, the docs and the templates, but none of Core's content (sources, notes, logs):

```bash
NEW="LLM Wiki Papers"
rsync -a \
  --exclude '.DS_Store' --exclude '__pycache__' --exclude '.obsidian/workspace*.json' \
  --exclude 'Raw/' --exclude 'Wiki/' --exclude 'Welcome.md' --exclude 'README.md' \
  --exclude 'Schema/source-manifest.jsonl' --exclude 'Schema/field-reference.md' \
  "LLM Wiki Core/" "$NEW/"
mkdir -p "$NEW/Raw/Sources" "$NEW/Raw/Files"
touch "$NEW/Raw/Sources/.gitkeep" "$NEW/Raw/Files/.gitkeep"
```

The new vault now has:
- `AGENTS.md`
- `Schema/` (the docs and `wiki-config.json`)
- `_templates/`
- `scripts/`
- `.githooks/`
- `.agents/skills/`
- `.obsidian/`

## Step 2. Create the profile folder

```bash
mkdir -p "$NEW/scripts/profiles/research-paper"
cp "$NEW/scripts/profiles/default/default-profile.md" \
   "$NEW/scripts/profiles/research-paper/research-paper-profile.md"
```

The profile doc must be called `<name>-profile.md`, not `README.md`. Obsidian links by filename, so every Markdown filename in a vault must be unique (check L2).

## Step 3. Write the profile's `wiki-config.json`

Edit **`$NEW/Schema/wiki-config.json`**, the new vault's own copy. Core's file is left alone. It starts as the default profile, so change only what your domain needs.

1. **Name the profile:** set `"profile": "research-paper"`. It must match the folder name from step 2.
2. **Kinds:** add, remove or rename them in `kinds`. Each kind needs a lowercase `tag` and a `folder` under `Wiki/`. Optionally set `requires_sources`, `summary`, `orphan_check`, `name` (`title` or `date`) and `index_order`, and declare extra typed `fields`.
3. **Source fields:** add domain fields to `source_fields`, e.g. `Year` or `Jurisdiction`. `Title`, `Created`, `Processed` and `tags` must stay, with their types.
4. **Statuses and naming:** change `statuses`, `raw_name_pattern` or `placeholders` if needed.
5. **Rules:** switch on checks from the rule library (`coverage`, `anchor_required`, `quote_matches`, …).
6. **Generators:** switch on generated files (`heading_index`, `term_list`, `catalog_table`, `bases_view`).

Example: the additions for a research-paper profile:

```json
{
  "profile": "research-paper",
  "kinds": [
    {"tag": "topic",   "folder": "Topics",   "orphan_check": false},
    {"tag": "concept", "folder": "Concepts"},
    {"tag": "finding", "folder": "Findings", "orphan_check": false,
     "fields": {
       "section": {"type": "string", "required": true, "pattern": "^[0-9]+(\\.[0-9]+)*$",
                   "description": "Paper section the finding comes from, e.g. 3.1"},
       "dataset": {"type": "string", "required": "recommended"},
       "result_type": {"type": "string", "enum": ["quantitative", "qualitative"], "template": "quantitative"}}},
    {"tag": "entity",  "folder": "Entities"},
    {"tag": "log",     "folder": "Logs", "requires_sources": false, "summary": false,
     "orphan_check": false, "name": "date", "index_order": "desc"}
  ],
  "rules": [
    {"id": "RP1", "type": "anchor_required", "kinds": ["finding"]},
    {"id": "RP2", "type": "alias_matches_anchor", "alias": "^§ ?(\\S+)$", "anchor": "^(\\S+) "},
    {"id": "RP3", "type": "coverage", "level": "warn", "heading": "^\\d+(\\.\\d+)* ", "levels": [2, 3],
     "exclude": "(?i)references|acknowledg", "by_kinds": ["finding", "concept"]},
    {"id": "RP4", "type": "quote_matches", "kinds": ["concept", "finding"]}
  ],
  "generators": [
    {"id": "paper-outlines", "type": "heading_index", "sources": ".*", "levels": [2, 3],
     "output": "Wiki/Generated/Paper Outlines.md"},
    {"id": "findings-table", "type": "catalog_table", "kinds": ["finding"],
     "columns": ["note", "section", "dataset", "status", "summary"], "group_by": "dataset",
     "output": "Wiki/Generated/Findings Table.md"}
  ]
}
```

These keys replace the corresponding keys in the file. Keep the other keys (`version`, `topics_kind`, `statuses`, `compiled_fields`, `source_fields`, …) as they are, unless you want to change them too.

Tips:
- **Rule `id`s:** uppercase and unique, e.g. a profile prefix plus a number (`RP1`). They can't reuse core codes (F1, S2, …).
- **Generator `output`:**
  - To make the output a searchable note, put it in a kind folder.
  - Otherwise put it anywhere else under `Wiki/`, e.g. `Wiki/Generated/`.
  - A `catalog_table` can't go into a kind that must cite sources.
- **Invalid config:** the tool refuses to run and says exactly which key is wrong (exit code 2).

## Step 4. Generate the vault's structure

```bash
cd "$NEW"
python3 scripts/wiki_tool.py sync-schema          # templates for every kind + Schema/field-reference.md
python3 scripts/wiki_tool.py build                # Wiki/ folders, indexes, catalog, generator outputs
python3 scripts/wiki_tool.py source-scan --update # empty source manifest
python3 scripts/wiki_tool.py doctor               # everything should be OK
python3 scripts/wiki_tool.py lint                 # 0 errors
```

`doctor` shows the active config, e.g. `(5 kinds: topic, concept, finding, entity, log, 4 rules, 2 generators)`, and the profile.

If you removed a kind, e.g. `project`, delete its old template (`_templates/project-note.md`) by hand. `sync-schema` only writes templates for the kinds in the config.

## Step 5. Write the profile doc

Edit `scripts/profiles/research-paper/research-paper-profile.md`. This is the guidance the agent follows when it ingests. Include:
1. **What the profile is for:** the kinds, and what belongs in each.
2. **Source requirements:** what a source must look like. For example: Markdown with numbered headings, a glossary with bold terms, and how to convert the raw documents (e.g. with the `defuddle` skill for web pages).
3. **Citation conventions:** e.g. cite section headings labelled `§3.1`.
4. **Ingest plan:** step by step, which notes to write for a source and in what order, and which checks to run.
5. **Rules and generators:** what each ID enforces or produces.

## Step 6. Write the vault README, open it and install the hooks

1. Create `$NEW/README.md`: one paragraph on what the vault is and which profile it uses, plus the commands from Part 2.
2. Open the `$NEW` folder as a vault in Obsidian.
3. Install the git hooks. The vault must be inside a git repository, so run `git init` first if it isn't in one:

   ```bash
   bash scripts/install_hooks.sh
   ```

   This sets up **automatic checks before every `git commit`**. Git then runs these before each commit:
   - `wiki_tool.py build`, `lint` and `source-lint`
   - `audit_public.py`, which looks for secrets, local paths and plugin or cache state

   If any of them fails, the commit is blocked until you fix the problem, so broken or sensitive content never reaches the repository.

   The script only changes one local git setting (`core.hooksPath`). Run it once per clone. In this repository the root `.githooks/pre-commit` runs the checks of **every** vault folder, so the new vault is checked on every commit.

## Step 7. Try one source end to end

Before you rely on the profile, run one real source through Part 2.
- **Rules too noisy or too weak?** Adjust them in `wiki-config.json`.
- **Generator output wrong?** Adjust its parameters.

Then commit the vault.

---

# Part 2 — Use a profile vault

Run every command from the vault folder.

## Health check

```bash
python3 scripts/wiki_tool.py doctor
```

This shows the config, the profile, and the rule and generator counts, the folders, the catalog and manifest status, and the note counts.

## Add a source

1. Put the source in `Raw/Sources/` as `YYYY-MM-DD-kebab-slug.md`, starting from `_templates/source-note.md`. Fill in the required fields listed in `Schema/field-reference.md`, and set `Processed: false`.
   - Web pages: clip them with the `defuddle` skill.
   - PDFs or other formats: convert them to Markdown with headings first.
   - Attachments: put them in `Raw/Files/` and embed them in the source note.
2. Check it:

   ```bash
   python3 scripts/wiki_tool.py source-lint
   python3 scripts/wiki_tool.py build   # refreshes generator outputs, e.g. the source's outline
   ```

## Ingest a source

Ask the agent to ingest it. The `llm-wiki-ingest` skill applies the general rules, and the profile doc's ingest plan adds the domain-specific steps. After writing notes:

```bash
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py lint
python3 scripts/wiki_tool.py source-scan --update --accept-covered
python3 scripts/wiki_tool.py source-lint
python3 scripts/wiki_tool.py log --title "ingest | <source title>" --details "<notes created/updated>"
```

- **Errors** (core codes or your rule IDs) must be fixed before committing.
- **Warnings**, e.g. a `coverage` rule set to `warn`, show what's still missing. Use them as a to-do list.

## Ask questions

Use the `llm-wiki-query` skill. It searches the catalog first:

```bash
python3 scripts/wiki_tool.py search-catalog --query "plain-language question" [--tag <kind>]
```

## Change the configuration

Edit `Schema/wiki-config.json` in the vault, then run:

```bash
python3 scripts/wiki_tool.py sync-schema   # templates + field reference follow the config
python3 scripts/wiki_tool.py build         # folders, indexes, generator outputs follow the config
python3 scripts/wiki_tool.py lint          # existing notes checked against the new config
```

| After you… | Also do this |
|---|---|
| Add a kind | `sync-schema` creates its template, and `build` creates its folder and index |
| Add a required field | Fill it in on existing notes of that kind (lint reports F2) |
| Add a rule | Fix what it reports, or start it at `"level": "warn"` |
| Remove a generator | Delete its old output file by hand |

## Commit

```bash
git add -A && git commit -m "<message>"
```

The pre-commit hook runs `build`, `lint`, `source-lint` and the public audit for every vault. If `build` changed a generated file, stage it and commit again.

## Troubleshooting

| Message | Meaning | Fix |
|---|---|---|
| `configuration error: …` (exit 2) | `wiki-config.json` is invalid. The message names the key. | Fix that key |
| `K1 … generated file is out of date` | A generated file was hand-edited, or its inputs changed | `build`. Never edit generated files. |
| `K5 … out of date with Schema/wiki-config.json` | Templates or the field reference don't match the config | `sync-schema` |
| `F2 missing field(s)` | A required field (core or typed) is missing | Add it. Required fields are listed in `Schema/field-reference.md`. |
| `F9 field '…'` | A typed field has the wrong type, value, pattern or link target | Fix the value, or the field definition |
| `L2 filename is not unique` | Two Markdown files share a name | Rename one. Profile docs are `<name>-profile.md`. |
| A finding under your rule ID | Your rule found something | See the rule's description in `Schema/field-reference.md` |

## Where to look

| Question | File |
|---|---|
| What must every note and source contain? | `Schema/field-reference.md` (generated) |
| What does each command and config key do? | `Schema/command-reference.md` |
| What are the hard rules for agents? | `AGENTS.md` |
| How should this domain be ingested? | `scripts/profiles/<name>/<name>-profile.md` |
| What does each check code mean? | `Schema/lint-checklist.md` |
