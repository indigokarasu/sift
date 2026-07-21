---
license: MIT
name: ocas-sift
source: https://github.com/indigokarasu/sift
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

**Why this matters:** On VPS/cloud environments, browser-based search (Google, Bing, DuckDuckGo) is almost entirely blocked by CAPTCHA from datacenter IPs. The `web_search` and `web_extract` MCP tools handle basic searches automatically via SearXNG. Load this skill directly for deep research, fact-checking, comparisons, or when the MCP tools' results are insufficient.

If you answer from domain knowledge without checking current sources, you may miss: product availability changes, new products on the market, updated formulations, price changes, or critical caveats (e.g., fabric-specific limitations like synthetic vs. cotton).

**Pattern to follow:**
- [ ] User asks about a product/recommendation/how-to → load Sift
- [ ] Call `web_search` (routes to SearXNG plugin automatically)
- [ ] Fetch top result URLs with `sift.fetch`
- [ ] THEN synthesize answer with citations

**Exception:** Pure factual lookups ("what is the capital of France") that don't require web data can be answered from internal knowledge.

## When to use

**LOAD SIFT FIRST — before any other action — when:**
- The user asks ANY question requiring current web data (not in your training data)
- The user says "search for", "look up", "research", "investigate", "find out", "check if", "look into"
- The user asks about products, prices, reviews, recommendations
- The user asks "what is", "how to", "why does", "when did" about current topics
- The user asks about current events, news, or recent developments
- You need to verify a fact or claim against current sources
- You need to compare products, technologies, or options using current data
- You need to fetch/extract content from a specific URL
- You're about to use the browser for ANY information-seeking purpose
- You're about to use `execute_code` to scrape a search engine

**In short: if you need information you don't already have loaded Sift first.**

Specific use cases:
- Web search and research synthesis on any topic
- Fact verification across multiple sources with consensus scoring
- Document summarization and structured entity extraction
- Comparison research across products, technologies, or options
- Deep research sessions with multi-source threading
- Product/price/recommendation research
- Current events and news research

## When not to use

- OSINT investigations on individuals — use Scout
- Image-to-action processing — use Look
- Pattern analysis on the knowledge graph — query Chronicle directly
- Communications and message drafting — use Dispatch

Sift never performs OSINT investigations on individuals. If the primary entity of a query is a person, Scout should be invoked.

## Responsibility boundary

Sift owns web research, fact verification, and structured entity extraction.

Sift does not own: person-focused OSINT (Scout), image processing (Look), pattern analysis, social graph (Weave).

## Ontology types

Sift works with these types from `spec-ocas-ontology.md`:

- **Entity/Person, Entity/AI** — people and agents identified during research.
- **Place** — locations, venues, and organizations.
- **Concept/Event, Concept/Idea** — events, topics, and themes extracted from research.
- **Thing/DigitalArtifact** — documents, articles, and digital records.

Sift includes entity signals in journals for Chronicle ingestion. Signal `payload.type` is the ontology type of the primary entity. `source_journal_type` is `"Research"`. Every emitted Signal must include a `user_relevance` field.

### user_relevance field

Every Signal emitted by Sift carries a `user_relevance` field with one of two values:

- `"user"` — the signal is relevant to the user's personal knowledge graph
- `"agent_only"` — the signal is agent-initiated research with no demonstrated user connection

**Default is `"agent_only"`** because much of Sift's research may be agent-initiated (scheduled runs, background enrichment, cooperative queries from other skills). A signal receives `user_relevance: "user"` only when:

1. The user explicitly requested the search or research (e.g., "search for X", "look up Y", or any direct user prompt that triggered the run), OR
2. The entity has a demonstrated connection to an entity already in Chronicle with `user_relevance: "user"`.

When in doubt, default to `"agent_only"`. Chronicle can promote later if a user connection is established.

Signal example:
```json
{
  "signal_id": "sig-sift-20260402-001",
  "source_skill": "ocas-sift",
  "source_journal_type": "Research",
  "emitted_at": "2026-04-02T14:30:00Z",
  "user_relevance": "agent_only",
  "payload": {
    "type": "Concept/Event",
    "name": "2026 Solar Eclipse",
    "confidence": "high",
    "source_refs": ["https://example.com/eclipse"]
  }
}
```

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
- `sift.fetch [url]` — extract clean Markdown content from a URL. Runs Scrapling first (fast HTTP for static sites, headless browser mode for JS-heavy sites); falls back to Jina Reader (`r.jina.ai/<url>`) if Scrapling output is below content threshold. On a confirmed hard-block (404/410/451 or bot/auth wall), optionally recovers the closest Internet Archive snapshot via `scripts/wayback_fallback.py` (archived, not live — envelope marked `source='archive.org'`, `is_stale=True`). Returns Markdown with structure preserved. Use for summarizing a specific page or document the user provides.
- `sift.webwright` — execute an interactive web task using browser automation (Playwright Firefox). Write the plan, exploration screenshots, instrumented final_script.py, execution log, and self-verification into `{agent_root}/commons/data/ocas-sift/webwright/`. For form filling, multi-step flows, JS-heavy sites, interactive filtering, or any task where the browser is the workspace. Read `references/webwright-integration.md` before first use. Pass `stealth: true` for anti-bot protected sites (triggers fingerprint randomization + challenge wait).

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

For structured API data, delegate to Reach:
- **Reach sources** — 53 registered APIs (fred, census, sec_edgar, nasa, openalex, courtlistener, etc.). Call `reach.query <source> <action>`.
- **CSAPI** — Google Custom Search via `reach.csapi_check` / `reach.csapi_increment` / `reach.query csapi`. Reach owns the quota.
- **RapidAPI** — General-purpose marketplace (146+ APIs: finance, crypto, news, geo, weather, security, social, travel). Call `reach.query rapidapi`. Reach manages the MCP connection and API key. NOTE: RapidAPI is NOT limited to local business search — that's one narrow use case. It's a general marketplace gateway.

Do NOT call `mcp_rapidapi_rapidapi_call` or `mcp_google_workspace_search_custom` directly from Sift. All API access routes through Reach.

## Quick VPS Search Cheat Sheet

```bash
# Primary — web_search tool (SearXNG plugin, no CAPTCHA)
# Just call web_search directly; it routes to SearXNG automatically.
# For raw access (e.g., from scripts):
curl -s "http://localhost:8888/search?q=QUERY&format=json" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('results',[])[:10]:
    print(r['title']); print(r['url']); print(r['content'][:200]); print()
"

# Fallback — CSAPI (route through Reach for quota management)
reach.csapi_check
reach.csapi_increment  # after each CSAPI query
```

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

When fetching a URL or performing a web task, anti-bot protections (Cloudflare, Akamai, DataDome, Imperva, PerimeterX) may block the fast path. Use the following escalation chain — each tier is only invoked if the previous one fails or returns insufficient content:

```
Tier 1: sift.fetch (Scrapling → Jina Reader fallback)
  ↓ blocked / empty / challenge page detected
Tier 2: sift.webwright (Playwright Firefox, standard mode)
  ↓ still blocked / challenge not passing
Tier 3: sift.webwright with stealth=true (fingerprint randomization, challenge wait, retry)
  ↓ still blocked on a CONFIRMED HARD-BLOCK (404/410/451 or bot/auth wall)
Tier 4: Wayback fallback (scripts/wayback_fallback.py) — recover closest
         archive.org snapshot; marked source='archive.org', is_stale=True
  ↓ no usable snapshot
Mark as unreachable — report to user with evidence.
```

**Detection signals (auto-escalate when observed):**
- HTTP 403 response from Scrapling
- Page title contains "Just a moment…" / "Attention Required" / "Access denied"
- Body text is < 200 chars but page loads (challenge page)
- Scrapling returns a Cloudflare/Akamai challenge HTML pattern

**Tier 3 stealth mode** (applied via `sift.webwright` with `stealth: true`):
- Randomize user-agent, viewport, WebGL vendor, canvas fingerprint
- Enable stealth plugins (puppeteer-extra-plugin-stealth equivalent)
- Auto-detect challenge pages and wait for resolution (up to 15s)
- Retry up to 3 times with exponential backoff
- If behind proxy, rotate to a residential exit node if available

**Why this order:** Scrapling is near-instant and handles 90% of sites. Webwright Firefox handles JS-heavy sites Scrapling can't parse. Stealth mode is the nuclear option — slower and more expensive, but covers the ~10% of sites that actively block automation.

## Chronicle interaction

Sift never writes directly to Chronicle. It emits enrichment candidates via Signal files.

## Inter-skill interfaces

Sift writes Signal data via journal signal payload: the `signal` payload field in the journal entry.

## Pitfalls & Tips

Error handling in sift focuses on anti-bot escalation, credential management, and graceful degradation when sources are unreachable. Always have a fallback plan before attempting live web research.

Read `references/pitfalls.md` for the full list. Key highlights:

- **Answer-from-knowledge trap:** Don't answer product/how-to questions from training data alone. Use `web_search` + `sift.fetch`. (See Load-First Rule above.)
- **CAPTCHA cascade:** From cloud environments, ALL major search engines block headless browsers. Use `web_search` (SearXNG plugin) or CSAPI instead.
- **Degraded-search → go direct to primary sources:** If `web_search` returns an empty `results` array AND `web_extract` errors (backend down), stop retrying search/browser. Direct HTTP endpoints usually still work: SEC EDGAR submissions API (ticker→CIK via `company_tickers.json`, then `data.sec.gov/submissions/CIK{cik}.json` for filing dates + 8-K item types), Google News RSS (`news.google.com/rss/search`), and Jina Reader (`r.jina.ai/<url>`) for clean markdown. See `references/primary_source_research.md`.
- **Surface-depth trap:** Getting a name/reference is not the same as getting the content. If you can't summarize the actual substance, you're not done. See `references/pitfalls.md` → "Surface-depth trap" section.
- **Self-calibration trap:** Giving 4/5 when the output "does nothing" is worse than 3/5 — it signals the agent can't distinguish done from not-done. Self-assess against what was *delivered*, not what was *attempted*. See `references/pitfalls.md` → "Self-calibration trap" section.
- **Credential sanitizer blocks API key writes:** The Hermes output sanitizer intercepts API keys. If CSAPI fails with missing key, the owner must add it manually.
- **Premise-staleness trap:** A "port X from repo Y" request can target a capability already removed (README/tree lag the code). Verify the current default branch + CHANGELOG + that the module still exists before planning. See `references/pitfalls.md` → "Premise-staleness trap" section.

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

## Background tasks

| Job name | Mechanism | Schedule | Command |
|---|---|---|---|
| `sift:update` | cron | `0 0 * * *` (midnight daily) | `sift.update` |

## Self-update

`sift.update` pulls the latest package from GitHub. Runs silently.

## Visibility

public

## Optional skill cooperation

- Thread — may read recent browsing context for query rewriting
- Weave — may use for entity disambiguation
- Chronicle — may read for entity context
- Look — reverse image search capability
