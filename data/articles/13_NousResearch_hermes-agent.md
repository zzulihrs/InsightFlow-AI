# Hermes Agent

## Metadata
- **Source**: NousResearch / GitHub
- **Date**: 2026-04-10
- **Original URL**: https://github.com/NousResearch/hermes-agent

---

## Project Description

**Hermes Agent** is a self-improving AI agent developed by Nous Research. It represents an autonomous system with built-in learning capabilities that evolves through experience rather than static deployment.

**Tagline**: "The agent that grows with you" — emphasizing continuous adaptation and skill development across sessions.

---

## Key Distinguishing Features

### Learning Architecture

The system implements a closed-loop learning mechanism featuring:

- Autonomous skill creation triggered by complex task completion
- Skills that self-improve during operational use
- Agent-curated memory with periodic reinforcement nudges
- Full-text-search session recall with LLM-powered summarization across conversation history
- Dialectic user modeling compatible with the Honcho framework
- Open standard skill compatibility through agentskills.io

### Multi-Platform Accessibility

- Terminal UI with full-featured text interface (multiline editing, streaming output, command autocomplete)
- Messaging integration: Telegram, Discord, Slack, WhatsApp, Signal, Email
- Voice transcription for audio memos
- Cross-platform conversation continuity

### Flexible Infrastructure

Deployable across six distinct terminal backends:

- Local execution
- Docker containerization
- SSH remote execution
- Daytona serverless environment
- Singularity containers
- Modal serverless platform

Modal and Daytona specifically enable hibernating environments that consume near-zero cost when idle.

### Model Agnostic

Supports any LLM provider without lock-in:

- Nous Portal
- OpenRouter (200+ models)
- Zhipu GLM
- Kimi/Moonshot
- MiniMax
- OpenAI
- Custom endpoints

Model switching via `hermes model` requires zero code modification.

### Operational Capabilities

- **Scheduling**: Built-in cron for automated tasks with multi-platform delivery
- **Delegation**: Spawns isolated subagents for parallel task execution
- **Tool Access**: 40+ integrated tools with extensible toolset system
- **Research Support**: Batch trajectory generation, RL environment integration (Atropos), trajectory compression for model training

---

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

Platform support: Linux, macOS, WSL2, Android/Termux. Windows requires WSL2.

Post-installation activation:

```bash
source ~/.bashrc  # or ~/.zshrc
hermes            # Launch interactive session
```

---

## Essential Commands

### Interactive Usage

- `hermes` — Start conversational interface
- `hermes model` — Switch LLM provider/model
- `hermes tools` — Enable/disable capabilities
- `hermes config set` — Modify individual settings
- `hermes gateway` — Activate messaging platform integration
- `hermes setup` — Comprehensive configuration wizard
- `hermes claw migrate` — Import OpenClaw configurations
- `hermes update` — Version upgrade
- `hermes doctor` — Troubleshoot installation issues

### In-Conversation Commands (both CLI and messaging)

- `/new`, `/reset` — Fresh conversation initiation
- `/model [provider:model]` — Runtime model switching
- `/personality [name]` — Persona assignment
- `/retry`, `/undo` — Revert last action
- `/compress`, `/usage`, `/insights` — Context analysis
- `/skills`, `/<skill-name>` — Skill exploration
- `/stop` (messaging) or `Ctrl+C` (CLI) — Interrupt execution

---

## OpenClaw Migration

Automated legacy system transition preserves:

- Persona configurations (SOUL.md)
- Memory entries (MEMORY.md, USER.md)
- Custom skills (relocates to ~/.hermes/skills/openclaw-imports/)
- Command approval patterns
- Messaging platform configurations
- API credentials (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- Text-to-speech assets
- Workspace instructions (AGENTS.md)

Migration initiated during `hermes setup` or manually via:

```bash
hermes claw migrate [--dry-run|--preset user-data|--overwrite]
```

---

## Development Setup

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv venv --python 3.11
source venv/bin/activate
uv pip install -e ".[all,dev]"
python -m pytest tests/ -q
```

Optional RL training integration:

```bash
git submodule update --init tinker-atropos
uv pip install -e "./tinker-atropos"
```

---

## Project Statistics

- **Repository Size**: 3,733 commits
- **Community**: 50.9k stars, 6.6k forks, 366 contributors
- **Code Composition**: 93.9% Python, supporting infrastructure in TeX, Shell, Nix, JavaScript

---

## Community & Resources

- **Documentation**: hermes-agent.nousresearch.com/docs
- **Discord Community**: discord.gg/NousResearch
- **Skills Marketplace**: agentskills.io
- **Issue Tracking & Discussions**: GitHub
- **License**: MIT
