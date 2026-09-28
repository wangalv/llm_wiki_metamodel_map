---
name: llm-wiki-maintain
description: Restructure the compiled Wiki without losing citations — merge duplicate notes, split oversized notes, rename notes, re-home misfiled notes, and refresh stale notes against their sources. Use when the user asks to merge, split, rename, reorganise, clean up, dedupe or refresh wiki notes.
---

# LLM Wiki: Maintain

Change the structure of `Wiki/` while keeping every claim cited and every link working. See `Schema/workflow-examples.md` §4.

## Before any change

- Look at the affected notes in `Wiki/catalog.jsonl`: their `sources`, `aliases`, and which other notes link to them.
- Tell the user the plan: which notes get kept, merged, renamed or deleted, and how many links will change.
- Never delete or rewrite anything in `Raw/`.

## Operations

### Merge duplicates
1. Choose the note to keep: the most common name, with the most inbound links.
2. Move over the unique, cited content from the other note, keeping each citation exactly.
3. Combine the `sources` and `topics` lists and update `source_count`. Add the other note's title and aliases to `aliases`.
4. Point every `[[Other]]` link at `[[Kept]]`, then delete the other note.

### Split an oversized note
1. Pick sections that stand on their own as a single note of one kind.
2. Move each one into a new note started from its `_templates/<kind>-note.md`. Its `sources` and `source_count` should cover only the sources cited in the moved text.
3. In the original note, leave a one-line summary and a link in place of each moved section.

### Rename
1. Rename the file following `Schema/naming-conventions.md`. The filename is the note's title.
2. Add the old name to `aliases`.
3. Update every `[[Old Name]]` and `[[Old Name#…]]` link. Keep display text: `[[New Name|Old Name]]`.

### Re-home a note filed under the wrong type
Move the note to the right `Wiki/` subfolder, and change its single tag to match the kind (see `Schema/wiki-config.json` and `scripts/profiles/togaf-core/togaf-core-profile.md`). Add or remove kind-specific fields (e.g. `classification_basis`) as the new kind requires. The filename stays the same, so links still work.

### Refresh a stale note
1. Re-read the note's cited sources, plus any newer Raw sources on the same subject (find them via the catalog).
2. Correct claims that are wrong or outdated, keeping citations accurate. Add `> [!question]` callouts where sources disagree.
3. Set `status` to `stable` if everything is cited and resolved, or keep `stale` and explain why in the log.

## After any change

1. Set `updated` to today on every note you touched.
2. Run `python3 scripts/wiki_tool.py build`, `lint` and `source-lint`. There must be no errors. In particular, no citations or links may be lost.
3. If coverage changed, e.g. after a merge or split, run `python3 scripts/wiki_tool.py source-scan --update`.
4. Log it: `python3 scripts/wiki_tool.py log --title "maintain | <operation>" --details "<notes changed, links rewritten>"`.
5. Report to the user. Commit only if they ask.
