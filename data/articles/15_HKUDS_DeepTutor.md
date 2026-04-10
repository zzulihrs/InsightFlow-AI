# DeepTutor: Agent-Native Personalized Learning Assistant

**Source:** GitHub - HKUDS/DeepTutor  
**Date:** 2026-04-10  
**Original URL:** [https://github.com/HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor)

---

## Repository Overview

**Repository:** HKUDS/DeepTutor  
**Stars:** 15.7k | **Forks:** 2.1k  
**License:** Apache 2.0  
**Latest Release:** v1.0.1 (2026.4.10)

**Badges:**
- Python 3.11+
- Next.js 16
- Apache 2.0 License

---

## Project Description

DeepTutor is an open-source AI tutoring platform built on an agent-native architecture. The project represents a comprehensive ground-up architecture rewrite (approximately 200,000 lines of code) designed to create autonomous, persistent learning assistants that adapt to individual learners. It features TutorBot, flexible mode switching, and a unified workspace where conversation history and knowledge bases persist across modes.

---

## Core Features

### Five Interactive Modes

1. **Chat** — Tool-augmented conversation with RAG retrieval, web search, code execution, and deep reasoning capabilities
2. **Deep Solve** — Multi-agent problem-solving with plan, investigate, solve, and verify phases; source citation at each reasoning step
3. **Quiz Generation** — Assessment creation grounded in knowledge bases with validation
4. **Deep Research** — Topic decomposition with parallel research agents across RAG, web, and academic sources with comprehensive reporting
5. **Math Animator** — Visual mathematical concept animations powered by Manim

### Primary Features

- **Personal TutorBots** — Autonomous tutors powered by nanobot, living in dedicated workspaces with persistent memory, personality templates, evolving skill sets, and multi-channel presence
- **AI Co-Writer** — A Markdown editor with AI as a collaborative first-class participant, drawing from knowledge bases and web
- **Guided Learning** — Transforms materials into structured, multi-step visual learning journeys with interactive pages for each knowledge point
- **Knowledge Hub** — PDF, Markdown, and text file uploads for RAG-ready document collections and organized, color-coded notebook systems
- **Persistent Memory** — Adaptive learner profiles shared across all features and agents, evolving over time
- **Agent-Native CLI** — Command-line interface with JSON output for autonomous agent operation and rich rendering for terminal users

---

## Technical Stack

- **Backend:** Python 3.11+, FastAPI framework
- **Frontend:** Next.js 16, React 19
- **LLM Support:** 30+ provider integrations (OpenAI, Anthropic, DeepSeek, Gemini, Ollama, etc.)
- **Embedding:** Multi-provider support with configurable dimensions
- **Deployment:** Docker containers with multi-architecture support (amd64, arm64)
- **Built on:** nanobot, LlamaIndex, and ManimCat
- **Default Ports:** Backend 8001, Frontend 3782

---

## Installation Options

### Option A: Setup Tour (Recommended)

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
conda create -n deeptutor python=3.11 && conda activate deeptutor
python scripts/start_tour.py
```

This interactive script handles dependency installation, environment configuration, live provider testing, and guided setup.

### Option B: Manual Local Install

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
conda create -n deeptutor python=3.11 && conda activate deeptutor
pip install -e ".[server]"
cd web && npm install && cd ..
cp .env.example .env
```

**Required Environment Variables:**
```
LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-xxx
LLM_HOST=https://api.openai.com/v1
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_HOST=https://api.openai.com/v1
EMBEDDING_DIMENSION=3072
```

**Start Services:**
```bash
python -m deeptutor.api.run_server
cd web && npm run dev -- -p 3782
```

Access at `http://localhost:3782`

### Option C: Docker Deployment

```bash
cp .env.example .env
# Edit .env with required credentials
docker compose -f docker-compose.ghcr.yml up -d
```

Or build from source:
```bash
docker compose up -d
```

**Data Persistence Volumes:**
- `/app/data/user` → `./data/user` (settings, memory, sessions, logs)
- `/app/data/knowledge_bases` → `./data/knowledge_bases` (documents and indices)

### Option D: CLI Only

```bash
pip install -e ".[cli]"
deeptutor chat
deeptutor run chat "Explain Fourier transform"
deeptutor run deep_solve "Solve x^2 = 4"
deeptutor kb create my-kb --doc textbook.pdf
```

See `SKILL.md` for the complete command reference.

---

## Supported LLM Providers

| Provider | Binding | Default URL |
|----------|---------|-------------|
| OpenAI | `openai` | `https://api.openai.com/v1` |
| Anthropic | `anthropic` | `https://api.anthropic.com/v1` |
| Azure OpenAI | `azure_openai` | — |
| DeepSeek | `deepseek` | `https://api.deepseek.com` |
| Groq | `groq` | `https://api.groq.com/openai/v1` |
| Mistral | `mistral` | `https://api.mistral.ai/v1` |
| Moonshot (Kimi) | `moonshot` | `https://api.moonshot.ai/v1` |
| Ollama | `ollama` | `http://localhost:11434/v1` |
| Gemini | `gemini` | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| Custom | `custom` | — |

*And 19+ additional providers including Qwen, Ernie, GLM, vLLM, OpenVINO, and others.*

---

## Supported Embedding Providers

| Provider | Binding | Model Example |
|----------|---------|---------------|
| OpenAI | `openai` | `text-embedding-3-large` |
| DashScope | `dashscope` | `text-embedding-v3` |
| Ollama | `ollama` | `nomic-embed-text` |
| SiliconFlow | `siliconflow` | `BAAI/bge-m3` |
| vLLM | `vllm` | Any embedding model |

---

## Web Search Providers

| Provider | Env Key | Notes |
|----------|---------|-------|
| Brave | `BRAVE_API_KEY` | Recommended, free tier available |
| Tavily | `TAVILY_API_KEY` | — |
| Jina | `JINA_API_KEY` | — |
| SearXNG | — | Self-hosted, no API key |
| DuckDuckGo | — | No API key required |
| Perplexity | `PERPLEXITY_API_KEY` | Requires API key |

---

## Architecture Highlights

The system implements a two-layer plugin model:

- **Tools layer:** Discrete capabilities for execution
- **Capabilities layer:** Workflow orchestration and reasoning

This decoupling enables flexible composition across all five chat modes while maintaining unified context management.

**Service Ports:**

| Service | Default Port |
|---------|-------------|
| Backend | 8001 |
| Frontend | 3782 |

**Data Storage:** Local user and knowledge base directories with Docker volume mapping support.

---

## Agent Interface

The CLI is agent-native, enabling autonomous operation with JSON output for pipelines and rich rendering for terminal users. Hand the `SKILL.md` specification to any LLM with tool access for autonomous operation.

```bash
deeptutor chat                              # Interactive REPL
deeptutor run chat "Your question"          # Single query
deeptutor kb create my-kb --doc document.pdf # Knowledge base management
```

---

## Release History

**v1.0.1** (2026.4.10) — Chart.js/SVG rendering pipeline, quiz duplicate prevention, o4-mini support

**v1.0.0-beta.4** (2026.4.10) — Embedding progress tracking, HTTP 429 retry, cross-platform dependencies

**v1.0.0-beta.3** (2026.4.8) — Removed litellm, native OpenAI/Anthropic SDKs, Windows compatibility

**v1.0.0-beta.2** (2026.4.7) — Runtime cache invalidation, MinerU support, Python 3.11+ minimum

**v1.0.0-beta.1** (2026.4.4) — Agent-native architecture rewrite, TutorBot, CLI/SDK entry points

---

## Additional Resources

- Multi-language README versions: Chinese, Japanese, Spanish, French, Arabic, Russian, Hindi, Portuguese
- Full documentation available at `/docs` directory
- Agent documentation: `AGENTS.md`
- Skill specifications: `SKILL.md`
- Contribution guidelines: `CONTRIBUTING.md`

---

## Community and Support

- **Discord:** Community server available
- **WeChat:** Group support option
- **Feishu:** Group discussions
- **GitHub:** Issues, Discussions, and Pull Requests

Maintained by **HKUDS** (Data Intelligence Lab @ The University of Hong Kong).
