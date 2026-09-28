# Workflow Examples

These are worked examples of the four workflows, using this vault's own domain (TOGAF Content Metamodel notes compiled from architecture documents). The source and notes are illustrative; the file formats follow `Schema/frontmatter-schema.md`, and the note types follow `scripts/profiles/togaf-core/togaf-core-profile.md`.

---

## 1. Ingest a source (`llm-wiki-ingest`)

**Person:** "Ingest the KYC architecture blog post I just added."

**Step 1. Find the source.** Assume it's `Raw/Sources/2026-09-27-modernizing-kyc-aws-serverless.md`, with `Processed: false`.

**Step 2. Check the catalog first.**

```bash
python3 scripts/wiki_tool.py search-catalog --query "KYC"
python3 scripts/wiki_tool.py search-catalog --query "sub-agent"
```

Suppose this vault is empty (first ingest) — nothing found yet.

**Step 3. Read the source.** Read it in full. Note each claim worth keeping and exactly where it appears (the heading it's under), so you can cite that precise place.

**Step 4. Plan the changes and tell the person before writing.** Follow "No representative sampling" in the profile doc: the source names *five* specialised sub-agents doing distinct tasks, so that's five `actor` notes, not one representative example.

| Action | Note | Kind | Why |
|---|---|---|---|
| create | `Wiki/Domains/Financial Services Compliance.md` | domain | Grouping note; `topics_kind` needs one |
| create | `Wiki/Business Capabilities/Know Your Customer (KYC) Validation.md` | business-capability | The generic ability being described |
| create | `Wiki/Actors/KYC Orchestration Supervisor Agent.md` | actor | Coordinates the sub-agents |
| create | `Wiki/Actors/Identity Verification Sub-Agent.md` | actor | One of five distinct named sub-agents — not a representative sample |
| create | `Wiki/Actors/Document Analysis Sub-Agent.md` | actor | A second, separate sub-agent — same reason |
| create | `Wiki/Requirements/Sub-5-Minute KYC Processing Time.md` | requirement | Explicit stated performance target |

**Step 5. Write the notes** from `_templates/<kind>-note.md`. For example, `Wiki/Actors/Identity Verification Sub-Agent.md`:

```markdown
---
tags:
  - "actor"
topics:
  - "[[Financial Services Compliance]]"
status: seed
created: 2026-09-28
updated: 2026-09-28
sources:
  - "[[2026-09-27-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases: []
classification_basis: "One of the 'Five Specialized Sub-Agents' explicitly listed as performing a domain-specific task — actor, since it's named as the performer, and its task is separately captured as Identity Verification ([[2026-09-27-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]])."
---

# Identity Verification Sub-Agent

The AI sub-agent that performs identity verification: validating customer identities against watchlists and sanctions databases.

## Explanation

- Calls third-party verification APIs and uses natural language processing to handle name variations ([[2026-09-27-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]]).

## Related

- coordinated by: [[KYC Orchestration Supervisor Agent]]
```

Every note needs `classification_basis`: one sentence, grounded in the source, saying why this became this kind and not another.

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
python3 scripts/wiki_tool.py log --title "ingest | Modernizing KYC with AWS serverless solutions" \
  --details "Created 6 notes (domain, business-capability, 3 actor, requirement), all status: seed."
```

**Step 8. Point to the review queue.** Tell the person: `Wiki/Generated/Review Queue.md` lists every `seed` note with its `classification_basis`, for them to confirm, fix, merge or delete.

---

## 2. Answer a question (`llm-wiki-query`)

**Person:** "What triggers escalation to a human, and who reviews it?"

1. Search the catalog, not `Raw/`:
   ```bash
   python3 scripts/wiki_tool.py search-catalog --query "escalation"
   ```
2. Open the matching Wiki notes, e.g. `Real-Time KYC Validation Process.md` and `Compliance Specialist.md`. There's no separate `Escalation` note — this vault doesn't have a `gap`-style note for every procedural step, only for stated differences between a baseline and target state.
3. Open only the Raw sources those notes cite, to confirm the detail.
4. Answer, citing Wiki notes for navigation and Raw sources for evidence:

   > Escalation is confidence-based: the Supervisor Agent auto-approves above 95% confidence, requires extra verification between 75–95%, and escalates below 75% to a human reviewer with full context ([[2026-09-27-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]]). That reviewer is the Compliance Specialist role — the source doesn't name a specific person, only the responsibility.
   >
   > There's no dedicated note for the escalation mechanism itself; it's described inside the process note. If you want it broken out separately, that's an ingest change, not a query.

5. Don't write to `Wiki/` during a query unless the person asks. Point out gaps instead of guessing.

---

## 3. Lint (`llm-wiki-lint`)

**Person:** "Lint the wiki."

```bash
python3 scripts/wiki_tool.py lint
python3 scripts/wiki_tool.py source-lint
```

Example report:

```
ERROR S3  Wiki/Technology Services/AgentCore Identity.md: [[2026-09-27-modernizing-kyc-aws-serverless#Cloud-native KYC solution architecture|...]]: no such heading/block in source
WARN  L3  Wiki/Physical Technology Components/Amazon S3.md: orphan: no other Wiki note links here
WARN  F7  Wiki/Constraints/Multi-Jurisdiction Regulatory Compliance.md: summary is 217 characters (max 200)
```

What to do with each:

| Finding | Fix |
|---|---|
| S3 | Copy the heading text exactly from the source, including punctuation (a curly apostrophe is not the same character as a straight one). |
| L3 | Add a `## Related` link connecting it to another note that gives it context — every note should have at least one, in either direction. |
| F7 | Shorten the one-sentence summary that follows the `# Heading` to 200 characters or fewer. |

Report what you fixed and what needs a person to decide.

---

## 4. Maintain (`llm-wiki-maintain`)

**Person:** "A second document also created a `Supervisor Agent` actor note — looks like a duplicate of `KYC Orchestration Supervisor Agent`."

1. Compare both notes: their `sources`, `aliases`, `classification_basis` and inbound links (`links` in the catalog).
2. Choose the one to keep (`KYC Orchestration Supervisor Agent` — the fuller name, with more inbound links).
3. Move any uniquely cited content from `Supervisor Agent.md` into it, keeping each citation exactly.
4. Merge the `sources` lists, update `source_count`, merge `topics`, and add `Supervisor Agent` to `aliases` (it may already be there).
5. Update inbound links from `[[Supervisor Agent]]` to `[[KYC Orchestration Supervisor Agent]]`, then delete `Supervisor Agent.md`. Deleting a Wiki note is fine; Raw files are never deleted.
6. Set `updated`, run `build`, `lint` and `source-lint`, and log it:

```bash
python3 scripts/wiki_tool.py log --title "maintain | merge Supervisor Agent → KYC Orchestration Supervisor Agent" \
  --details "Moved 1 cited detail, merged 2 sources, added alias, relinked 3 notes."
```
