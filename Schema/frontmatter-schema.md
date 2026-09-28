# Frontmatter Schema

Every Markdown note in `Raw/Sources/` and `Wiki/` starts with YAML frontmatter. Start new notes from the matching template in `_templates/`.

This file explains the default fields and the rules behind them. The authoritative, generated list of every field, its type and whether it's required, including any extra fields a profile adds, is in **`Schema/field-reference.md`**. Regenerate it with `sync-schema`.

General rules:
- Dates are ISO `YYYY-MM-DD`.
- Links inside frontmatter are quoted wikilinks, e.g. `"[[Note Name]]"`, so Obsidian updates them on rename.
- A note's title is its filename. There is no separate title field on compiled notes.

## Source notes: `Raw/Sources/*.md`

Template: `_templates/source-note.md`

```yaml
---
Title: "Attention Is All You Need"
Author: "Ashish Vaswani et al."
Reference: "https://arxiv.org/abs/1706.03762"
ContentType:
  - "markdown"
  - "pdf"
Created: 2026-09-25
Processed: false
tags:
  - "source"
---
```

| Field | Required | Notes |
|---|---|---|
| `Title` | yes | The source's own title |
| `Author` | yes | As written in the source. Use `""` if unknown; never guess. |
| `Reference` | yes | URL, DOI or bibliographic reference. Use `""` if there is none. |
| `ContentType` | yes | List of what the source contains: `markdown`, `pdf`, `image`, `audio`, `video`, `transcript`, `dataset`, `other` |
| `Created` | yes | Date the source was added to the vault |
| `Processed` | yes | `false` when captured. Set to `true` by `llm-wiki-ingest` once the source is compiled into `Wiki/`. |
| `tags` | yes | Must include `source` |

The body holds the captured content. Attachments live in `Raw/Files/` and are embedded in the body, e.g. `![[2017-06-12-attention-is-all-you-need.pdf]]`.

Agents never rewrite a source note. The one exception is flipping `Processed` from `false` to `true`, which is the only edit an agent makes to `Raw/`.

## Compiled notes: `Wiki/**/*.md`

Templates: `_templates/<kind>-note.md`, one per kind in `Schema/wiki-config.json` (e.g. `actor-note.md`, `business-capability-note.md`). Run `ls _templates/` for the current list.

```yaml
---
tags:
  - "actor"
topics:
  - "[[Financial Services Compliance]]"
status: seed
created: 2026-09-28
updated: 2026-09-28
sources:
  - "[[2026-09-27-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases: []
classification_basis: "One sentence, quoting or closely paraphrasing the source, saying why this note is this kind and not another."
---
```

| Field | Required | Notes |
|---|---|---|
| `tags` | yes | Exactly one tag from the allowed list below. It must match the note's folder. |
| `topics` | yes (may be `[]`) | Wikilinks to the notes of the `topics_kind` kind this note belongs under — `Wiki/Domains/` in this vault. |
| `status` | yes | `seed` \| `growing` \| `stable` \| `stale` (see below) |
| `created` | yes | Date the note was created |
| `updated` | yes | Date of the last change; must be on or after `created` |
| `sources` | yes | Wikilinks to `Raw/Sources/` notes. Every kind in this vault requires at least one (`requires_sources: true`). Every source cited in the body must be listed here. |
| `source_count` | yes | Must equal the number of entries in `sources` |
| `aliases` | yes (may be `[]`) | Other names, used for search, link suggestions and duplicate detection |

### Allowed compiled-note tags

The kinds, their folders and their behaviour are configured in `Schema/wiki-config.json` (`kinds`) and listed in the generated `Schema/field-reference.md`: the 23 TOGAF Content Metamodel core types, plus `domain` — the grouping kind `topics` points to, not part of the metamodel itself. See `scripts/profiles/togaf-core/togaf-core-profile.md` for what each type means and when to use it.

Don't add any other tags to compiled notes. Use `topics` for grouping. The allowed `status` values and the required fields also come from `wiki-config.json`.

### Status

| Value | Meaning |
|---|---|
| `seed` | First pass, compiled from one or a few sources |
| `growing` | Being extended as more sources arrive |
| `stable` | Reviewed: every claim cited, no open questions |
| `stale` | Sources are outdated or conflict; needs a refresh (`llm-wiki-maintain`) |

### Log notes

`Wiki/log.md` is the short append-only activity log, written by `python3 scripts/wiki_tool.py log`. It has no frontmatter and isn't a compiled note. This vault has no `log` kind, so there are no detailed per-day log notes — `Wiki/log.md` is the only log.

### Body

- The first line after the `# Heading` is a one-sentence summary. `build` copies it into the catalog.
- Put a citation at the end of each factual sentence or paragraph (see below).

## Citations in the body

Put an inline wikilink to the Raw source at the end of the sentence or paragraph it supports:

```markdown
Self-attention lets every position attend to every other position in one step ([[2017-06-12-attention-is-all-you-need]]).
```

To point at a specific place, link to a heading or block in the source:

```markdown
... ([[2017-06-12-attention-is-all-you-need#3.2 Attention]]).
```

Rules:
- Cite only Raw sources, not other Wiki notes. Wiki notes are for navigation, not evidence.
- Every cited source must also appear in `sources`.
- A claim that no source supports doesn't go in the body as fact.

### Open questions

When sources disagree, or don't answer something important, record it instead of guessing:

```markdown
> [!question] Open question
> Source A says X ([[source-a]]); source B says Y ([[source-b]]). Not resolved.
```

## `Wiki/catalog.jsonl`

`build` generates this file: one JSON object per line, one line per note in `Wiki/`. Never hand-edit it.

```json
{"path": "Wiki/Actors/Customer.md", "title": "Customer", "tag": "actor", "summary": "The individual or entity going through the KYC onboarding and verification journey.", "topics": ["Wiki/Domains/Financial Services Compliance.md"], "aliases": [], "status": "seed", "sources": ["Raw/Sources/2026-09-27-modernizing-kyc-aws-serverless.md"], "source_count": 1, "links": ["Wiki/Data Entities/KYC Decision.md"], "updated": "2026-09-28"}
```

| Key | Content |
|---|---|
| `path` | Vault-relative path |
| `title` | Filename without `.md` |
| `tag` | The note's single compiled-note tag |
| `summary` | First sentence after the `# Heading` |
| `topics`, `sources` | Frontmatter wikilinks resolved to vault-relative paths |
| `links` | Outgoing body wikilinks to other Wiki notes, resolved to paths |
| `aliases`, `status`, `source_count`, `updated` | Copied from frontmatter |
