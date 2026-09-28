---
tags:
  - "logical-technology-component"
topics:
  - "[[Financial Services]]"
status: seed
created: 2026-09-28
updated: 2026-09-29
sources:
  - "[[2026-09-28-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases:
  - "Event-Driven Architecture Backbone"
  - "EDA Backbone"
classification_basis: "It is a technology infrastructure role described independent of a specific product, though later implemented with MSK."
---

# Event-Driven Communication Infrastructure

A vendor-neutral messaging backbone organizing inbound and outbound topics for asynchronous KYC processing.

## Explanation
The communication backbone enables asynchronous, real-time message exchange, organizing inbound and outbound topics for KYC flows ([[2026-09-28-modernizing-kyc-aws-serverless#Event-Driven Communication Infrastructure with Amazon MSK|Event-Driven Communication Infrastructure with Amazon MSK]]).

## Related
- implemented by: [[Amazon Managed Streaming for Apache Kafka (Amazon MSK)]]
- integrates: [[Event Listeners]]
- helps close: [[Legacy KYC Bottlenecks]]
- monitored by: [[Amazon CloudWatch]]
