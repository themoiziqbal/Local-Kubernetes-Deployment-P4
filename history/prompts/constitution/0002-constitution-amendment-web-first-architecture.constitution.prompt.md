---
id: 0002
title: Constitution Amendment Web-First Architecture
stage: constitution
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: ThinK Pad
command: /sp.constitution
labels: ["constitution", "amendment", "web-first", "architecture", "major-version"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (constitution amendment, no tests)
---

## Prompt

Update constitution to reflect web-first architecture with FastAPI deployment

## Response snapshot

**Constitution v2.0.0 Successfully Created**

**Version Change**: 1.0.0 → 2.0.0 (MAJOR - backward-incompatible architectural pivot)

**Key Amendments**:
1. **Principle I**: "Agent-First Architecture" → "Modular Architecture" (relaxed MCP requirement, allows flexible patterns)
2. **Principle II**: "OpenAI Technology Stack" → "AI-Powered Web Stack" (FastAPI + OpenAI API instead of ChatKit/Agents SDK)
3. **Principle III**: "Console-First, API-Ready" → "Web-First, API-Ready" (primary interface changed from CLI to web)
4. **Principle IV**: "Multimodal & Multilingual Intelligence" → Preserved goals, added phased implementation approach (P0: text, P1: translation, P2: voice)
5. **Principle V**: "Intent-Driven Todo Management" → Preserved, relaxed agent requirements (allows keyword matching + GPT fallback)
6. **Principle VI**: "MCP-Based Tool & Resource Communication" → "RESTful API Communication" (MCP optional for advanced use cases)
7. **Principle IX**: "Test-Driven Agent Development" → "Test-Driven Development (Phased)" (tests optional for MVP, required for production)

**Technology Stack Updates**:
- Added: FastAPI, HTML/CSS/JavaScript, RESTful APIs, serverless deployment (Vercel, Railway)
- Removed mandates: OpenAI ChatKit, OpenAI Agents SDK, strict MCP SDK requirement
- Made optional: MCP SDK, agent-based architecture, console CLI

**Deployment Strategy Updates**:
- Primary: Serverless deployment (Vercel, Railway, Render, AWS Lambda)
- Alternative: Traditional hosting (VPS, Docker)
- Local: .env files, hot-reload development

**Template Compatibility**: All dependent templates (.specify/templates/plan-template.md, spec-template.md, tasks-template.md) are already flexible enough to support web-first architecture - no updates required.

**Sync Impact Report**: Prepended to constitution.md documenting all changes, modified principles, added/removed sections, and follow-up TODOs.

## Outcome

- ✅ Impact: Constitution aligned with web-first reality; resolves 6 critical constitutional violations from analysis report
- 🧪 Tests: N/A (constitution document, no tests applicable)
- 📁 Files: 1 file updated (.specify/memory/constitution.md v1.0.0 → v2.0.0)
- 🔁 Next prompts: "/sp.adr 'Architectural Pivot from Console to Web' to document decision, then update plan.md/spec.md/tasks.md to align with new constitution"
- 🧠 Reflection: Constitutional amendment successfully captures the architectural pivot from console-first agent-based system to web-first FastAPI deployment. This resolves the core misalignment identified in the analysis report and provides a solid foundation for future development.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution successfully amended with comprehensive sync impact report
- Graders run and results (PASS/FAIL): N/A (constitution update)
- Prompt variant (if applicable): Standard /sp.constitution execution with user directive to adopt web-first architecture
- Next experiment (smallest change to try): Update feature-specific artifacts (plan.md, spec.md, tasks.md) to align with new constitution v2.0.0, then implement missing critical features (persistence, delete confirmation, translation)
