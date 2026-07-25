# 🔬 Sift

> **Web search, research synthesis, and fact verification — with source reliability scoring.**

## Why Sift?

Not all search results are equal. Sift is the system's general research engine, retrieving and synthesizing information from the web across a tiered source hierarchy. It evaluates reliability through cross-source agreement scoring, extracts structured entities, and emits enrichment candidates to Chronicle so researched knowledge accumulates over time.

Skill packages follow the [agentskills.io](https://agentskills.io/specification) open standard and are compatible with OpenClaw, Hermes Agent, Claude, and any agentskills.io-compliant client.

## Quick Start

```
# Quick search
"What's the current status of the SAFE Act?"

# Deep research
"Research the competitive landscape for AI-powered calendars"

# Fact check
"Is it true that OpenAI raised $6.6B in March 2025?"
```

Sift auto-initializes on first use.

## What It Does

Sift selects search depth automatically (quick answer, comparison, deep research, or document analysis), routes queries through a tiered source hierarchy from internal knowledge to semantic research providers, and evaluates reliability through cross-source agreement scoring. It never performs person-focused OSINT — those requests belong with Scout.

## Commands

| Command | Description |
|---|---|
| `sift.search` | Execute a search with automatic tier selection |
| `sift.research` | Multi-source research session producing a structured journal |
| `sift.verify` | Fact-check a claim with consensus scoring |
| `sift.summarize` | Summarize a document or URL |
| `sift.extract` | Extract entities, claims, and statistics |
| `sift.thread.list` | List active research threads |
| `sift.status` | Active threads, quota usage |
| `sift.journal` | Write journal |
| `sift.update` | Self-update |

## Dependencies

- See `references/integration-notes.md` for the current backend architecture.
- [Weave](https://github.com/<agent-handle>/weave) — entity disambiguation
- Brave Search API, SearXNG, DuckDuckGo, Exa, Tavily

## Scheduled Tasks

| Job | Schedule | Command |
|---|---|---|
| `sift:update` | `0 0 * * *` | Self-update |

## Changelog

### v2.8.5 — April 12, 2026
- Content-density check, search tier deduplication

### v2.5.0 — April 2, 2026
- Added `user_relevance` field on emitted signals

### v2.0.0 — March 18, 2026
- Initial release

---

*Sift is part of the [OCAS Agent Suite](https://github.com/<agent-handle>).*