---
tags:
  - "process"
topics:
  - "[[Financial Services]]"
status: seed
created: 2026-09-28
updated: 2026-09-29
sources:
  - "[[2026-09-28-modernizing-kyc-aws-serverless]]"
source_count: 1
aliases:
  - "Real-Time KYC Validation"
  - "KYC Orchestration"
classification_basis: "The document describes a workflow that validates identity information in real time via an event-driven pipeline orchestrating specialized agents."
---

# KYC Validation Process

A process to validate customer identity and risk with AI-driven, event-based orchestration targeting sub‑5‑minute decisions.

## Explanation
The architecture processes live onboarding requests and validates identity using an event-driven pipeline targeting sub-5-minute throughput ([[2026-09-28-modernizing-kyc-aws-serverless#Cloud-native KYC solution architecture using agentic AI|Cloud-native KYC solution architecture using agentic AI]]).
It decomposes workflows into functions like identity verification, document analysis, fraud detection, and compliance checks coordinated by a supervisor agent ([[2026-09-28-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]]).

## Activities
- Receive onboarding requests and documents via inbound topics ([[2026-09-28-modernizing-kyc-aws-serverless#Event-Driven Communication Infrastructure with Amazon MSK|Event-Driven Communication Infrastructure with Amazon MSK]]).
- Perform identity, document, fraud, and compliance evaluations with specialized sub-agents ([[2026-09-28-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]]).
- Issue decisions with confidence scores and audit trails to downstream systems ([[2026-09-28-modernizing-kyc-aws-serverless#Event-Driven Communication Infrastructure with Amazon MSK|Event-Driven Communication Infrastructure with Amazon MSK]]).

## Related
- delivers: [[Know Your Customer (KYC)]]
- enabled by: [[Event-Driven Communication Infrastructure]]
- orchestrated by: [[KYC Orchestration Supervisor Agent]]
- performed by: [[Financial Institutions]]
- addresses: [[Legacy KYC Bottlenecks]]
- reviewed by: [[Compliance Specialist]]
