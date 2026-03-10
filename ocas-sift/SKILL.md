---
name: ocas-sift
description: >
  Web search, research synthesis, fact verification, and entity extraction.
  Separates signal from noise across the open web. Topic research engine
  for the OCAS ecosystem.
---

# Sift

Sift retrieves information from the web, evaluates reliability across multiple sources, extracts structured knowledge, and produces reliable answers or research artifacts.

## When to use

- Web search and research synthesis on any topic
- Fact verification across multiple sources with consensus scoring
- Document summarization and structured entity extraction
- Comparison research across products, technologies, or options
- Deep research sessions with multi-source threading

## When not to use

- OSINT investigations on individuals — use Scout
- Image-to-action processing — use Look
- Pattern analysis on the knowledge graph — use Corvus
- Communications and message drafting — use Dispatch
- Person-focused investigations — use Scout

Sift never performs OSINT investigations on individuals. If the primary entity of a query is a person, Scout should be invoked.

## Core promise

Sift converts vague questions into precise search queries, gathers sources, extracts structured information, evaluates consensus, and produces reliable answers. Fast for simple queries, thorough for deep research.

## Commands

- `sift.search` — execute a search query with automatic tier selection and query rewriting
- `sift.research` — run a multi-source research session producing a structured research journal
- `sift.verify` — fact-check a specific claim across multiple sources with consensus scoring
- `sift.summarize` — summarize a document or URL with structured entity extraction
- `sift.extract` — extract entities, claims, statistics, and relationships from content
- `sift.thread.list` — list active research threads with entity overlap detection
- `sift.status` — return current state: active threads, quota usage, source reputation summary

## Response modes

Sift classifies query depth automatically:

- **quick_answer** — simple factual lookups, single-source sufficient
- **comparison** — multi-source comparison with structured output
- **research** — deep multi-session investigation with threading
- **document_analysis** — URL or document-focused extraction

Users may override with phrases like "quick answer", "deep dive", "compare", or "summarize".

## Search tier selection

- **Tier 1 — Internal Knowledge**: LLM knowledge, conversation context, Chronicle if available. For fast answers.
- **Tier 2 — Free Web Search**: Brave Search API, SearXNG, DuckDuckGo. Standard research. Used by default.
- **Tier 3 — Semantic Research**: Exa, Tavily. Used only for deep research with sparse sources. Quota-limited.

Escalation: Tier 2 runs by default. Tier 3 only when deep research is needed and Tier 2 results are insufficient. Quota monitored via periodic heartbeat.

## Source reputation model

Sift maintains per-domain trust scores based on: cross-source agreement, contradiction frequency, historical accuracy, structured data quality, citation frequency.

Chronicle preferred sources (if available) influence ranking.

## Structured extraction rules

When pages are retrieved, extract: entities (with type from shared ontology), claims, statistics, relationships, citations. Each extraction includes confidence level.

Extracted entities are emitted as enrichment candidates for Elephas.

## Chronicle interaction

Sift never writes directly to Chronicle. It emits enrichment candidates. Elephas decides whether to store them.

Read `references/schemas.md` for candidate format.

## Support file map

- `references/schemas.md` — SearchQuery, SearchSession, ResearchThread, ExtractedEntity, SourceReputation, EnrichmentCandidate, DecisionRecord
- `references/search_tiers.md` — tier definitions, provider details, escalation criteria, quota monitoring
- `references/query_rewrite.md` — rewrite mechanics, examples, domain-scoped patterns, local search verticals

## Storage layout

```
.sift/
  config.json
  sessions.jsonl
  threads.jsonl
  entities.jsonl
  sources.jsonl
  decisions.jsonl
  reports/
```

## Validation rules

- Every extracted entity has a source reference and confidence level
- Tier 3 queries do not exceed configured daily quota
- Research sessions produce structured journal entries
- Source reputation scores are updated after each session
