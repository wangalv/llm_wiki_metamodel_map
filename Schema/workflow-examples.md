# Workflow Examples

These are worked examples of the four workflows. The source and notes are illustrative; the file formats follow `Schema/frontmatter-schema.md`.

---

## 1. Ingest a source (`llm-wiki-ingest`)

**Person:** "Ingest the attention paper I just added."

**Step 1. Find the source.** Assume it's `Raw/Sources/2017-06-12-attention-is-all-you-need.md`, with `Processed: false`, and with the PDF embedded as `![[2017-06-12-attention-is-all-you-need.pdf]]`.

**Step 2. Check the catalog first.**

```bash
python3 scripts/wiki_tool.py search-catalog --query "attention"
python3 scripts/wiki_tool.py search-catalog --query "transformer"
```

Suppose this finds `Wiki/Topics/Large Language Models.md`, but no `Transformer` or `Self-Attention` note.

**Step 3. Read the source.** Read it, and the PDF if needed. Note the claims worth keeping and where each one appears (section headings).

**Step 4. Plan the changes and tell the person before writing:**

| Action | Note | Why |
|---|---|---|
| create | `Wiki/Concepts/Transformer.md` | Main subject of the source |
| create | `Wiki/Concepts/Self-Attention.md` | Core mechanism, reused elsewhere |
| create | `Wiki/Entities/Ashish Vaswani.md` | Lead author; skip if only named once |
| update | `Wiki/Topics/Large Language Models.md` | Add a link and one cited sentence |

**Step 5. Write the notes** from `_templates/concept-note.md`. For example, `Wiki/Concepts/Self-Attention.md`:

```markdown
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

# Self-Attention

A layer where each token computes a weighted mix of all tokens in the sequence.

Each position computes queries, keys and values, and takes a softmax-weighted sum of the values ([[2017-06-12-attention-is-all-you-need#3.2 Attention]]).

Used as the core layer of the [[Transformer]].
```

**Step 6. Build, lint, and mark the source processed.**

```bash
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py lint
python3 scripts/wiki_tool.py source-scan --update --accept-covered   # sets Processed: true, updates the manifest
python3 scripts/wiki_tool.py source-lint
```

`--accept-covered` flips `Processed: false` → `true` in the source note. This is the only edit allowed in `Raw/`.

**Step 7. Log the change,** then commit if the person asks. The pre-commit hook re-runs the checks.

```bash
python3 scripts/wiki_tool.py log --title "ingest | Attention Is All You Need" \
  --details "Created [[Transformer]], [[Self-Attention]]. Updated [[Large Language Models]]. Skipped author entities (named only in the byline)."
```

---

## 2. Answer a question (`llm-wiki-query`)

**Person:** "What's the difference between self-attention and cross-attention?"

1. Search the catalog, not `Raw/`:
   ```bash
   python3 scripts/wiki_tool.py search-catalog --query "attention"
   ```
2. Open the matching Wiki notes, e.g. `Self-Attention.md`. There's no `Cross-Attention` note.
3. Open only the Raw sources those notes cite, to confirm the details.
4. Answer, citing Wiki notes for navigation and Raw sources for evidence:

   > Self-attention draws queries, keys and values from the same sequence ([[2017-06-12-attention-is-all-you-need#3.2 Attention]]). The Wiki has no note on cross-attention, and the ingested sources only mention it in passing, so I can't give a sourced comparison yet.
   >
   > Gap: no `Cross-Attention` note. Add a source that covers encoder-decoder attention, and I'll ingest it.

5. Don't write to `Wiki/` during a query unless the person asks. Point out gaps instead.

---

## 3. Lint (`llm-wiki-lint`)

**Person:** "Lint the wiki."

```bash
python3 scripts/wiki_tool.py lint
python3 scripts/wiki_tool.py source-lint
```

Example report:

```
ERROR S2  Wiki/Entities/OpenAI.md: source [[2024-05-01-gpt4o-launch]] not found in Raw/Sources/
ERROR F4  Wiki/Concepts/Embedding.md: source_count is 1 but sources lists 2
WARN  L3  Wiki/Concepts/Tokenizer.md: no inbound links from Wiki/
WARN  S7  Raw/Files/2025-01-10-scan.pdf: not referenced by any source note
```

What to do with each:

| Finding | Fix |
|---|---|
| S2 | Look for the source under a different name. If it's really missing, ask the person. **Don't** create a fake source note. |
| F4 | Set `source_count: 2` to match `sources`. |
| L3 | Link it from the relevant topic note, e.g. `[[Large Language Models]]`. |
| S7 | Ask the person whether to create a source note for the file. |

Report what you fixed and what needs a person to decide.

---

## 4. Maintain (`llm-wiki-maintain`)

**Person:** "`LLM` and `Large Language Models` look like duplicates."

1. Compare both notes: their `sources`, `aliases` and inbound links (`links` in the catalog).
2. Choose the one to keep (`Large Language Models`).
3. Move any cited content from the other note into it, keeping each citation.
4. Merge the `sources` lists, update `source_count`, merge `topics`, and add `LLM` to `aliases`.
5. Update inbound links from `[[LLM]]` to `[[Large Language Models]]`, then delete `LLM.md`. Deleting a Wiki note is fine; Raw files are never deleted.
6. Set `updated`, run `build`, `lint` and `source-lint`, and log it:

```bash
python3 scripts/wiki_tool.py log --title "maintain | merge LLM → Large Language Models" \
  --details "Moved 2 cited paragraphs, merged 3 sources, added alias LLM, relinked 4 notes."
```
