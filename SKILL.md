---
name: ocas-sift
license: MIT
source: https://github.com/indigokarasu/sift
warning: 'FALSE TRIGGER RISK: high false-trigger rate on interactive loads — often pulled in for repo/push clarification or unrelated resource questions instead of structured research. Do NOT load for those; use clarification + ocas-reach instead.'
description: >-
  Sift: web search, research synthesis, fact verification, entity extraction, and
  URL content extraction — the system's general research engine. Use for any task
  requiring current web information: search, research, look up, investigate, find
  out, check if, fact check, compare, summarize, what is, how to, product
  recommendations, price checks, current events, or reading a specific URL.
  TRIGGER ON: any question needing current web data, or an "investigate/find
  out/check/look into" request. Do NOT use the browser for search (CAPTCHA'd on
  VPS); the `web_search`/`web_extract` MCP tools route to SearXNG automatically —
  load this skill directly for deep research. NOT for person-focused OSINT (use
  Scout) or image processing (use Look).
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
    - research
    - fact-verification
    - url-extraction
triggers:
- web search
- research synthesis
- fact verification
- extract URL content
- search the web
- investigate
- find out
- check if
- product research
- price check
- current events
- how to
- what is
---

# Sift

Sift is the system's general research engine: tiered web search, synthesis, fact
verification, structured entity extraction, and URL content extraction. It scores
source reliability by cross-source agreement and emits enrichment candidates to
Chronicle. **Support files:** `references/support-file-map.md` indexes the bundled
files not covered inline — check it before assuming a capability is missing.

## Load-First Rule

**Load Sift FIRST for anything requiring current web data** — products, prices,
reviews, how-to, news, or any "check / look up / find out" request — even when you
think you know the answer from training data.

**Why:** on VPS/cloud hosts, browser search (Google, Bing, DuckDuckGo) is
CAPTCHA-blocked from datacenter IPs. The `web_search` and `web_extract` MCP tools
cover basic searches via SearXNG; load this skill directly for deep research,
comparisons, fact-checking, and URL fetches. Answering from model memory misses
availability changes, price changes, new products, and caveats (e.g.
fabric-specific limits like synthetic vs. cotton).

**Exception:** pure trivia with no currency requirement ("capital of France") may
be answered from internal knowledge.

## When to Use

- Any question requiring current web data (not in training data)
- "search for", "look up", "research", "investigate", "find out", "check if", "look into"
- Products, prices, reviews, recommendations
- "what is / how to / why does / when did" about current topics; current events and news
- Verifying a fact or claim against current sources
- Comparing products, technologies, or options with current data
- Fetching or extracting content from a specific URL
- Any time you would otherwise drive the browser for search, or scrape a search engine

## When NOT to Use

- OSINT investigations on individuals — use Scout
- Image-to-action processing — use Look
- Knowledge-graph pattern analysis — use Corvus
- Communications and message drafting — use Dispatch

Sift never performs OSINT on individuals; if the primary entity of a query is a
person, Scout owns the task.

## Responsibility boundary

Sift owns web research, fact verification, and structured entity extraction. Sift
does not own: person-focused OSINT (Scout), image processing (Look), knowledge-graph
writes (Chronicle), pattern analysis (Corvus), social graph (Weave).

## Research workflow

Before reporting any research result, verify:
- [ ] A search path actually ran — nothing answered from training data alone
- [ ] Source-layer health checked (SearXNG reachable; CSAPI quota checked before use)
- [ ] Read past the name/title to the actual content (no surface-depth result)
- [ ] Cross-source agreement scored before claiming consensus
- [ ] Archived or cached content marked stale in the answer
- [ ] Signals emitted for entities with confidence ≥ `med`, each with `user_relevance`
- [ ] Journal written (`sift.journal`)

Run shape:

1. `sift.search` / `sift.research` — tier selection and query rewriting are automatic.
2. Fetch the leads worth reading: `sift.fetch`, escalating per `references/escalation-pattern.md` on blocks.
3. Synthesize with citations; run `sift.verify` when a claim is contested or high-stakes.
4. Close the run: persist JSONL, emit Signals, write the journal (see Run completion).

## Commands

- `sift.search` — search with automatic tier selection and query rewriting
- `sift.research` — multi-source research session producing a structured research journal
- `sift.verify` — fact-check a claim across multiple sources with consensus scoring
- `sift.summarize` — summarize a document or URL with structured entity extraction
- `sift.extract` — extract entities, claims, statistics, and relationships from content
- `sift.thread.list` — list active research threads with entity-overlap detection
- `sift.status` — current state: active threads, quota usage, source reputation summary
- `sift.journal` — write the journal for the current run; called at the end of every run
- `sift.fetch [url]` — clean Markdown from one URL: Scrapling first (fast HTTP for static sites, headless for JS-heavy), Jina Reader fallback when output is below the content threshold. Known-URL fetches only — never for general search.
- `donsetch fetch [url]` — anti-bot fetch via the locally installed `donsetch` (real Chrome TLS, solve-and-bounce) when `sift.fetch` returns a bot-wall, empty body, or Cloudflare challenge. Bridges to `donsetch search|crawl|mcp`. See `references/donsetch-integration.md`.
- `sift.webwright` — interactive browser task (Playwright driving system Chrome; requires the `playwright` package). Writes plan, screenshots, `final_script.py`, and execution log to `{agent_root}/commons/data/ocas-sift/webwright/`. Read `references/webwright-integration.md` before first use.

## Response modes

- **quick_answer** — simple factual lookup, single source sufficient
- **comparison** — multi-source comparison with structured output
- **research** — deep multi-session investigation with threading
- **document_analysis** — URL or document-focused extraction

Users may override with "quick answer", "deep dive", "compare", or "summarize".

## Search tier selection

All configured sources fire in parallel; results are deduplicated by URL and content hash.

- **Internal knowledge** — LLM knowledge, conversation context, Chronicle if available. Always runs first as a pre-check.
- **Free web search (parallel fan-out)** — N2 MCP (`n2_web_search`, SearXNG-backed, plus `n2_news_search`), Brave Search API, SearXNG (`localhost:8888` — the primary source on VPS), platform search (X/Reddit/LinkedIn/GitHub via agent-reach). Provider config and API keys: `references/search_tiers.md`.
- **CSAPI (Google Custom Search JSON API)** — fallback when free search is insufficient. Route through Reach (`reach.query csapi`); quota is owned by Reach (`reach.csapi_check` before, `reach.csapi_increment` after) — Sift does not manage CSAPI quota or MCP connections itself. Provider details: `references/csapi-quota.md`.

SearXNG can answer HTTP 200 while most engines are CAPTCHA'd or rate-limited, so one call is a narrow sample, not coverage. Before concluding a topic is unfindable, check which engines actually contributed (probe in `references/search_tiers.md`); a degraded engine layer means rephrasing will not help — go to primary sources (`references/primary_source_research.md`). Detailed tier-by-tier workflow and cloud fallbacks: `references/research-workflow.md`.

## Source reputation model

Per-domain trust scores from cross-source agreement, contradiction frequency, historical accuracy, structured-data quality, and citation frequency.

## Structured extraction rules

Extract entities (with shared-ontology types), claims, statistics, relationships, and citations — each with a confidence level. Entities with confidence ≥ `med` become Chronicle enrichment candidates.

## Run completion

After every Sift command that produces results:

1. Persist session, entities, sources, and decisions to local JSONL files.
2. For each extracted entity or relationship with confidence ≥ `med`, write a Signal file to the `signal` payload field in the journal entry (schema: pending `spec-ocas-shared-schemas.md`). Every Signal carries `user_relevance` — set `"user"` only if the run was user-initiated or the entity connects to an existing `user_relevance: "user"` Chronicle entry; otherwise `"agent_only"`.
3. Write the journal via `sift.journal`.

## Ontology types

Sift uses these types from the pending `spec-ocas-ontology.md`:

- **Entity/Person, Entity/AI** — people and agents identified during research
- **Place** — locations, venues, organizations
- **Concept/Event, Concept/Idea** — events, topics, themes
- **Thing/DigitalArtifact** — documents, articles, digital records

Signals go to Chronicle for entities and relationships with confidence ≥ `med`;
`payload.type` is the primary entity's ontology type; `source_journal_type` is
`"Research"`. Every Signal includes `user_relevance` — the full rules and a signal
example live in `references/user-relevance.md`.

## Error Handling

| Failure | Handling |
|---|---|
| SearXNG down (connection refused / empty) | Escalate to CSAPI via Reach, then RapidAPI (`reach.query rapidapi`); record `degraded: searxng` in the run record |
| `web_search` reports "SEARXNG_URL is not set" | Fix once: `hermes config set SEARXNG_URL http://localhost:8888` |
| Browser search CAPTCHA'd on every attempt | Stop using the browser; use SearXNG/CSAPI, then primary-source APIs (`references/research-workflow.md`) |
| `sift.fetch` returns bot-wall / 403 / empty | Escalate: `donsetch fetch` → `sift.webwright` (→ stealth) → Wayback (recovery-only, marked stale). See `references/escalation-pattern.md` |
| CSAPI quota exhausted | Skip CSAPI until it resets; record `degraded: csapi_quota`; continue with other sources |
| CSAPI fails on missing key or engine ID | Owner must add `GOOGLE_PSE_API_KEY` / engine ID manually — the sanitizer blocks agent writes |
| Wayback availability check errors (HTTP ≠ 200) | Snapshot presence is UNKNOWN, not absent — retry later; do not declare the URL unarchived |
| Journal or state write fails | Log to stderr, still return the results, and flag the run record |
| Page fetched but no extractable text | Report the failure with evidence — never fabricate a summary |

## Gotchas

Read `references/pitfalls.md` for the full list. Key highlights:

- **Answer-from-knowledge trap:** never answer product/how-to/recommendation questions from training data alone — that is exactly what the Load-First Rule forbids.
- **CAPTCHA cascade:** from cloud IPs most engines block automated browsers, but not uniformly — Google serves an "unusual traffic" page to the system Chrome while Bing may answer normally. Prefer SearXNG/CSAPI, and check pages for CAPTCHA markers before declaring a subject unfindable.
- **Surface-depth trap:** getting a name or title is step 1, not the deliverable — if you cannot say what the content says, the research is unfinished.
- **Credential sanitizer:** the Hermes output sanitizer intercepts API keys; the owner must add CSAPI keys manually.

## Support file map

| File | When to read |
|---|---|
| `references/pitfalls.md` | Before research runs — full pitfall list |
| `references/search_tiers.md` | Before tier selection; SearXNG engine-health probe, provider keys |
| `references/research-workflow.md` | When executing research sessions from cloud environments |
| `references/escalation-pattern.md` | When a fetch hits a bot-wall or challenge page |
| `references/csapi-quota.md` | Before touching CSAPI quota or key setup |
| `references/schemas.md` | Before creating sessions, threads, or extraction records |
| `references/query_rewrite.md` | Before query rewriting |
| `references/journal.md` | Before `sift.journal`; at the end of every run |
| `references/mcp-redirect-pattern.md` | When tracing how `web_search`/`web_extract` route to SearXNG |
| `references/webwright-integration.md` | Before `sift.webwright` |
| `references/donsetch-integration.md` | Before escalating past `sift.fetch` to donsetch |
| `references/local-business-search.md` | When searching for local businesses, services, or venues |
| `references/dye-transfer-fabric-guide.md` | When researching dye transfer, color run, or stain removal from clothes |

## Background tasks

None registered — Sift runs on demand. Skill updates are fleet-wide (see Updates),
so there is no per-skill update job.

## Updates

Updates are centralized: the `skills:update-fleet` cron runs a shared fleet
updater that pulls the latest from `source:` and never discards uncommitted
local work. There is no per-skill update script, and updates never touch
`{agent_root}/commons/` data or journals.

## Visibility

public

## Optional skill cooperation

- Chronicle — Sift emits Signal files for promotion; it never writes the graph itself
- Thread — may read recent browsing context for query rewriting
- Weave — may read for entity disambiguation
- Look — reverse image search capability
