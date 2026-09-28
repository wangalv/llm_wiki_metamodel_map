---
name: llm-wiki-ingest
description: Compile a source from Raw/Sources/ (and its Raw/Files/ attachments) into cited notes under Wiki/. Use when the user asks to ingest, process, compile, summarise into the wiki, or "add to the wiki" a source, article, paper, PDF or transcript in this vault.
---

# LLM Wiki: Ingest

Turn one or more Raw sources into Wiki notes, following `AGENTS.md`. Formats are defined in `Schema/frontmatter-schema.md` and `Schema/naming-conventions.md`, and there's a full worked example in `Schema/workflow-examples.md` §1.

## Steps

1. **Identify the source(s).**
   - Resolve what the user means to specific files in `Raw/Sources/`.
   - If the user gave a URL or file that isn't in `Raw/` yet, capture it first as a source note:
     - Start from `_templates/source-note.md` and fill in `Title`, `Author`, `Reference`, `ContentType` and `Created`, with `Processed: false`.
     - Name it per the naming conventions. Put attachments in `Raw/Files/` and embed them in the body.
     - For web pages, use the `defuddle` skill if it's available.
   - Once a source note exists, don't edit its body.

2. **Check what's already compiled.**
   - Search the catalog for the source's key terms, titles and aliases: `python3 scripts/wiki_tool.py search-catalog --query "<term>"`.
   - Check whether the source is already covered: `python3 scripts/wiki_tool.py source-coverage`.
   - Don't scan `Raw/` broadly.

3. **Read the source.** Read the whole source note and any attachments embedded in it. For each claim worth keeping, note where it appears (heading or block), so you can cite that exact place.

4. **Plan, then confirm with the user if it's non-trivial.**
   - Make a table of the notes you'll create or update, with the type and reason for each.
   - Prefer updating existing notes over creating near-duplicates. Check titles and `aliases`.
   - Only create a note if the source says something substantive about it — don't create one just because a name appears in passing.
   - Follow "No representative sampling" in `scripts/profiles/togaf-core/togaf-core-profile.md`: if the source names several distinct instances of the same kind, that's several notes, not one.

5. **Write the notes.**
   - Start each note from `_templates/<kind>-note.md`, using the kind `scripts/profiles/togaf-core/togaf-core-profile.md` says fits.
   - Fill all required frontmatter:
     - Exactly one tag for the note's kind
     - `topics` it belongs under
     - The source in `sources`, with `source_count` matching
   - Write a one-sentence summary right after the `# Heading`. Remove the template's guidance comments and any empty sections.
   - Cite claims inline: `([[source-stem]])`, or `([[source-stem#Heading]])` for a specific place.
   - Link to related Wiki notes with wikilinks, in a `## Related` section, labelling the connection in plain language (see the profile doc's "How connections are made"). Link each new note from at least one other note that gives it context, and set its `topics` to the relevant `domain` note(s).
   - Where sources disagree or leave gaps, add a `> [!question]` callout. Don't guess.
   - For a new note, set `status: seed` and `created`/`updated` to today.
   - When adding to an existing note, bump `updated`, and move `seed` → `growing`.

6. **Build, check and mark the source processed.** Fix every error before moving on.
   ```bash
   python3 scripts/wiki_tool.py build
   python3 scripts/wiki_tool.py lint
   python3 scripts/wiki_tool.py source-scan --update --accept-covered   # Processed: true + manifest
   python3 scripts/wiki_tool.py source-lint
   ```
   `--accept-covered` is the only thing that edits `Raw/`: it flips `Processed` to `true` in covered sources.

7. **Log it:**
   ```bash
   python3 scripts/wiki_tool.py log --title "ingest | <source title>" --details "Created …; updated …; skipped …"
   ```
   (This vault has no `log` kind, so there's no detailed daily note beyond `Wiki/log.md`.)

8. **Report** to the user: the notes you created or updated, any open questions you recorded, and any warnings. Commit only if the user asks.

## Don'ts

- Don't cite a source you didn't open, or a section that doesn't say what you claim.
- Don't copy long passages. Summarise in your own words; short quotes (under 15 words) are fine if cited.
- Don't write compiled content anywhere except `Wiki/`.
