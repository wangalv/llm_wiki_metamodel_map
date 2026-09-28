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
  - "Supervisor Agent"
classification_basis: "It is a named application component that coordinates sub-agents and decision logic."
---

# KYC Orchestration Supervisor Agent

A coordinating application component that routes work and manages confidence-driven decisions across KYC sub-agents.

## Explanation
The supervisor implements intelligent routing in AgentCore, invoking sub-agents in parallel or sequence based on case characteristics and dependencies ([[2026-09-28-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]]).
It applies confidence thresholds to approve, request additional verification, or escalate to human review ([[2026-09-28-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]]).

## Related
- coordinates: [[Identity Verification Sub-Agent]]
- coordinates: [[Document Analysis Sub-Agent]]
- coordinates: [[Fraud Detection Sub-Agent]]
- coordinates: [[Compliance & Risk Sub-Agent]]
- coordinates: [[Customer Experience Sub-Agent]]
- runs in: [[AgentCore Runtime Environment]]
