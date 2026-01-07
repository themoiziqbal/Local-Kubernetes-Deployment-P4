# ADR-0001: Architectural Pivot from Console-First to Web-First Deployment

> **Scope**: This ADR documents the fundamental architectural decision to pivot from the originally planned console-first CLI application to a web-first deployment model.

- **Status:** Accepted
- **Date:** 2025-12-21
- **Feature:** 001-multimodal-todo-chatbot
- **Context:** The original implementation plan (specs/001-multimodal-todo-chatbot/plan.md) specified a console-first architecture using OpenAI ChatKit for CLI interaction, OpenAI Agents SDK for agent orchestration, and MCP for inter-agent communication. However, during development, the team pivoted to a web-first approach using FastAPI and HTML/CSS/JavaScript deployed on Vercel. This decision was driven by: (1) greater user accessibility without requiring local installation, (2) simpler deployment and distribution model, (3) cross-platform compatibility by default, and (4) faster MVP delivery without complex agent framework setup.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Long-term architectural direction changed from CLI to web
     2) Alternatives: YES - Console CLI, hybrid approach, desktop app all considered
     3) Scope: YES - Cross-cutting change affecting all layers (UI, backend, deployment)
-->

## Decision

Adopt a **web-first architecture** for the AI-powered todo chatbot instead of the console-first approach:

**Implementation Stack:**
- **Frontend:** HTML5/CSS3/JavaScript (vanilla) with responsive design
- **Backend:** FastAPI (Python 3.11+) with RESTful API endpoints
- **AI Engine:** OpenAI API (GPT-3.5-turbo/GPT-4) for intent classification and conversational AI
- **Storage:** In-memory (MVP) → SQLite (planned) for task persistence
- **Deployment:** Vercel serverless functions (primary), Railway/Render (alternatives)
- **Communication:** RESTful HTTP/JSON instead of MCP protocol
- **Architecture:** Monolithic FastAPI application instead of agent-based microservices

**Key Architectural Changes:**
- Primary interface: Web browser (HTTP) instead of terminal (stdin/stdout)
- User interaction: Web forms and chat UI instead of ChatKit console
- AI integration: Direct OpenAI API calls instead of Agents SDK orchestration
- Component communication: Function calls instead of MCP tool invocation
- Deployment: Serverless cloud hosting instead of local executable distribution

## Consequences

### Positive

- **Universal accessibility:** Users can access the application from any device with a web browser without installation
- **Zero setup friction:** No local Python environment, dependencies, or CLI tool installation required
- **Cross-platform by default:** Works on Windows, macOS, Linux, mobile devices without platform-specific builds
- **Simpler deployment:** Single Vercel deployment command (`vercel deploy`) instead of packaging executables for multiple platforms
- **Easier updates:** Server-side updates propagate to all users instantly without client updates
- **Familiar UX:** Web interface patterns are more familiar to non-technical users than CLI commands
- **Faster MVP:** Skip complex agent framework setup, MCP protocol implementation, and ChatKit integration
- **Lower barrier to contribution:** More developers familiar with web development than CLI/agent frameworks
- **Built-in CORS/security:** Leverage browser security model and FastAPI middleware
- **Rich UI capabilities:** Can add visual task lists, colors, drag-and-drop without terminal limitations

### Negative

- **Increased complexity:** Now requires frontend (HTML/CSS/JS) + backend (FastAPI) instead of single Python CLI script
- **Internet dependency:** Requires network connection; cannot function fully offline (original plan had offline English text mode)
- **Stateless by default:** RESTful APIs are stateless; conversation context tracking requires session management (originally built into agent framework)
- **Lost agent modularity:** Monolithic FastAPI implementation loses the clean separation of concerns from agent-based architecture
- **MCP investment wasted:** Research and design work for MCP integration is not used in web implementation
- **Harder local development:** Developers need to run both frontend and backend instead of single Python script
- **Deployment dependency:** Reliant on third-party hosting (Vercel) instead of self-contained executable
- **Testing complexity:** Need to test REST API contracts, CORS, HTTP edge cases instead of just Python function calls
- **No agent reusability:** Cannot easily swap agents or build CLI/mobile interfaces sharing same agent layer

## Alternatives Considered

### Alternative A: Console-First CLI (Original Plan)

**Stack:** OpenAI ChatKit + Agents SDK + MCP + SQLite + packaged executable

**Pros:**
- Clean agent-based modularity with MCP protocol
- Works fully offline (English text mode fallback)
- No frontend complexity or HTTP concerns
- Single Python codebase, easier debugging
- Aligns with original constitution v1.0.0

**Cons:**
- Requires local installation and Python environment setup
- Barriers to non-technical users
- Complex agent framework learning curve
- Harder to distribute and update
- Platform-specific packaging needed

**Why rejected:** Accessibility concerns outweighed architectural elegance. Web-first reaches more users with zero installation friction.

### Alternative B: Hybrid Approach (Console + Web)

**Stack:** Shared agent layer (src/agents/) + dual frontends (console CLI + web UI)

**Pros:**
- Best of both worlds: accessible web UI + power-user CLI
- Agent layer can be reused across interfaces
- Flexible deployment (cloud or local)
- Preserves MCP investment

**Cons:**
- Doubles maintenance burden (two frontends to maintain)
- More complex architecture and testing
- Delayed MVP delivery (need to build both interfaces)
- Session/state management differs between CLI and web

**Why rejected:** Premature complexity for MVP. Can revisit if CLI demand emerges after web launch.

### Alternative C: Desktop Application (Electron)

**Stack:** Electron wrapper + React + local SQLite + auto-updates

**Pros:**
- Rich UI capabilities without browser limitations
- Local-first (offline capable)
- Native OS integration (system tray, notifications)
- Single codebase for Windows/macOS/Linux

**Cons:**
- Large bundle size (Electron runtime ~50MB+)
- Still requires download/installation
- More complex than web deployment
- Resource-heavy compared to web or CLI

**Why rejected:** Installation friction still exists, and bundle size is excessive for a simple todo app.

## References

- Feature Spec: [specs/001-multimodal-todo-chatbot/spec.md](../../specs/001-multimodal-todo-chatbot/spec.md)
- Implementation Plan: [specs/001-multimodal-todo-chatbot/plan.md](../../specs/001-multimodal-todo-chatbot/plan.md)
- Constitution v2.0.0: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (amended to reflect web-first principles)
- Related ADRs: None (first ADR)
- Analysis Report: [history/prompts/001-multimodal-todo-chatbot/0006-cross-artifact-consistency-analysis-report.misc.prompt.md](../prompts/001-multimodal-todo-chatbot/0006-cross-artifact-consistency-analysis-report.misc.prompt.md)
- Constitution Amendment: [history/prompts/constitution/0002-constitution-amendment-web-first-architecture.constitution.prompt.md](../prompts/constitution/0002-constitution-amendment-web-first-architecture.constitution.prompt.md)
