---
tags:
  - "role"
topics:
  - "[[Financial Services]]"
status: seed
created: 2026-09-28
updated: 2026-09-28
sources:
  - "[[2026-09-28-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases:
  - "Manual Reviewer"
classification_basis: "The workflow explicitly routes complex or low-confidence cases to human reviewers."
---

# Human Reviewer

A role that adjudicates low-confidence or complex KYC cases escalated from automated processing.

## Explanation
Low-confidence cases are escalated to human review with comprehensive context from the supervisor agent ([[2026-09-28-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]]).
Complex cases are routed to human reviewers via case management events ([[2026-09-28-modernizing-kyc-aws-serverless#Event-Driven Communication Infrastructure with Amazon MSK|Event-Driven Communication Infrastructure with Amazon MSK]]).

## Related
- receives: [[Case Management System]]
- assesses: [[KYC Decision]]
