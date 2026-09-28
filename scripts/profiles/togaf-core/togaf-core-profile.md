# Profile: togaf-core 


## The purpose of this profile

Turn an organisation's technical documents — architecture descriptions, design documents, data dictionaries — into a wiki structured by the TOGAF 9.2 Content Metamodel's core objects. One document is ingested at a time. Every new note is written for human review before it counts as confirmed.

## The entities I care about

Use exactly these 23 note types (the TOGAF Core Content Metamodel) and no others. Do not add extension-module types (Driver, Goal, Event, Contract, …).

| Type | TOGAF definition | Use it when the document describes | Illustrative example (not from a real source) |
|---|---|---|---|
| actor | A person, organisation or system with a behavioural role | Who performs an action or holds a role | "Claims Officers review submitted claims" |
| assumption | A statement taken as true for architecture planning | A stated planning assumption | "Assumes the current CRM stays in place through 2027" |
| business-capability | A generic ability the business has, independent of how it's delivered | A named ability described at the level of "what", not "how" | "Claims Management" as a capability the business has |
| business-service | A defined interface exposing business value to consumers | A business-level service with an explicit interface | "Policy Quotation Service" offered to brokers |
| capability | An ability at any layer, more general than business-capability | An ability that isn't specifically business-level (could span layers) | "Digital Channel Delivery" as a cross-cutting capability |
| constraint | An external factor limiting the choice of approach | A stated limitation not chosen by the architecture | "Must run on existing mainframe until 2026" |
| course-of-action | An approach chosen to realise a capability or strategy | A named plan or strategic direction | "Migrate to cloud-native claims processing" |
| data-entity | A business object of data | A named thing the business tracks as data | "Customer", "Claim", "Policy" |
| function | A delivered capability closely aligned to the org, not governed by org structure | A described business function | "Underwriting" as a function performed |
| gap | A stated difference between a baseline and target state | An explicit "we don't have X yet" or "moving from A to B" | "No self-service claim lodgement today" |
| location | A place architecture is carried out or business is performed | A named site, region or facility | "Sydney Data Centre", "APAC region" |
| logical-application-component | Application functionality, independent of a specific product | A described application module in vendor-neutral terms | "Claims Processing Engine" as a logical module |
| logical-technology-component | Technology infrastructure, independent of a specific product | A described infrastructure layer in vendor-neutral terms | "Message Queue" as a logical component |
| organization-unit | A self-contained unit of resources with line management | A named business unit or team with a manager | "Claims Operations" as an org unit |
| physical-application-component | A specific, actual application or system | A named product or system instance | "Guidewire ClaimCenter v10" |
| physical-technology-component | A specific technology product or infrastructure instance | A named vendor product or piece of infrastructure | "AWS RDS PostgreSQL 15 instance" |
| principle | A general rule guiding how the org pursues its mission | A stated architecture or business principle | "Prefer buy over build" |
| process | A flow of activities achieving a defined outcome | A described sequence of steps with a result | "Claim Intake Process" |
| requirement | A statement of a need the architecture must meet | A stated "must" or "shall" requirement | "The system must support multi-currency claims" |
| role | A responsibility taken by an actor in a context | A named responsibility distinct from the person holding it | "Claims Approver" as a role, regardless of who holds it |
| technology-service | Technical functionality exposed through an interface | A described technical/infrastructure service | "Authentication Service" |
| value-stream | An end-to-end set of activities producing a result for a stakeholder | A described stakeholder-to-stakeholder flow of value | "New Business Onboarding" value stream |
| work-package | A set of actions to achieve one or more objectives | A named project, initiative or delivery package | "Claims Platform Modernisation Phase 1" |

Choosing between the easily-confused pairs (fix these once you have a real document; the definitions above are TOGAF's own, but where your documents actually draw the line may differ):
- **capability vs business-capability**: business-capability if the document frames it as a business ability; capability if it's described independent of any one layer (rare — most things will be business-capability).
- **function vs process vs value-stream**: function is a standing capability the org performs ("Underwriting"); process is a specific sequence of steps ("Claim Intake Process"); value-stream is the end-to-end, stakeholder-facing version ("New Business Onboarding").
- **logical vs physical (application/technology)**: logical if the document names a role or module without naming a vendor/product; physical if it names an actual product, version or instance.
- **data-entity vs logical-application-component**: data-entity is a thing the business tracks (a noun in the data dictionary); a component is something that processes or holds data, not the data itself.

Not needed: extension-module types, and anything only shown as a picture with no accompanying text (see "What this can't do yet" below).

## No representative sampling

**One example of a type is not the same as covering that type.** If the source names five specific sub-agents, five specific data stores, or five specific named systems, and they're all the same type, create five notes — not one, with the rest left as background detail inside other notes' prose.

This was an observed failure, not a hypothetical one: the first real ingest against this spec created one `physical-technology-component` note (for a named messaging product) and one `physical-application-component` note (for a named orchestration product), then treated both types as "represented" and stopped — even though the source went on to name several more distinct products of the same kind in later paragraphs. Those products were read, and even quoted inside other notes' prose, but never given their own note. The cause wasn't failing to notice them; it was stopping once a type had one example.

This risk is highest for the types that name specific things — actor, physical-application-component, physical-technology-component, technology-service, data-entity — because a document can plausibly name many distinct instances of each. It's lower for the types that describe something the whole document argues for once — business-capability, value-stream — where one or two notes may genuinely be all there is.

**Rule:** while reading, list every distinct named instance you notice for a type before writing any note of that type, the same way you'd list candidates for any other type. Do not let an early example stop you from continuing to read for more of the same kind. Nothing in this vault checks this mechanically today (see "What should block, and what should only warn") — it depends on doing this deliberately.

## What every note records

Every note, of every type, has one required field beyond the framework's defaults:

- `classification_basis` (string, required): one sentence, quoting or closely paraphrasing the source, saying why this became this type and not another. This is what a human reviews.

No other type-specific fields. No typed relationship fields (see below).

## How connections are made

No typed, directional associations (TOGAF's "Function delivers Business Capability" style bidirectional links are not modelled). Instead:

- Every note has a `## Related` section with plain wikilinks to the other notes it's connected to.
- A one- or two-word label before each link says the nature of the connection in plain language, e.g. `- delivers: [[Claims Management]]`, `- part of: [[Claims Operations]]`. This is prose, not a checked field — the tool doesn't verify it.
- Every note also cites the exact place in the source document it came from (heading, or page/paragraph if the document has no headings).

## What should block, and what should only warn

Block (error):
- A note missing `classification_basis`.
- A citation that doesn't point at an identifiable place in the source (see "What this can't do yet").

Warn only:
- A note that's been `status: seed` for more than one ingest session (a nudge to review it, not a hard stop — there's no reliable "how old is this" check today, so in practice this means: check the review queue every time).
- Nothing today checks "no representative sampling" (see above) mechanically — there's no rule that can tell whether every distinct named instance in a source got its own note. This is a known gap, not a decision that it doesn't matter.

## Review workflow

1. Every new note starts `status: seed`.
2. Before generating the review queue, re-read the source once specifically checking for "no representative sampling" (above): for each type you used, are there other distinct named instances in the source that didn't get a note? If so, write them now, before moving on.
3. After each document is ingested, generate a review queue: one table row per `seed` note, with its type, `classification_basis`, and source citation.
4. You read the queue. For each note: confirm it (bump `status` to `stable` if this is its only source, or `growing` if more sources are still expected), fix its type or fields, merge it into an existing note if it's a duplicate, or delete it.
5. Only move to the next document once the queue is clear, or you've consciously left something in `seed`.

## Views to generate

- One table per type would be 23 tables; instead, generate one combined catalogue table (type, title, status, classification_basis, sources) that can be filtered/sorted in Obsidian.
- The review queue described above (filtered to `status: seed`).

## What this can't do yet

- **Source format:** this spec assumes a document with real headings (Word, Markdown) so a citation can point at an exact place. Excel data dictionaries, PDFs, PowerPoint, Visio and diagrams are not covered here — each needs its own conversion step before it fits this citation model. Start with Word/Markdown documents only.
- **Cross-document deduplication:** the same Business Capability will appear in more than one document, worded differently. This spec doesn't yet say how to guarantee it lands in one note, not two. Needs deciding before ingesting a second document that overlaps the first.
- **Bulk/unattended ingest:** not in scope. One document at a time, reviewed before the next.

## Instructions for whoever builds this profile

- Do only what this page lists. Do not add note types, fields, checks or views that are not written here.
- Do not add typed relationship fields, even though the TOGAF metamodel defines them — this spec deliberately leaves associations as plain links.
- If something you need is not decided here, stop and ask. Do not guess.
- The examples in the type table are illustrative, not from a real document. Take real heading levels, terminology and phrasing from the first sample document you're given, and flag any type whose boundary doesn't match what the sample actually says.
- Follow "No representative sampling" above. When you finish, report the note count per type used, not just which types were used — a type used once and a type used five times both just show up as "used" unless you say the count.
- When you finish, report: the note types created, the checks and views created, and every place where you had to choose something not written here.
