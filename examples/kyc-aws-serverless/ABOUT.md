# Example: KYC + agentic AI on AWS

A static, browse-only snapshot of one real ingest — 49 compiled notes across 11 of the 23 TOGAF Content
Metamodel types, produced by `scripts/auto_ingest.py --provider openai` (gpt-5) over a condensed, own-words
stand-in for a real AWS architecture blog post about modernising KYC with serverless services and agentic AI.

**This is reference material, not part of the vault.** `wiki_tool.py`'s `build`/`lint`/`doctor` only look at the
top-level `Raw/`/`Wiki/`, never here — this folder is never scanned, checked, or counted. Open it in Obsidian
(as part of the same vault, since it's still inside the repo) to click through the notes and their links, or
just read the Markdown directly on GitHub.

- `Raw/Sources/2026-09-28-modernizing-kyc-aws-serverless.md` — the (condensed, own-words) source. `Reference`
  in its frontmatter links to the real article; the full text isn't reproduced here.
- `Wiki/` — the 49 compiled notes, one folder per TOGAF type, same layout as the real vault.

Every note here still starts `status: seed` — it was never run through the human-review step
(`Wiki/Generated/Review Queue.md` in a real ingest) that step 5 of "Add and ingest a document" in the root
README calls for. Treat it as "what a fresh ingest produces," not as a model of a fully reviewed note.

See the root [README.md](../../README.md) for how to run this yourself against your own documents.
