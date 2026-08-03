# Kepler Agent v1 — Product Specification

## 1. Identity

**Kepler Agent** is a proprietary, fine-tuned research agent model. It is the core intellectual property of the Kepler ecosystem, deployed across Kepler Application (web) and Kepler Workspace (desktop).

**Positioning:** "More than Claude" — same base model class, superior fine-tuning for deep academic and intellectual research workflows.

---

## 2. Core Capabilities (v1)

| # | Capability | Description | Deployment |
|---|-----------|-------------|------------|
| 1 | **Web Browsing** | Navigate, read, extract, and synthesize information from web pages | Cloud + Local |
| 2 | **Bash Tool** | Execute shell commands in sandboxed environment | Cloud + Local |
| 3 | **Code Execution** | Run and create code (Python, etc.) in isolated runtime | Cloud + Local |
| 4 | **Git Operations** | Clone, read, diff, commit, push to repositories | Cloud + Local |
| 5 | **Knowledge Fetch** | Retrieve from curated Kepler knowledge base | Cloud + Local |
| 6 | **Image Fetch** | Retrieve and analyze images from web or user sources | Cloud + Local |
| 7 | **Article Fetch** | Extract and parse article content from URLs | Cloud + Local |
| 8 | **Sandbox Integration** | Execute in secured environment with domain whitelisting | Cloud (Render/Daytona) |

**v2 Capabilities (post-launch):** 3D simulation, motion simulator, graphing tools, vector scaling, OpenLibre integration, Google Earth, Playwright dev servers, interactive web panel.

---

## 3. Architecture

### 3.1 Model

- **Base:** Same model class as frontier models (Claude-class)
- **Fine-tuning:** Research workflow optimization, tool-use alignment, long-context retention, citation grounding
- **Context Window:** Extended for multi-step research sessions
- **Tool Use:** Native function calling for all capabilities

### 3.2 Deployment Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **API** | Hosted inference via Kepler servers | Application web users |
| **Hosted** | Dedicated endpoint with token | Enterprise / power users |
| **Local Proxy** | User runs local daemon, Kepler routes through infra | Privacy-sensitive, cost-conscious |

**Local Proxy Note:** User provides model brain. Kepler provides orchestration, sandbox, security. Platform costs apply; token costs reduced.

---

## 4. Integration Points

```
┌─────────────────────────────────────────┐
│           Kepler Agent (Model)          │
│         Proprietary, Fine-tuned         │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐   ┌───────────┐   ┌───────────┐
│ Kepler  │   │  Kepler   │   │  Future   │
│ App     │   │ Workspace │   │  API/CLI  │
│ (Web)   │   │ (Desktop) │   │           │
└─────────┘   └───────────┘   └───────────┘
```

- **Kepler Application:** Agent invoked remotely via API. Runs in Daytona (paid) or Render (free) sandbox.
- **Kepler Workspace:** Agent bundled locally. Works offline. Syncs when online.

---

## 5. Training Objectives

| Objective | Description |
|-----------|-------------|
| **Research Workflow** | Multi-step, iterative investigation with hypothesis refinement |
| **Tool Orchestration** | Seamless handoff between browse, bash, code, git |
| **Grounded Generation** | Every claim citeable to fetched source |
| **Long Session Memory** | Retain context across 100k+ token research sessions |
| **Error Recovery** | Self-correct when tools fail or return unexpected results |

---

## 6. Safety & Constraints

- **Sandboxed Execution:** All code/bash runs in isolated environment
- **Domain Whitelisting:** Free tier restricted to arxiv, github, etc. Others require user permission
- **Rate Limiting:** Tool call limits per conversation tier
- **Credit System:** Unified credit = API inference tokens + platform cost (merged display)

---

## 7. Success Metrics (v1 Launch)

- [ ] Benchmark exceeds Claude on research task suite
- [ ] Tool use accuracy > 95% for core 8 capabilities
- [ ] Session completion rate (full research task end-to-end)
- [ ] User retention at 7 days, 30 days

---

## 8. Roadmap

| Phase | Deliverable |
|-------|-------------|
| v1.0 | Core 8 capabilities, Application integration |
| v1.1 | Workspace integration, local proxy |
| v1.2 | Knowledge base expansion, .kepler content format |
| v2.0 | Simulation tools, graphing, 3D space |
