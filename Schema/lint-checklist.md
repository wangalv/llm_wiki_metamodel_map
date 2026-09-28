# Lint Checklist

`python3 scripts/wiki_tool.py lint` checks compiled Wiki notes, and `python3 scripts/wiki_tool.py source-lint` checks Raw sources and the manifest. See `Schema/command-reference.md` for details.

The scripts don't check **S8, L5, C1, K2 and K3** (L5 only partly). Check those by hand, in review.

Severity:
- **error**: blocks a commit.
- **warn**: fix it or mention it in the log.

## 1. Frontmatter

| # | Check | Severity |
|---|---|---|
| F1 | Every `.md` file in `Raw/Sources/` and `Wiki/` has valid YAML frontmatter | error |
| F2 | All required fields are present: the source-note fields in `Raw/Sources/`, the compiled-note fields in `Wiki/` (`Schema/frontmatter-schema.md`) | error |
| F3 | A compiled note has exactly one tag, from `topic`, `concept`, `entity`, `project`, `log`, and it matches the note's folder. A source note's `tags` include `source`. | error |
| F4 | `source_count` equals the number of entries in `sources` | error |
| F5 | Dates are `YYYY-MM-DD`, and `updated` is on or after `created` | error |
| F6 | `status` is one of `seed`, `growing`, `stable`, `stale`. `Processed` is `true` or `false`. | error |
| F7 | The first line after the `# Heading` is a one-sentence summary of 200 characters or fewer | warn |
| F8 | Every `topics` entry links to a note in `Wiki/Topics/` | error |
| F9 | Typed fields (`Schema/field-reference.md`) have the declared type, allowed value, pattern and link target | error |

## 2. Sources and citations (`lint` S1–S5, `source-lint` S6–S9)

| # | Check | Severity |
|---|---|---|
| S1 | Every topic, concept, entity and project note has at least one entry in `sources` | error |
| S2 | Every `sources` entry resolves to an existing file in `Raw/Sources/` | error |
| S3 | Every inline citation `[[...]]` pointing at a Raw source resolves, including the `#heading` if one is given | error |
| S4 | Every source cited in the body is listed in `sources` | error |
| S5 | Every source listed in `sources` is cited at least once in the body | warn |
| S6 | Every attachment embedded in a source note (`![[...]]`) resolves to an existing file in `Raw/Files/` | error |
| S7 | Every file in `Raw/Files/` is embedded in at least one source note | warn |
| S9 | A source marked `Processed: true` is cited by at least one compiled Wiki note | error |
| S9 | A source cited by Wiki notes but still `Processed: false` (fix with `source-scan --update --accept-covered`) | warn |
| S8 | Wiki notes don't cite other Wiki notes as evidence | warn |

## 3. Links and structure

| # | Check | Severity |
|---|---|---|
| L1 | No broken wikilinks in `Wiki/` | error |
| L2 | Every Markdown filename is unique across the vault | error |
| L3 | Every concept, entity and project note is linked from at least one other Wiki note (no orphans) | warn |
| L4 | Every Raw source is cited by at least one Wiki note, i.e. it has been ingested (see also S9) | warn |
| L5 | No Wiki-style compiled content outside `Wiki/` | warn |

## 4. Naming (`Schema/naming-conventions.md`)

| # | Check | Severity |
|---|---|---|
| N1 | Raw filenames match `YYYY-MM-DD-kebab-slug.ext` | error |
| N2 | Wiki filenames contain no forbidden characters | error |
| N3 | Log filenames match `YYYY-MM-DD.md` | error |
| N4 | Two notes whose titles differ only in case, plural or an alias are likely duplicates | warn |

## 5. Content

| # | Check | Severity |
|---|---|---|
| C1 | No factual paragraph without a citation. Headings, definitions of the note's own title, and `[!question]` callouts are exempt. | warn |
| C2 | No placeholder text left from templates (`YYYY-MM-DD`, `{{title}}`, `source-stem`, empty `<!-- -->` guidance comments, `TODO`) | warn |
| C3 | Notes with `status: stable` have no open `[!question]` callouts | warn |

## 6. Catalog and Raw integrity

| # | Check | Severity |
|---|---|---|
| K1 | Everything `build` writes is up to date: catalog, indexes, and configured or profile generator outputs. Running `build` produces no diff. | error |
| K2 | `git diff` on `Raw/` only adds files or flips `Processed: false` → `true`. Any other change to an existing file needs a person's request. | error |
| K3 | `Wiki/log.md` has an entry for every Wiki change being committed | warn |
| K4 | No note in `Wiki/` or `Raw/` is ignored by `.gitignore`, which would silently leave it out of commits | error |
| K5 | `_templates/*-note.md` frontmatter and `Schema/field-reference.md` match `Schema/wiki-config.json` (run `sync-schema`) | error |
| M1 | `Schema/source-manifest.jsonl` exists, parses, and matches the sources on disk (run `source-scan --update`) | error if it doesn't parse, warn if it's out of date |

## 7. Configured and profile rules

- **Declarative rules:** the rules listed under `rules` in `Schema/wiki-config.json`, taken from the rule library (`Schema/command-reference.md#rules`). They report under their own IDs, and `Schema/field-reference.md` lists the active ones.
- **Python rules:** the active profile (`Schema/wiki-config.json` → `profile`) may add its own checks through `scripts/profiles/<profile>/rules.py`. Their codes use a profile prefix, e.g. `LG1` for legislation, and are documented in `scripts/profiles/<profile>/<profile>-profile.md`. The `default` profile adds none.

## Before committing

The pre-commit hook runs the first three of these commands, plus `audit_public.py`:

```bash
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py lint
python3 scripts/wiki_tool.py source-lint
python3 scripts/audit_public.py
git status        # generated files, the manifest and Wiki/log.md should be among the changes
```

Commit only when there are no **errors**. List any remaining **warnings** in the log entry.
