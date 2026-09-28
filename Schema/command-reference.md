# Command Reference

All tooling uses only the Python standard library (Python ≥ 3.9). The core behaviour is fixed. What's specific to a vault's domain comes from its [configuration](#configuration) and [profile](#profiles). The tools find the vault from their own location, so you can run them from anywhere. The examples below assume you're in the vault root.

```bash
python3 scripts/wiki_tool.py <command> [options]
python3 scripts/wiki_tool.py --root <vault> <command>   # run against a different vault
```

## At a glance

| Command | Writes files? | Fails (exit 1) when |
|---|---|---|
| `doctor` | no | a folder is missing, Python is too old, or the catalog/manifest can't be parsed |
| `build` | Configured generator and profile outputs, `Wiki/catalog.jsonl`, `Wiki/index.md`, `Wiki/<Folder>/<Folder> Index.md` | never, unless there's an I/O error |
| `lint` | no | any compiled-note **error** (with `--strict`, warnings too) |
| `source-scan` | only with `--update` | the manifest can't be parsed |
| `source-scan --update --accept-covered` | the manifest, plus `Processed: true` in covered sources | the manifest can't be parsed |
| `source-lint` | no | any source **error** (with `--strict`, warnings too) |
| `source-delta` | no | with `--check`: the manifest is out of date |
| `source-coverage` | no | never |
| `search-catalog --query "…"` | no | the catalog is missing or can't be parsed |
| `log --title "…" --details "…"` | appends to `Wiki/log.md` | the title is empty |
| `sync-schema [--check]` | `_templates/*-note.md` frontmatter and `Schema/field-reference.md` | with `--check`: any of them is out of date |
| `convert <name> <input> --output <file>` | the output file | the input is missing or the output exists (use `--force`); exit 2 for an unknown converter |

Every command exits with **2** if `Schema/wiki-config.json` or the profile can't be loaded. The error message names the problem.

Finding codes such as `F3` and `S9` refer to `Schema/lint-checklist.md`.

## doctor

A read-only health check. It reports:
- the Python version
- the configuration in use (`Schema/wiki-config.json` or built-in defaults) and its note kinds
- the active profile and which plugins it provides
- the required folders, and whether `AGENTS.md` exists
- the catalog: whether it parses, its entry count versus the number of compiled notes, and whether it's stale
- the source manifest: whether it parses and whether it has drifted
- note counts per tag, plus sources processed / covered
- whether the git hooks are installed

## build

Regenerates the derived files from the frontmatter and body of each compiled note. Compiled notes are the `.md` files in `Wiki/Topics|Concepts|Entities|Projects|Logs/`, excluding the generated index files.

- **`Wiki/catalog.jsonl`**: one JSON object per compiled note, sorted by path.
- **`Wiki/index.md`**: section counts, plus every note with its summary.
- **`Wiki/<Folder>/<Folder> Index.md`**: a table of status, source count, updated date and summary. Logs are listed newest first.

Output is deterministic: running `build` twice changes nothing, and it only writes files whose content changed.

Catalog contract (keys marked \* are the minimum):

```json
{"path*": "Wiki/Concepts/Self-Attention.md", "title*": "Self-Attention", "tag*": "concept",
 "summary": "…", "topics*": ["Wiki/Topics/Large Language Models.md"],
 "sources*": ["Raw/Sources/2017-06-12-attention-is-all-you-need.md"], "source_count": 1,
 "aliases": [], "status": "seed", "links": [], "updated*": "2026-09-25"}
```

- `topics` and `sources` are frontmatter wikilinks resolved to vault paths. An entry that doesn't resolve keeps its raw target, and `lint` reports it.
- `summary` is the first sentence after the `# Heading`, with citations removed.
- `links` lists the body links to other compiled notes.

## lint

Validates compiled Wiki notes:

| Area | Codes |
|---|---|
| Frontmatter | F1–F8. Required fields; exactly one allowed tag (a kind from `Schema/wiki-config.json`) that matches the folder; `source_count` = number of `sources`; dates; status; summary; `topics` point at the `topics_kind` kind (`domain` in this vault). |
| Sources and citations | S1–S5. At least one source (except logs); every `sources` entry resolves under `Raw/Sources/`; cited headings and blocks exist; cited sources are listed; listed sources are cited. |
| Links | L1 broken links, L2 duplicate filenames, L3 orphans, L5 notes outside a subfolder |
| Naming | N2 forbidden characters, N3 log filenames, N4 likely duplicates (shared title or alias) |
| Content | C2 leftover template placeholders, C3 `stable` note with an open question |
| Typed fields | F9: a kind's extra field has the wrong type, value, pattern or link target |
| Generated files and git | K1: catalog or index out of date (run `build`) · K4: note ignored by `.gitignore` · K5: template or field reference out of sync with the config (run `sync-schema`) |

Links inside code spans, fenced code, `<!-- -->` and `%% %%` comments are ignored.

## source-scan

Lists every note in `Raw/Sources/` with:
- `P` if it's processed
- how many compiled notes cover it
- its state in the manifest: `new`, `changed` or `ok`

| Option | Effect |
|---|---|
| `--update` | Write `Schema/source-manifest.jsonl` |
| `--accept-covered` | With `--update`: mark every covered source as processed, in the manifest **and** in its frontmatter (`Processed: false` → `true`, the only edit the tooling makes to `Raw/`). Run it after compiled notes have been written for new sources. |
| `--json` | Print the entries as JSON lines |

Manifest contract (one line per Raw source, sorted by path):

```json
{"path": "Raw/Sources/2017-06-12-attention-is-all-you-need.md", "title": "Attention Is All You Need",
 "processed": true, "covered_by": ["Wiki/Concepts/Self-Attention.md"], "updated": "2026-09-25"}
```

- `processed` mirrors the source's `Processed` field.
- `covered_by` lists the compiled topic, concept, entity and project notes whose `sources` cite the file. Logs don't count.
- `updated` keeps its old value unless `title`, `processed` or `covered_by` changed.

## source-lint

Validates source notes and their coverage state:

| Severity | Checks |
|---|---|
| **Error** | A typed source field with the wrong type or value (F9) · Source or attachment ignored by `.gitignore` (K4) · Missing `Title`, `Reference`, `Created`, `Processed` or `tags` (F2) · `tags` without `source` (F3) · bad `Created` date (F5) · non-boolean `Processed` (F6) · **`Processed: true` with no Wiki coverage (S9)** · missing embedded attachment (S6) · bad Raw filename (N1) · unparseable manifest (M1) |
| **Warning** | Missing `Author` or `ContentType` · covered but `Processed: false` (S9) · uncovered source (L4) · attachment not embedded anywhere (S7) · leftover placeholders (C2) · manifest missing or out of date (M1) |

## source-delta

Compares the sources on disk with `Schema/source-manifest.jsonl`. It lists sources **not in the manifest**, manifest entries **missing on disk**, and entries whose title, processed flag or coverage **changed**.

| Option | Effect |
|---|---|
| `--json` | Print the result as JSON |
| `--check` | Exit 1 if there's any difference (useful in CI) |

## source-coverage

Shows, for each Raw source, the compiled notes that cover it, and which sources are uncovered.

| Option | Effect |
|---|---|
| `--uncovered` | List only uncovered sources |
| `--json` | Print the result as JSON |

## rollback-source

```bash
python3 scripts/wiki_tool.py rollback-source <source> [--dry-run] [--delete-source]
```

Removes compiled notes created from one Raw source, for when a source turns out to have been a mistake (wrong document, bad ingest) and you want it fully undone rather than fixed note by note.

- Only removes a note if that source is the **only** entry in its `sources` field. A note that also cites another source is left alone and listed, since there's no safe way to split its content back apart — merge or edit it by hand instead.
- `--dry-run` lists what would happen and changes nothing.
- `--delete-source` also deletes the source file itself (default: keep it, e.g. to re-ingest later with corrections).
- Appends a `rollback` entry to `Wiki/log.md` — it never deletes or rewrites earlier log entries, so the record shows the ingest happened and was later undone, not that it never happened.
- Doesn't rewrite links: run `build` and `lint` afterwards. Any wikilink left pointing at a removed note shows up as `L1`, for a person or `llm-wiki-maintain` to resolve.

## search-catalog

```bash
python3 scripts/wiki_tool.py search-catalog --query "what did the authors conclude about the larger dataset" [--tag concept] [--limit 20] [--json]
```

A case-insensitive search of the compiled Wiki notes listed in `Wiki/catalog.jsonl`. It works with plain-language questions.

**How the query is processed**
- Question words and other common words (who, the, of, how, …) are ignored.
- Simple plurals are folded, so "fees" matches "fee".

**How notes match**
- A note matches if at least half of the remaining words appear in one of its fields.
- The fields, from strongest to weakest match:
  1. title
  2. aliases
  3. tag and summary
  4. topics, path and the note's body text

  Citation links in the body are ignored, because every note cites the same sources.

**Ranking**
1. Notes that match more of the words come first.
2. Then notes that match on stronger fields.
3. An exact title or alias match gets a bonus.

Each result shows how many of the query words it matched.

Run `build` first so the catalog is current. This is the first step of `llm-wiki-query` and `llm-wiki-ingest`, before opening anything in `Raw/`. It only searches compiled notes in `Wiki/`, never `Raw/`.

## log

```bash
python3 scripts/wiki_tool.py log --title "ingest | Attention Is All You Need" --details "Created [[Self-Attention]], updated [[Large Language Models]]."
```

Appends `## [YYYY-MM-DD HH:MM] <title>` and the details to `Wiki/log.md`, creating the file if needed. `Wiki/log.md` is the short chronological activity log. (A profile with a `log` kind can also keep detailed daily notes in `Wiki/Logs/`; this vault has no `log` kind, so `Wiki/log.md` is the only log.)

Suggested title prefixes: `ingest |`, `query |`, `lint |`, `maintain |`.

## audit_public.py

```bash
python3 scripts/audit_public.py
```

Scans everything git would publish: tracked files, plus untracked files that aren't ignored. It fails on:

- private keys (`-----BEGIN … PRIVATE KEY-----`, `id_rsa`, `*.pem`, `*.key`, …)
- API keys and tokens with well-known formats (Anthropic, OpenAI, GitHub, AWS, Slack, Google, Stripe), and `api_key = "…"`-style assignments
- machine-local paths (a home directory under `/Users/` or `/home/`, a Windows user folder, file URLs) and absolute symlink targets
- plugin, cache and state files: `.obsidian/workspace*.json`, `.obsidian/plugins/*/data.json`, `.obsidian/cache`, `.trash/`, `.DS_Store`, `__pycache__`, `.env*` (except `.env.example`)

To accept a known false positive, add `audit-public: allow` to that line.

## Git hooks

```bash
bash scripts/install_hooks.sh
```

Sets `core.hooksPath` to the vault's `.githooks/` folder. Git resolves this path relative to the repository root, which is one level above the vault.

`.githooks/pre-commit` runs, in order:
1. `wiki_tool.py build`
2. `wiki_tool.py lint`
3. `wiki_tool.py source-lint`
4. `audit_public.py`

It then fails if `build` changed any generated file that isn't staged. Stage those files and commit again.

- Bypass the hook in an emergency with `git commit --no-verify`.
- Uninstall with `git config --unset core.hooksPath`.

## Configuration

`Schema/wiki-config.json` is optional. Without it, the built-in defaults apply, and those are exactly what the file contains as shipped. Keys starting with `_` are comments. Unknown keys and invalid values are rejected.

| Key | Meaning | Default |
|---|---|---|
| `version` | Config format version | `1` |
| `profile` | Plugin folder `scripts/profiles/<profile>/` | `default` |
| `kinds` | Compiled-note kinds, in index order (see below) | topic, concept, entity, project, log |
| `topics_kind` | Kind that `topics` entries must point to (F8) | `topic` |
| `statuses` | Allowed `status` values (F6) | seed, growing, stable, stale |
| `compiled_fields` | Core compiled-note frontmatter, required on every kind (F2). Their checks are built in (F3–F8, S rules). | tags, topics, status, created, updated, sources, source_count, aliases |
| `source_fields` | Typed source-note fields, in template order (see [Field types](#field-types)). Must define `Title` (string), `Created` (date), `Processed` (bool) and `tags` (list). | Title, Author, Reference, ContentType, Created, Processed, tags |
| `raw_name_pattern` | Regex for Raw filenames (N1) | `YYYY-MM-DD-kebab-slug` |
| `placeholders` | Template leftovers flagged by C2 | `YYYY-MM-DD`, `{{title}}`, `[[source-stem` |
| `rules` | Declarative rules from the rule library, run by `lint` (see [Rules](#rules)) | `[]` |
| `generators` | Declarative generators from the generator library, run by `build` (see [Generators](#generators)) | `[]` |
| `extra_required_dirs` | Folders `doctor` requires, on top of `Raw/Sources`, `Raw/Files` and one `Wiki/<folder>` per kind | Schema, _templates, scripts |

Each entry in `kinds`:

| Field | Meaning | Default |
|---|---|---|
| `tag` | The single tag notes of this kind carry. Lowercase; not `source`. | required |
| `folder` | Folder under `Wiki/` | required |
| `requires_sources` | Must list ≥ 1 Raw source (S1); counts toward source coverage; S5 applies | `true` |
| `summary` | One-sentence summary is checked (F7) | `true` |
| `orphan_check` | Warn if no other Wiki note links here (L3) | `true` |
| `name` | `title` (Title Case.md) or `date` (YYYY-MM-DD.md, N3) | `title` |
| `index_order` | `asc` or `desc` order in the generated indexes | `asc` |
| `fields` | Extra typed frontmatter fields for this kind (see [Field types](#field-types)). Names can't repeat core fields. | `{}` |

A new kind needs:
- its entry in `kinds`
- the folder `Wiki/<folder>/`

Then run `sync-schema` to create its template `_templates/<tag>-note.md`, and `build` to add its index page and section.

### Field types

Used by `source_fields` and `kinds[].fields`. Each field is an object:

| Key | Meaning |
|---|---|
| `type` | `string`, `int`, `bool`, `date` (YYYY-MM-DD), `link` (a quoted wikilink) or `list` |
| `item` | For lists: `string` (the default), `int`, `date` or `link` |
| `required` | `true` (missing = F2 error), `"recommended"` (missing = F2 warning) or `false` |
| `enum` | Allowed values, for string or int fields and list items |
| `pattern` | Regex a string must match |
| `to_kind` | For links: the kind tag the target must belong to, or `"source"` for a note in `Raw/Sources/` |
| `template` | The value written into the generated template. Without it, an empty value of the right type is used. |
| `description` | Shown in `Schema/field-reference.md` |

A value of the wrong type, outside `enum`, not matching `pattern`, or pointing at the wrong kind of note is reported as **F9**. Empty values are only checked for presence.

- **Catalog:** when a kind has extra fields, its catalog entries gain a `fields` object, with link values resolved to vault paths.
- **Templates and docs:** after changing fields or kinds, run `sync-schema`. It rewrites the frontmatter of the templates, keeping their bodies, and regenerates `Schema/field-reference.md`. `lint` reports any file that is out of sync with the config as **K5**.

## Rules

`rules` in `wiki-config.json` switches on checks from the built-in rule library. Each rule is configured with parameters, not code, and runs as part of `lint`. The active rules are listed in `Schema/field-reference.md`, and `doctor` shows how many there are.

Every rule has these keys:

| Key | Meaning |
|---|---|
| `id` | The finding code, e.g. `LG1` or `R2`: uppercase, unique, and not a core code (F1, S2, …) |
| `type` | One of the types below |
| `level` | `error` (the default; blocks commits) or `warn` |
| `message` | Optional: replaces the default finding text |
| `description` | Optional: shown in `Schema/field-reference.md` |

`kinds` defaults to every kind. For `anchor_required`, it defaults to the kinds that must cite sources. A "citation" here means a body link to a note in `Raw/Sources/`.

| Type | Checks | Parameters |
|---|---|---|
| `anchor_required` | Every citation in notes of `kinds` points at a heading or block (`[[src#Heading]]`, `[[src#^id]]`), not the whole source | `kinds`, `sources` (regex on source path) |
| `alias_matches_anchor` | A citation whose label matches `alias` must have an anchor matching `anchor`, and the two captured values must be equal. For example, label `s 29` must point at heading `29 …`. Block anchors are skipped. | `kinds`, `alias` (regex, 1 group), `anchor` (regex, 1 group) |
| `coverage` | Every source heading matching `heading` must be cited, by anchor, by at least one note of `by_kinds` | `by_kinds` (required), `heading` (required), `levels` `[min, max]`, `exclude`, `text`, `where`, `sources`, `processed_only` |
| `rows_cited` | Every data row of every Markdown table in notes of `kinds` contains a citation (with an anchor, if `require_anchor`) | `kinds`, `require_anchor` (default true), `under_heading` (regex: only tables under a matching note heading) |
| `quote_matches` | The text of each `> [!quote]` callout in notes of `kinds` appears word for word in the cited section or block. Markdown formatting, list markers and whitespace are ignored. The callout must contain a citation. | `kinds`, `callout` (callout type, default `quote`) |
| `unique_scope` | No two notes of `kinds` have the same values for all of `fields`. Notes missing a field are skipped. Links are compared by target. | `kinds`, `fields` (required) |
| `filename` | Filenames of notes of `kinds` match `pattern` | `kinds`, `pattern` (required) |

More on the `coverage` parameters:
- `text`: only check headings whose section text matches this pattern. For example, `\bmust\b` finds the sections that state an obligation.
- `where`: only count citations from notes whose frontmatter fields equal the given values, e.g. `{"matrix_kind": "obligations"}`.
- `processed_only` (default `true`): skip sources whose `Processed` is still `false`.

Example:

```json
"rules": [
  {"id": "R1", "type": "anchor_required", "kinds": ["finding"]},
  {"id": "R2", "type": "alias_matches_anchor", "alias": "^s (\\S+)$", "anchor": "^(\\S+) "},
  {"id": "R3", "type": "coverage", "level": "warn", "heading": "^\\d+[A-Z]* ", "levels": [5, 5],
   "exclude": "\\(Repealed\\)", "by_kinds": ["concept", "entity"]}
]
```

Rules that can't be expressed with these types can still be written in Python, in a profile's `rules.py`. Prefer the declarative rules, because they're reusable and documented automatically.

## Generators

`generators` in `wiki-config.json` switches on generated files from the built-in generator library, configured with parameters rather than code:
- `build` writes them; `lint` reports hand edits (K1)
- `Schema/field-reference.md` lists them; `doctor` shows how many there are
- the output is deterministic: no timestamps anywhere

Every generator has these keys:

| Key | Meaning |
|---|---|
| `id` | A lowercase name, unique |
| `type` | One of the types below |
| `output` | A path under `Wiki/`. It must end in `.md`, or `.base` for `bases_view`, and can't be a system file. |
| `description` | Optional: shown in `Schema/field-reference.md` |

**Where the output goes matters.**
- **Inside a kind folder** (e.g. `Wiki/Topics/…`), the output is a normal note. The generator writes its full frontmatter:
  - the kind's tag
  - `sources` and `source_count` from the sources it read
  - `created` and `updated`, set to the newest date among its inputs
  - `status`, `topics`, `aliases` and extra `fields`, taken from the generator's keys

  It also writes a one-sentence summary, so the note passes lint like any other. `title` and `summary` can be overridden.
- **Anywhere else** (e.g. `Wiki/Generated/…`), it's a system file, like the index pages. It isn't a note, isn't in the catalog, and isn't subject to note rules.

| Type | Produces | Parameters |
|---|---|---|
| `heading_index` | A nested list of a source's headings, each linked to its anchor | `sources` (regex on source path, required), `levels` `[min, max]`, `heading`, `exclude` |
| `term_list` | One `> [!quote]` callout per term, holding the term's paragraph and any following non-term paragraphs, cited to the section. Pair it with a `quote_matches` rule to verify every quote. | `sources` (required), `term` (regex with 1 group, matched against the first line of each paragraph; required), `section` (regex on the heading to search under), `callout` (default `quote`) |
| `catalog_table` | A Markdown table of notes | `columns` (required), `kinds`, `where`, `sort`, `group_by` |
| `bases_view` | An Obsidian Bases `.base` file: a live query that Obsidian renders as a table, cards or list | `kinds`, `where`, `views` |

More detail:
- **`catalog_table` columns** can be any frontmatter field or extra field, plus `note` (a link), `summary`, `tag`, `path` and `links`. Links render as wikilinks.
- **`catalog_table` placement:** it summarises other notes and cites nothing itself, so its output can't go in a kind that must cite sources. Put it outside the kind folders, or in a kind with `requires_sources: false`.
- **`bases_view` views:** each view is `{"name", "type": "table"|"cards"|"list", "columns", "where", "group_by"}`. `note` becomes `file.name`.

Example:

```json
"generators": [
  {"id": "paper-outline", "type": "heading_index", "sources": "sample-paper", "levels": [2, 3],
   "output": "Wiki/Topics/Sample Paper Outline.md"},
  {"id": "paper-glossary", "type": "term_list", "sources": "sample-paper", "section": "^Glossary$",
   "term": "^\\*\\*(.+?)\\*\\*", "output": "Wiki/Concepts/Sample Paper Glossary.md"},
  {"id": "findings-table", "type": "catalog_table", "kinds": ["finding"],
   "columns": ["note", "section", "status", "summary"], "group_by": "dataset",
   "output": "Wiki/Generated/Findings Table.md"},
  {"id": "findings-base", "type": "bases_view", "kinds": ["finding"], "where": {"status": "stable"},
   "views": [{"name": "By dataset", "columns": ["note", "section"], "group_by": "dataset"}],
   "output": "Wiki/Views/Findings.base"}
]
```

A profile's `generators.py` can still produce files in Python. Prefer the declarative generators.

## Profiles

A profile adds domain-specific behaviour through optional plugins in `scripts/profiles/<profile>/`:
- `rules.py`: extra lint and source-lint rules
- `generators.py`: files produced by `build`, and checked by K1
- `converters.py`: raw document → source note, run by the `convert` command

The interface is described in `scripts/profiles/plugin-interface.md`. The `default` profile has no plugins.

## sync-schema

```bash
python3 scripts/wiki_tool.py sync-schema          # write templates + Schema/field-reference.md
python3 scripts/wiki_tool.py sync-schema --check  # only report what is out of date (exit 1)
```

Generates from the configuration:
- the frontmatter of `_templates/source-note.md` and of `_templates/<tag>-note.md` for every kind. Template bodies are kept, and new templates get a minimal body.
- `Schema/field-reference.md`: tables of all source fields, core fields, kinds and extra fields.

Output is deterministic. `lint` reports files out of sync with the config as K5.

## convert

```bash
python3 scripts/wiki_tool.py convert --list
python3 scripts/wiki_tool.py convert <name> <input-file> --output Raw/Sources/<YYYY-MM-DD-slug>.md [--force]
```

Runs a converter from the active profile. The output becomes a normal source note, and from then on the Raw rules apply to it. Check the result, run `source-lint`, then ingest it.

## Typical sequences

```bash
# After ingesting a new source
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py lint
python3 scripts/wiki_tool.py source-scan --update --accept-covered
python3 scripts/wiki_tool.py source-lint
python3 scripts/wiki_tool.py log --title "ingest | <source title>" --details "<notes created/updated>"

# What still needs ingesting?
python3 scripts/wiki_tool.py source-coverage --uncovered
python3 scripts/wiki_tool.py source-delta
```
