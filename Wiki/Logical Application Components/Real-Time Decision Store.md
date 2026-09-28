---
tags:
  - "logical-application-component"
topics:
  - "[[Financial Services]]"
status: seed
created: 2026-09-28
updated: 2026-09-28
sources:
  - "[[2026-09-28-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases: []
classification_basis: "It is a named application component dedicated to decision data used during KYC."
---

# Real-Time Decision Store

A low-latency store for current KYC status, risk scores, histories, and dynamic configuration.

## Explanation
The Real-Time Decision Store provides sub-millisecond access to KYC status, risk scores, interaction history, and dynamic parameters ([[2026-09-28-modernizing-kyc-aws-serverless#Intelligent Knowledge Management Architecture|Intelligent Knowledge Management Architecture]]).

## Related
- supports: [[KYC Validation Process]]
- implemented on: [[Amazon DynamoDB]]
