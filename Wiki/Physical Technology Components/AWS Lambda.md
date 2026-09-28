---
tags:
  - "physical-technology-component"
topics:
  - "[[Financial Services]]"
status: seed
created: 2026-09-28
updated: 2026-09-28
sources:
  - "[[2026-09-28-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases:
  - "Lambda"
classification_basis: "It is a specific AWS compute product used for event-driven integration and scaling."
---

# AWS Lambda

A serverless compute service used to integrate MSK with AgentCore and publish results asynchronously.

## Explanation
AWS Lambda provides serverless computing that scales on demand and supports instant onboarding in this KYC architecture ([[2026-09-28-modernizing-kyc-aws-serverless#Content|Content]]).
Lambda consumers trigger AgentCore asynchronously and publish results back to Kafka topics ([[2026-09-28-modernizing-kyc-aws-serverless#Cloud-native KYC solution architecture using agentic AI|Cloud-native KYC solution architecture using agentic AI]]).

## Related
- integrates: [[Amazon Managed Streaming for Apache Kafka (Amazon MSK)]]
- invokes: [[Amazon Bedrock AgentCore]]
