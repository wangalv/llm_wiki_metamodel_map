---
tags:
  - "logical-application-component"
topics:
  - "[[Financial Services]]"
status: seed
created: 2026-09-28
updated: 2026-09-29
sources:
  - "[[2026-09-28-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases:
  - "Identity Verification Agent"
classification_basis: "It is a named application module performing identity verification tasks."
---

# Identity Verification Sub-Agent

An application component that validates identities against watchlists and vendor checks using NLP for name variations.

## Explanation
This sub-agent validates identities against watchlists and sanctions, calls third-party verification APIs, and handles name variations with NLP ([[2026-09-28-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]]).

## Related
- coordinated by: [[KYC Orchestration Supervisor Agent]]
- consumes: [[Identity Document]]
- outputs: [[ID Verification Result]]
- uses: [[AgentCore Memory]]
