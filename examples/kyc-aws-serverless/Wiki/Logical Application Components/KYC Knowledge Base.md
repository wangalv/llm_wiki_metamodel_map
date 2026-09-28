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
  - "KYC KB"
classification_basis: "It is a named application component providing knowledge retrieval to agents."
---

# KYC Knowledge Base

A retrieval-augmented repository integrating regulations, policies, and vendor docs to ground agent decisions.

## Explanation
The KYC Knowledge Base implements RAG, storing regulations, internal rules, and vendor docs, and serving context for agents via semantic retrieval ([[2026-09-28-modernizing-kyc-aws-serverless#Intelligent Knowledge Management Architecture|Intelligent Knowledge Management Architecture]]).

## Related
- powers: [[Compliance & Risk Sub-Agent]]
- supports: [[KYC Validation Process]]
- secured by: [[AgentCore Identity]]
- powered by: [[Amazon OpenSearch Serverless]]
- stores documents in: [[Amazon Simple Storage Service (Amazon S3)]]
