
---
id: 0001
title: Define AI Todo Chatbot Constitution
stage: constitution
date: 2025-12-13
surface: agent
model: claude-sonnet-4.5
feature: none
branch: master
user: ThinkPad
command: /sp.constitution

labels:
  - constitution
  - agent-architecture
  - openai-stack
  - multimodal
  - multilingual

links:
  spec: null
  ticket: null
  adr: null
  pr: null

files:
  - .specify/memory/constitution.md

tests:
  - none
---


/sp.constitution

You are an expert AI software architect and product engineer.

Your task is to define the constitutional foundation for an **AI‑powered, console‑based Todo application** with a **multimodal and multilingual AI chatbot**.

---

## Core Vision

Build a conversational AI Todo system that allows users to manage their tasks (**Create, Read, Update, Patch, Delete**) using:

* Natural‑language text input
* Natural‑language voice input
* Any spoken or written language (automatic detection and translation)

---

## Non‑Negotiable Requirements

1. Use **OpenAI ChatKit** for the conversational interface
2. Use the **OpenAI Agents SDK** for agent orchestration
3. Use the **Official MCP SDK** for tool and resource communication
4. Operate in a **console‑based (CLI)** environment
5. Support **multilingual input and output** (text and voice)
6. Support **speech‑to‑text (STT)** and **text‑to‑speech (TTS)**
7. Todo management must be **fully AI‑driven via intent understanding**

---

## Intelligence Design

Create reusable AI intelligence units:

* Core Todo Agent
* Language Detection & Translation Agent
* Voice Processing Agent
* Intent Classification Agent
* Task Operation Sub‑Agents:

  * Add
  * Update
  * Patch
  * Delete
  * Read

All agents must be **reusable, composable, and skill‑based**.

---

## Behavior Rules

* The chatbot must always respond politely and clearly
* If the user speaks, automatically convert **voice → text**
* If the user types, process input directly
* Detect the user’s language automatically
* Translate internally to the system language (English)
* Execute the requested task operation
* Respond in the user’s original language
* Optionally respond using voice output

---

## Architecture Principles

* Agent‑first design
* Tool calling via MCP
* Clean separation of concerns
* Extensible for future UIs (Web / Mobile)
* Console‑first, but API‑ready

---

## Error Handling

* Gracefully handle unclear or ambiguous intent
* Ask follow‑up questions when required task information is missing
* Never crash the application

---

You must strictly follow this constitution when generating future specifications and plans.

---

## Response Snapshot

A comprehensive project constitution (**v1.0.0**) was created, defining **nine core principles**:

1. Agent‑First Architecture (**Non‑Negotiable**)
2. OpenAI Technology Stack (**Non‑Negotiable**)
3. Console‑First, API‑Ready Design
4. Multimodal & Multilingual Intelligence (**Non‑Negotiable**)
5. Intent‑Driven Todo Management (**Non‑Negotiable**)
6. MCP‑Based Tool and Resource Communication
7. Polite, Clear, and Helpful Behavior
8. Graceful Error Handling
9. Test‑Driven Agent Development

Additional sections include:

* **Technology Stack Requirements** (Python 3.11+, OpenAI Agents SDK, ChatKit, MCP SDK, STT/TTS, pytest)
* **Development Workflow** (agent lifecycle, code review, complexity management, deployment strategy)
* **Governance** (amendment process, versioning policy, compliance reviews, violation justification)

All placeholders were resolved. The constitution was written to `.specify/memory/constitution.md` with a **Sync Impact Report** prepended.

---

## Outcome

* ✅ **Impact**: Constitution ratified; establishes the architectural foundation for the AI‑powered Todo chatbot
* 🧪 **Tests**: Not required (documentation only)
* 📁 **Files**: `.specify/memory/constitution.md` created/updated
* 🔁 **Next Prompt**: `/sp.specify <feature-description>` to define the first feature specification
* 🧠 **Reflection**: The constitution provides strong architectural guardrails, ensuring OpenAI stack consistency and an agent‑first design

---

## Evaluation Notes (Flywheel)

* Failure modes observed: None
* Graders run and results: N/A (constitution establishment)
* Prompt variant: N/A
* Next experiment: Validate constitution compliance during the first feature specification
