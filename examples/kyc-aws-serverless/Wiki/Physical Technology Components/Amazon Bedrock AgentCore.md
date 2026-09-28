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
  - "AgentCore"
classification_basis: "It is a specific AWS agent runtime product named as the orchestration layer."
---

# Amazon Bedrock AgentCore

A managed agent runtime providing orchestration, state, memory, and tool integrations for KYC agents.

## Explanation
The architecture is built using Amazon Bedrock AgentCore, with runtime providing orchestration, session management, and memory persistence ([[2026-09-28-modernizing-kyc-aws-serverless#Cloud-native KYC solution architecture using agentic AI|Cloud-native KYC solution architecture using agentic AI]]).

## Related
- runs: [[KYC Orchestration Supervisor Agent]]
- runs: [[Identity Verification Sub-Agent]]
- invoked by: [[AWS Lambda]]
- includes: [[AgentCore Gateway]]
- includes: [[AgentCore Identity]]
- includes: [[AgentCore Memory]]
- includes: [[AgentCore Runtime Environment]]
- hosted on: [[Amazon Bedrock]]
