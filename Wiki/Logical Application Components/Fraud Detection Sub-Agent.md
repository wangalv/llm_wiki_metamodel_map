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
  - "Fraud Detection Agent"
classification_basis: "It is a named application module for behavioral fraud analysis and risk scoring."
---

# Fraud Detection Sub-Agent

An application component that detects suspicious behavior, correlates with history, and maintains explainable risk scores.

## Explanation
This sub-agent identifies suspicious patterns (e.g., repeated IP usage, inconsistencies), correlates with historical cases, and maintains dynamic, explainable risk scores ([[2026-09-28-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]]).

## Related
- coordinated by: [[KYC Orchestration Supervisor Agent]]
- outputs: [[Fraud Alert]]
- updates: [[Risk Score]]
- analyzes: [[Transaction Event]]
