---
tags:
  - "physical-technology-component"
topics:
  - "[[Financial Services]]"
status: seed
created: 2026-09-28
updated: 2026-09-29
sources:
  - "[[2026-09-28-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases:
  - "Amazon MSK"
  - "MSK"
classification_basis: "It is a specific managed Kafka product named as the communication backbone."
---

# Amazon Managed Streaming for Apache Kafka (Amazon MSK)

A managed Kafka service providing the streaming backbone for real-time KYC event exchange.

## Explanation
Amazon MSK serves as the communication backbone enabling asynchronous, real-time message exchange between agentic components and enterprise systems ([[2026-09-28-modernizing-kyc-aws-serverless#Event-Driven Communication Infrastructure with Amazon MSK|Event-Driven Communication Infrastructure with Amazon MSK]]).

## Related
- implements: [[Event-Driven Communication Infrastructure]]
- ingests: [[KYC Request]]
- integrated via: [[AWS Lambda]]
