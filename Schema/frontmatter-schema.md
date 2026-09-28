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

Templates:
- `_templates/topic-note.md`
- `_templates/concept-note.md`
- `_templates/entity-note.md`
- `_templates/project-note.md`
- `_templates/log-note.md`

```yaml
---
tags:
  - "concept"
topics:
  - "[[Large Language Models]]"
status: seed
created: 2026-09-25
updated: 2026-09-25
sources:
  - "[[2017-06-12-attention-is-all-you-need]]"
source_count: 1
aliases:
  - "Scaled dot-product attention"
---
```

| Field | Required | Notes |
|---|---|---|
| `tags` | yes | Exactly one tag from the allowed list below. It must match the note's folder. |
| `topics` | yes (may be `[]`) | Wikilinks to the `Wiki/Topics/` notes this note belongs under. Topic and log notes normally leave it empty. |
| `status` | yes | `seed` \| `growing` \| `stable` \| `stale` (see below) |
| `created` | yes | Date the note was created |
| `updated` | yes | Date of the last change; must be on or after `created` |
| `sources` | yes | Wikilinks to `Raw/Sources/` notes. Topic, concept, entity and project notes need at least one. Every source cited in the body must be listed here. |
| `source_count` | yes | Must equal the number of entries in `sources` |
| `aliases` | yes (may be `[]`) | Other names, used for search, link suggestions and duplicate detection |

### Allowed compiled-note tags

The kinds, their folders and their behaviour are configured in `Schema/wiki-config.json` (`kinds`). A profile may add more kinds. The defaults are:

| Tag | Folder |
|---|---|
| `topic` | `Wiki/Topics/` |
| `concept` | `Wiki/Concepts/` |
| `entity` | `Wiki/Entities/` |
| `project` | `Wiki/Projects/` |
| `log` | `Wiki/Logs/` |

Don't add any other tags to compiled notes. Use `topics` for grouping. The allowed `status` values and the required fields also come from `wiki-config.json`. The tables here show the defaults.

### Status

| Value | Meaning |
|---|---|
| `seed` | First pass, compiled from one or a few sources |
| `growing` | Being extended as more sources arrive |
| `stable` | Reviewed: every claim cited, no open questions |
| `stale` | Sources are outdated or conflict; needs a refresh (`llm-wiki-maintain`) |

### Log notes

`Wiki/log.md` is the short append-only activity log, written by `python3 scripts/wiki_tool.py log`. It has no frontmatter and isn't a compiled note.

Detailed daily log notes in `Wiki/Logs/` use the same frontmatter as other compiled notes, with `tags: ["log"]`. They're named `Wiki/Logs/YYYY-MM-DD.md`, and their `sources` field lists every Raw source read that day (it may be `[]`). The body has one `##` section per operation. See `Schema/workflow-examples.md`.

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
{"path": "Wiki/Concepts/Self-Attention.md", "title": "Self-Attention", "tag": "concept", "summary": "A layer where each token computes a weighted mix of all tokens in the sequence.", "topics": ["Wiki/Topics/Large Language Models.md"], "aliases": ["Scaled dot-product attention"], "status": "seed", "sources": ["Raw/Sources/2017-06-12-attention-is-all-you-need.md"], "source_count": 1, "links": ["Wiki/Concepts/Transformer.md"], "updated": "2026-09-25"}
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
