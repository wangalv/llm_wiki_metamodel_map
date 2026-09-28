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
  - "Document Analysis Agent"
  - "OCR Agent"
classification_basis: "It is a named application module focused on OCR and document authenticity checks."
---

# Document Analysis Sub-Agent

An application component that extracts data via OCR, handles poor images and languages, and detects document forgery.

## Explanation
This sub-agent performs OCR on identity documents, handles poor image quality and multiple languages, and detects forgery features ([[2026-09-28-modernizing-kyc-aws-serverless#Agentic AI Orchestration Layer|Agentic AI Orchestration Layer]]).

## Related
- coordinated by: [[KYC Orchestration Supervisor Agent]]
- inputs: [[Identity Document]]
- powered by: [[Amazon Bedrock]]
