---
tags:
  - "data-entity"
topics:
  - "[[Financial Services]]"
status: seed
created: 2026-09-28
updated: 2026-09-28
sources:
  - "[[2026-09-28-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases: []
classification_basis: "It is a named event data object carrying signals relevant to fraud and risk."
---

# Transaction Event

An event containing fraud or risk signals associated with a customer profile.

## Explanation
Inbound topics carry transaction events representing fraud/risk signals, which listeners correlate with profiles ([[2026-09-28-modernizing-kyc-aws-serverless#Event-Driven Communication Infrastructure with Amazon MSK|Event-Driven Communication Infrastructure with Amazon MSK]]).

## Related
- analyzed by: [[Fraud Detection Sub-Agent]]
