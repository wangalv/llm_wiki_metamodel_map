# Naming Conventions

Obsidian resolves `[[wikilinks]]` by **filename**. For that reason, every Markdown filename must be unique across the whole vault, regardless of folder.

## Raw

| Kind | Pattern | Example |
|---|---|---|
| Source note | `Raw/Sources/YYYY-MM-DD-kebab-slug.md` | `2017-06-12-attention-is-all-you-need.md` |
| Attachment | `Raw/Files/YYYY-MM-DD-kebab-slug.ext` | `2017-06-12-attention-is-all-you-need.pdf` |

- `YYYY-MM-DD` is the source's **published** date if known. Otherwise use the date it was added to the vault (its `Created` field).
- `kebab-slug` is lowercase ASCII, with words joined by `-`, max about 60 characters, based on the source title.
- An attachment and its source note share the same stem.
- If two sources would get the same name, add `-2`, `-3`, … to the later one.

## Wiki

| Kind | Pattern | Example |
|---|---|---|
| Compiled note (any TOGAF kind) | `Wiki/<Kind>/Title Case.md` | `Wiki/Actors/Customer.md`, `Wiki/Business Capabilities/Know Your Customer (KYC) Validation.md` |

See `Schema/field-reference.md` for the current kind list and their folders, and `scripts/profiles/togaf-core/togaf-core-profile.md` for which kind to use.

- The filename is the note's title. Use the most common name for the thing, and put other names in `aliases`.
- Use singular nouns for concepts (`Embedding`, not `Embeddings`), unless the plural is the usual name.
- Keep the official spelling and capitalisation of names (`GitHub`, `arXiv`, `PyTorch`).
- Filenames can't contain `/ \ : * ? " < > | # ^ [ ]`. Spell things out or drop the character (`C#` → `C Sharp`).
- Keep acronyms in the title only if the acronym is how people usually say it (`RAG` → `Retrieval-Augmented Generation`, with alias `RAG`).
- If a concept and an entity would share a name, add the kind in parentheses: `Python (Language)`, `Python (Snake)`.

## Other files

| Kind | Pattern |
|---|---|
| Templates | `_templates/<kind>-note.md` (e.g. `_templates/concept-note.md`) |
| Schema docs | `Schema/kebab-case.md` |
| Skills | `.agents/skills/kebab-case/SKILL.md` |
| Scripts | `scripts/snake_case.py` |

## Tags

- Compiled notes have exactly one tag, which marks the note's kind — one of the kinds in `Schema/wiki-config.json`. It must match the folder.
- Source notes carry `source`. Extra tags on source notes are allowed, in lowercase kebab-case, e.g. `ml/architecture`.
- Group compiled notes by subject with `topics: ["[[Topic]]"]`, not with tags.

## Renaming

Rename files through Obsidian or the `llm-wiki-maintain` skill so that links get updated. After a rename:

1. Add the old name to `aliases`.
2. Run `build` and `lint`.
3. Record the rename in today's log.
