---
name: llm-wiki-lint
description: Check this vault against its schema and agent rules (frontmatter, citations, links, naming, catalog, Raw integrity) and fix what can safely be fixed. Use when the user asks to lint, validate, check or health-check the wiki, or before committing Wiki changes.
---

# LLM Wiki: Lint

Run the checks in `Schema/lint-checklist.md`, then report and fix the problems. See `Schema/workflow-examples.md` §3.

## Steps

1. **Run the checks** from the vault root:
   ```bash
   python3 scripts/wiki_tool.py build
   python3 scripts/wiki_tool.py lint
   python3 scripts/wiki_tool.py source-lint
   ```
   Also run `python3 scripts/audit_public.py` before anything is published. The finding codes are explained in `Schema/command-reference.md`.

   The scripts don't cover S8, L5, C1, K2 and K3; review those by hand. If a command fails to run at all, go through `Schema/lint-checklist.md` by hand:
   - Read the frontmatter of every file in `Wiki/` and `Raw/Sources/`.
   - Resolve every wikilink against the vault's filenames.
   - Tell the user the checks were done by hand.

2. **Sort the findings** by severity: **errors** first, then **warnings**, each tagged with its checklist ID (F1, S2, …).

3. **Fix only what's safe and mechanical:**
   - Missing `updated`, or a `source_count` that doesn't match `sources`
   - `Processed` out of sync with whether any Wiki note cites the source (S9)
   - Out-of-date `catalog.jsonl` (re-run `build`)
   - Orphans that clearly belong linked from an existing note
   - Broken links caused by a rename you can find

4. **Ask the user about anything else.** Especially:
   - A missing source (S2): never create a stand-in source note.
   - Uncited claims (C1): find a real citation in the note's sources, or remove the claim. Never add a citation to a source that doesn't support it.
   - Likely duplicates (N4): hand off to `llm-wiki-maintain`.
   - Changes to `Raw/` (K2).

5. **Re-run the checks** after fixing, until there are no errors.

6. **Log it and report.**
   - If you changed anything, log it: `python3 scripts/wiki_tool.py log --title "lint | <summary>" --details "<fixes>"`.
   - Report to the user: what you fixed, what still needs their decision, and any remaining warnings.
