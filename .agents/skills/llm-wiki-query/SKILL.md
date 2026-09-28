---
name: llm-wiki-query
description: Answer a question using this vault's compiled Wiki, catalog-first, with citations to Raw sources. Use when the user asks what the wiki/vault/notes say about something, asks a research question about collected material, or wants a summary across notes.
---

# LLM Wiki: Query

Answer from compiled knowledge first, and from Raw sources only to confirm details. See `AGENTS.md` rule 4 and `Schema/workflow-examples.md` §2.

## Steps

1. **Search the catalog.**
   - Search the catalog for the question's key terms, synonyms and likely aliases:
     ```bash
     python3 scripts/wiki_tool.py search-catalog --query "term"
     ```
   - Run `build` first if the catalog might be stale; `doctor` will tell you.
   - Use each match's `summary`, `topics`, `links` and `sources` to decide what to open.

2. **Read the matching Wiki notes.** Follow `topics` and `links` one hop out if the question needs it.

3. **Confirm details in Raw.**
   - Only open Raw sources that the relevant Wiki notes cite.
   - Scan `Raw/Sources/` broadly only if the catalog and Wiki have nothing, and say that you did.

4. **Answer.**
   - Link the Wiki notes with `[[Note]]` so the user can navigate to them.
   - Back factual statements with citations to Raw sources: `[[source-stem]]` or `[[source-stem#Heading]]`.
   - Say plainly what the vault doesn't cover. Don't fill gaps from general knowledge without labelling it: "Not in the vault — general knowledge: …".
   - Mention any `> [!question]` callouts or `status: stale` notes that affect the answer.

5. **Suggest follow-ups.** Point out missing notes or missing sources that would improve the answer.

## Writing

- Queries are read-only by default. Don't create or edit Wiki notes unless the user asks.
- If the user wants the answer saved, store it as a Wiki note using the `llm-wiki-ingest` conventions:
  - Cite Raw sources, not the chat.
  - Follow the schema.
  - Run the checks, and log it with `wiki_tool.py log --title "query | <question>"`.
