---
license: MIT
name: ocas-sift
source: https://github.com/<agent-handle>/sift
description: 'Sift: web search, research synthesis, fact verification, entity extraction,
  and URL content extraction. The system''s general research engine. Use for ANY task
  requiring web information: search, research, look up, investigate, find out, check
  if, fact check, compare, summarize, what is, how to, product recommendations, price
  checks, current events, or reading a specific URL. TRIGGER ON: any question requiring
  current web data, any "investigate/find out/check/look into" request, any product/price/recommendation
  query. Do NOT use browser for search (CAPTCHA''d on VPS). For deep research, load
  this skill directly. NOT for: person-focused OSINT (use Scout), image processing (use Look), offline tasks, or general knowledge that does not require web lookup.'
triggers:
- web search
- research
- fact check
- URL content extraction

includes:
- references/**
- scripts/**
metadata:
  author: Indigo Karasu (indigokarasu)
  version: 2.9.4
  hermes:
    category: research
    tags:
    - web-search
    - research-synthesis
    - fact-verification
    - OCAS-core
---

# Sift

Sift is the system's general research engine, retrieving and synthesizing information from the web across a tiered source hierarchy — internal knowledge first, then free web search, then rate-limited semantic research providers for deep work. It evaluates source reliability through cross-source agreement scoring, extracts structured entities from retrieved content, and emits enrichment candidates to Chronicle so researched knowledge accumulates over time.

## Load-First Rule for Web-Adjacent Queries

**When the user asks about products, prices, reviews, how-to advice, or any information that requires current web data, load Sift FIRST before answering from domain knowledge.** This applies even if you think you already know the answer from training data.

**Why:** browser search is CAPTCHA-blocked from datacenter IPs; `web_search`/`web_extract` route via SearXNG instead. Answering from domain knowledge risks missing availability changes, new products, price moves, and critical caveats.

Pattern: load Sift → call `web_search` → fetch top results with `sift.fetch` → synthesize with citations. Exception: pure static lookups ("capital of France") need no web data.

## When to use

**Load Sift first, before any other action, when:** the question needs current web data; the user says "search / look up / research / investigate / find out / check if"; products, prices, reviews, or recommendations are involved; facts need verification against live sources; options need comparison; a specific URL needs fetching; or you're about to use the browser or a scraper for information-seeking.

Use cases: web search and synthesis, multi-source fact verification with consensus scoring, summarization with entity extraction, comparison research, deep threaded research sessions, current-events research.

## When not to use

- OSINT investigations on individuals — use Scout
- Image-to-action processing — use Look
- Pattern analysis on the knowledge graph — query Chronicle directly
- Communications and message drafting — use Dispatch

If the primary entity of a query is a person, invoke Scout instead — Sift never does person-focused OSINT.

## Ontology types

Sift extracts entities typed from `spec-ocas-ontology.md` (Entity/Person, Entity/AI, Place, Concept/Event, Concept/Idea, Thing/DigitalArtifact). Signal `payload.type` is the primary entity's ontology type; `source_journal_type` is `"Research"`.

### user_relevance field

Every Signal carries `user_relevance`: `"user"` or `"agent_only"`. Default `"agent_only"`; use `"user"` only when the user explicitly requested the research OR the entity connects to a `"user"` Chronicle entry. Full semantics + JSON example: `references/user-relevance.md`.

Sift may read Thread's active context for query rewriting and Weave's database for entity disambiguation (both cooperative read-only; see `spec-ocas-interfaces.md` Cooperative Query Interfaces).

## Commands

- `sift.search` — execute a search query with automatic tier selection and query rewriting
- `sift.research` — run a multi-source research session producing a structured research journal
- `sift.verify` — fact-check a specific claim across multiple sources with consensus scoring
- `sift.summarize` — summarize a document or URL with structured entity extraction
- `sift.extract` — extract entities, claims, statistics, and relationships from content
- `sift.thread.list` — list active research threads with entity overlap detection
- `sift.status` — return current state: active threads, quota usage, source reputation summary
- `sift.journal` — write journal for the current run; called at end of every run
- `sift.update` — pull latest from GitHub source; preserves journals and data
- `sift.fetch [url]` — extract clean Markdown from a specific URL (Scrapling → Jina Reader fallback; wayback recovery on confirmed hard-block). Specific URLs only, never general search. See `sift.fetch behavior` below.
- `sift.webwright` — interactive browser task via Playwright Firefox (forms, multi-step flows, JS-heavy sites); artifacts written to `{agent_root}/commons/data/ocas-sift/webwright/`. Read `references/webwright-integration.md` before first use. Pass `stealth: true` on anti-bot sites.

## Response modes

Sift classifies query depth automatically:

- **quick_answer** — simple factual lookups, single-source sufficient
- **comparison** — multi-source comparison with structured output
- **research** — deep multi-session investigation with threading
- **document_analysis** — URL or document-focused extraction

Users may override with phrases like "quick answer", "deep dive", "compare", or "summarize".

## Search tier selection

All search sources fire in parallel. Results are deduplicated by URL and content hash.

- **Internal knowledge** — LLM knowledge, conversation context, Chronicle if available. Always runs first as a pre-check.
- **Free web search** — SearXNG via `web_search` tool (self-hosted metasearch, 70+ engines, no key). This is the default first query for all research.
- **Platform search** — agent-reach on Twitter/X, Reddit, LinkedIn, GitHub, etc.

Structured API data routes through **Reach**: `reach.query <source> <action>` across 53 registered APIs (fred, census, sec_edgar, nasa, openalex, courtlistener…), CSAPI (`reach.csapi_check/increment`, quota owned by Reach), and RapidAPI (146+ general-marketplace APIs — not just local business search). Never call `mcp_rapidapi_rapidapi_call` or `mcp_google_workspace_search_custom` directly; all API access goes through Reach.

## Quick VPS search cheat sheet

Raw SearXNG curl one-liner and CSAPI quota commands: read `references/search-tiers-inline.md` (when scripting search outside the `web_search` tool).

## Source reputation model

Sift maintains per-domain trust scores based on: cross-source agreement, contradiction frequency, historical accuracy, structured data quality, citation frequency.

## Structured extraction rules

When pages are retrieved, extract: entities (with type from shared ontology), claims, statistics, relationships, citations. Each extraction includes confidence level.

Extracted entities are included as enrichment candidates in journal signal payloads for Chronicle ingestion.

## Run completion

After every Sift command that produces results:

- [ ] Persist session, entities, sources, and decisions to local JSONL files
- [ ] For each extracted entity or relationship with confidence >= `med`: write a Signal file to the `signal` payload field in the journal entry. Use Signal schema from `spec-ocas-shared-schemas.md`. Every Signal must include `user_relevance` (see Ontology types section). Set `"user"` if the run was user-initiated or the entity connects to a `user_relevance: "user"` Chronicle entry; otherwise `"agent_only"`.
- [ ] Write journal via `sift.journal`

## sift.fetch behavior

`sift.fetch [url]` extracts clean Markdown from a specific URL.

Do not use `sift.fetch` for general search — it fetches a specific known URL only.

## Browsing Escalation Chain

When fetching a URL or performing a web task, anti-bot protections (Cloudflare, Akamai, DataDome, Imperva, PerimeterX) may block the fast path. Escalate tier by tier — each tier only if the previous failed or returned insufficient content:

```
Tier 1: sift.fetch (Scrapling → Jina Reader)  →  Tier 2: sift.webwright (standard)
→ Tier 3: sift.webwright stealth=true  →  Tier 4: wayback_fallback.py (archive.org, is_stale=True)
→ no usable snapshot: mark unreachable, report to user with evidence.
```

**Why this order:** Scrapling is near-instant and covers ~90% of sites; webwright handles JS-heavy sites; stealth is the slow, expensive nuclear option; wayback is recovery-only and always marked stale.

Detection signals, the hard-block vs soft-failure decision table (never escalate on 429/5xx), and stealth-mode configuration: read `references/escalation-pattern.md` (when a fetch is blocked or auto-escalation triggers).

## Chronicle interaction

Sift never writes directly to Chronicle. It emits enrichment candidates via Signal files.

## Inter-skill interfaces

Sift writes Signal data via journal signal payload: the `signal` payload field in the journal entry.

## Error handling

| Failure | Symptom | Handling |
|---|---|---|
| SearXNG backend down | `web_search` empty `results` + `web_extract` errors | Stop retrying; go direct to primary sources (`references/primary_source_research.md`) |
| CAPTCHA on search engine | Challenge page from Google/Bing/DDG in browser | Never use browser for search; use `web_search` (SearXNG) or CSAPI via Reach |
| Anti-bot block on fetch | 403 / challenge HTML / tiny body | Escalate chain (see Browsing Escalation Chain) |
| Dead or hard-blocked URL | 404/410/451, auth wall | `scripts/wayback_fallback.py`; mark output `is_stale=True` |
| CSAPI key missing | Quota check fails | Sanitizer blocks key writes — owner must add key manually; use SearXNG meanwhile |
| Reach API quota exhausted | `reach.csapi_check` reports 0 | Fall back to free web search; do not call CSAPI directly |

## Pitfalls & Tips

Read `references/pitfalls.md` for the full list. Top traps:

- **Answer-from-knowledge trap** — don't answer product/how-to questions from training data; use `web_search` + `sift.fetch` (see Load-First Rule).
- **CAPTCHA cascade** — from cloud environments all major engines block headless browsers; use `web_search`/CSAPI.
- **Degraded search** — if `web_search` returns empty AND `web_extract` errors, go direct to primary sources (`references/primary_source_research.md`).
- **Self-calibration trap** — self-assess against what was delivered, not attempted.
- **Premise-staleness trap** — verify a capability still exists on the default branch before planning around it.

## Support file map

| File | When to read |
|---|---|
| `references/dye-transfer-fabric-guide.md` | When researching dye transfer, color run, or stain removal from clothes — fabric-specific product recommendations |
| `references/pitfalls.md` | Before research runs; CAPTCHA cascade, answer-from-knowledge trap, web_search plugin routing |
| `references/search_tiers.md` | Before tier selection or escalation |
| `references/research-workflow.md` | When executing research sessions from cloud environments |
| `references/ddg_html_fallback.md` | When `web_search` returns an empty `results` array (SearXNG degraded) — manual DuckDuckGo HTML + urllib discovery/read fallback |
| `references/primary_source_research.md` | When search engines (SearXNG/DDG/Bing) AND `web_extract` are all degraded — direct primary-source endpoints (SEC EDGAR API, Google News RSS, Jina Reader) that survive search-layer outages |
| `references/csapi-quota.md` | Before calling `search_custom` — quota tracking |
| `references/schemas.md` | Before creating sessions, threads, or extraction records |
| `references/query_rewrite.md` | Before query rewriting |
| `references/journal.md` | Before sift.journal; at end of every run |
| `references/webwright-integration.md` | Before `sift.webwright` — includes stealth mode configuration |
| `references/escalation-pattern.md` | When auto-escalation triggers or debugging anti-bot blocks |
| `references/wayback_fallback.md` | When `sift.fetch` hits a confirmed hard-block and may recover the dead URL from the Internet Archive |
| `references/user-relevance.md` | Before emitting any Signal — full `user_relevance` semantics + JSON example |
| `references/interfaces.md` | When wiring Sift's journal/signal interface to other OCAS skills |
| `references/research-pipeline.md` | When running a full multi-step research session end to end |
| `references/journal-example.md` | When writing a journal entry and unsure of the exact format |

Additional refs (read on demand): `fetch-behavior.md` (sift.fetch edge behavior), `search-tiers-inline.md` (curl cheat sheet), `exhaustive-research-methodology.md` (exhaustive coverage requests), `d3-graph-pitfalls.md` (D3 visualization), `x_discovery.md` (X/Twitter discovery), `searxng-plugin-setup.md` (SearXNG misconfiguration).

## Background tasks

| Job name | Mechanism | Schedule | Command |
|---|---|---|---|
| `sift:update` | cron | `0 0 * * *` (midnight daily) | `sift.update` |

## Self-update

`sift.update` pulls the latest package from GitHub. Runs silently.

## Visibility

public

## Skill cooperation

Cooperative read-only: Thread (browsing context for query rewriting), Weave (entity disambiguation), Chronicle (entity context). See `references/interfaces.md`.

