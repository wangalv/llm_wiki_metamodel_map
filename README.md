# LLM Wiki Metamodel Mapper

An Obsidian vault that turns organisational technical documents (architecture descriptions, design documents, data dictionaries) into a wiki structured by the TOGAF 9.2 Content Metamodel's 23 core objects, plus a `domain` grouping kind the engine requires.

Built from [LLM Wiki Core](https://github.com/wangalv/llm_wiki_starter), following its `PROFILE-GUIDE.md`. The domain-specific rules live in `scripts/profiles/togaf-core/togaf-core-profile.md` — read that first; it defines every note type, how notes should link to each other, and a "no representative sampling" rule (extract every distinct named instance of a type, not just one example).

## Status

This vault ships empty: no sources ingested yet, ready for a first real document.

## Daily use

Run these from this folder.

```bash
python3 scripts/wiki_tool.py doctor        # health check
python3 scripts/wiki_tool.py source-lint   # check a new source in Raw/Sources/
python3 scripts/wiki_tool.py build         # rebuild indexes and the two generated tables
python3 scripts/wiki_tool.py lint          # check the notes
python3 scripts/wiki_tool.py source-scan --update --accept-covered   # mark a source processed
python3 scripts/wiki_tool.py log --title "ingest | <title>" --details "<notes>"
```

To add a document: save it in `Raw/Sources/` as `YYYY-MM-DD-kebab-slug.md` with `Processed: false`, then ask the agent to ingest it following `scripts/profiles/togaf-core/togaf-core-profile.md`.

Every new note starts `status: seed`. After each ingest, `Wiki/Generated/Review Queue.md` lists everything pending your review — read each note's `classification_basis`, then confirm, fix, merge or delete it.

To change the rules: edit `Schema/wiki-config.json`, then run `sync-schema`, `build` and `lint`.

Install the git hook once (repo root, since this is its own repo): `bash scripts/install_hooks.sh`.
