---
tags:
  - "data-entity"
topics:
  - "[[Financial Services]]"
status: seed
created: 2026-09-28
updated: 2026-09-29
sources:
  - "[[2026-09-28-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases:
  - "KYC Outcome"
classification_basis: "It is a named decision artifact published to enterprise systems."
---

# KYC Decision

An outbound decision record including approval state, confidence, and supporting audit context.

## Explanation
Outbound topics publish KYC decisions with confidence scores and audit trails to downstream systems ([[2026-09-28-modernizing-kyc-aws-serverless#Event-Driven Communication Infrastructure with Amazon MSK|Event-Driven Communication Infrastructure with Amazon MSK]]).

## Related
- consumed by: [[Customer Management System]]
- triggers: [[Core Banking System]]
- evidenced by: [[Audit Trail]]
- accompanied by: [[Confidence Score]]
