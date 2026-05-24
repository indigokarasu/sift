---
name: ocas-sift
description: 'Sift: web search, research synthesis, fact verification, entity extraction,
  and URL content extraction. The system''s general research engine. Use for topic
  research, web lookups, fact-checking, document summarization, comparison research,
  structured information extraction, or reading a specific URL. Trigger phrases: ''search
  for'', ''look up'', ''research this topic'', ''fact check'', ''compare'', ''summarize
  this'', ''what is'', ''find information about'', ''read this URL'', ''fetch this
  page'', ''update sift''. Do not use for person-focused OSINT investigations (use
  Scout) or image processing (use Look).

  '
license: MIT
metadata:
  author: Indigo Karasu
  version: 2.8.7
---

# Sift

Sift is the system's general research engine, retrieving and synthesizing information from the web across a tiered source hierarchy — internal knowledge first, then free web search, then rate-limited semantic research providers for deep work. It evaluates source reliability through cross-source agreement scoring, extracts structured entities from retrieved content, and emits enrichment candidates to Chronicle so researched knowledge accumulates over time.

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

Sift never performs OSINT investigations on individuals. If the primary entity of a query is a person, Scout should be invoked.

## Responsibility boundary

Sift owns web research, fact verification, and structured entity extraction.

Sift does not own: person-focused OSINT (Scout), image processing (Look), knowledge graph writes (Elephas), pattern analysis (Corvus), social graph (Weave).

## Ontology types

Sift works with these types from `spec-ocas-ontology.md`:

- **Entity/Person, Entity/AI** — people and agents identified during research.
- **Place** — locations, venues, and organizations.
- **Concept/Event, Concept/Idea** — events, topics, and themes extracted from research.
- **Thing/DigitalArtifact** — documents, articles, and digital records.

Sift emits Signals to Elephas for entities and relationships extracted with confidence ≥ med. Signal `payload.type` is the ontology type of the primary entity. `source_journal_type` is `"Research"`. Every emitted Signal must include a `user_relevance` field.

### user_relevance field

Every Signal emitted by Sift carries a `user_relevance` field with one of two values:

- `"user"` — the signal is relevant to the user's personal knowledge graph
- `"agent_only"` — the signal is agent-initiated research with no demonstrated user connection

**Default is `"agent_only"`** because much of Sift's research may be agent-initiated (scheduled runs, background enrichment, cooperative queries from other skills). A signal receives `user_relevance: "user"` only when:

1. The user explicitly requested the search or research (e.g., "search for X", "look up Y", or any direct user prompt that triggered the run), OR
2. The entity has a demonstrated connection to an entity already in Chronicle with `user_relevance: "user"`.

When in doubt, default to `"agent_only"`. Elephas can promote later if a user connection is established.

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
- `sift.fetch [url]` — extract clean Markdown content from a URL. Runs Scrapling first (fast HTTP for static sites, headless browser for JS-heavy sites); falls back to Jina Reader (`r.jina.ai/<url>`) if Scrapling output is below content threshold. Returns Markdown with structure preserved. Use for summarizing a specific page or document the user provides.

## Response modes

Sift classifies query depth automatically:

- **quick_answer** — simple factual lookups, single-source sufficient
- **comparison** — multi-source comparison with structured output
- **research** — deep multi-session investigation with threading
- **document_analysis** — URL or document-focused extraction

Users may override with phrases like "quick answer", "deep dive", "compare", or "summarize".

## Search tier selection

All configured search sources fire in parallel. Results are deduplicated by URL and content hash.

- **Internal knowledge** — LLM knowledge, conversation context, Chronicle if available. Always runs first as a pre-check.
- **Free web search (parallel fan-out)** — all of the following fire simultaneously:
  - **N2 MCP** (`n2_web_search`) — SearXNG-backed, 70+ engines, no API key required. Registered during `sift.init`. Also provides `n2_news_search` for recency-focused queries.
  - **Brave Search API** — structured web results. Runs when `BRAVE_SEARCH_API_KEY` is set.
  - **SearXNG** — self-hosted if `SEARXNG_URL` env var is set; otherwise N2 MCP covers this. **Deduplication gate:** if `SEARXNG_URL` is set and the self-hosted instance responds, skip the N2 MCP call — both are SearXNG-backed and results would duplicate.
  - **Platform search** — agent-reach on Twitter/X (via Mirror Rotator → Search Bridge), Reddit, LinkedIn, GitHub, etc.
- **Semantic research** — Exa, Tavily. Deep research only. Quota-limited (~50 calls/day combined). Runs when standard web search is insufficient.

For detailed tier-by-tier workflow, API curl examples, and cloud environment fallbacks, read `references/research-workflow.md`.

Read `references/search_tiers.md` for provider details.

## Source reputation model

Sift maintains per-domain trust scores based on: cross-source agreement, contradiction frequency, historical accuracy, structured data quality, citation frequency.

## Structured extraction rules

When pages are retrieved, extract: entities (with type from shared ontology), claims, statistics, relationships, citations. Each extraction includes confidence level.

Extracted entities are emitted as enrichment candidates for Elephas.

## Run completion

After every Sift command that produces results:

1. Persist session, entities, sources, and decisions to local JSONL files
2. For each extracted entity or relationship with confidence >= `med`: write a Signal file to the `signal` payload field in the journal entry. Use Signal schema from `spec-ocas-shared-schemas.md`. Every Signal must include `user_relevance` (see Ontology types section). Set `"user"` if the run was user-initiated or the entity connects to a `user_relevance: "user"` Chronicle entry; otherwise `"agent_only"`.
3. Write journal via `sift.journal`

## sift.fetch behavior

`sift.fetch [url]` extracts clean Markdown from a specific URL.

**Fetch pipeline (sequential within the command):**
1. **Scrapling** — domain-aware: fast HTTP mode for static sites (~1–3s), headless browser mode for JS-heavy sites (~5–15s). Requires `scrapling[fetchers]` and `html2text` Python packages.
2. **Content-density check** — after Scrapling returns, count words in the `html2text` output (strip markdown links before counting). If output contains **≥ 200 words** of extractable text, return immediately — do not call Jina. If output contains < 200 words, is an error body, an empty response, or a JS-gated loading page: fall through to step 3. Do not retry Scrapling in a different mode if the content-density check fails — go straight to Jina.
3. **Jina Reader** — fallback at `https://r.jina.ai/<url>`. Free tier: 200 requests/day. Skipped for platforms where it performs poorly (WeChat, Zhihu, Juejin, CSDN).
4. **Fail cleanly** — if both methods fail, return a clear error message. No silent empty result. No retry.

Default output: Markdown with headings, links, lists, code blocks, and blockquotes preserved. Pass `--json` for metadata output (url, mode used, content length).

Do not use `sift.fetch` for general search — it fetches a specific known URL only.

## Chronicle interaction

Sift never writes directly to Chronicle. It emits enrichment candidates via Signal files to the `signal` payload field in the journal entry. Elephas decides promotion.

## Inter-skill interfaces

Sift writes Signal files to Elephas (via journal signal payload): the `signal` payload field in the journal entry

Every Signal must include the `user_relevance` field (`"user"` or `"agent_only"`). Elephas decides promotion.

Sift may read from Thread (when present) for recent browsing context to improve query rewriting. This is a cooperative read, not a dependency.

See `spec-ocas-interfaces.md` for signal format.

## Pitfalls & Tips

Read `references/pitfalls.md` for the full list of 10 common pitfalls. Key highlights:

- **CAPTCHA cascade:** From cloud environments, ALL major search engines block headless browsers simultaneously. Switch to Tier 2 API-only collection immediately. See `references/research-workflow.md` for the full workflow.
- **Semantic Scholar rate limits:** Space requests 3-5 seconds apart; batch author data into single calls.
- **LinkedIn/Google Developer profiles:** Auth-walled or generic — don't rely on them for identity confirmation.
- **Reverse image search from cloud:** Google blocks from cloud/VPS IPs. Use Yandex Images instead.

## Recovery Behavior

This skill implements the recovery contract from `spec-ocas-recovery.md`.

- **Evidence**: Every search/research run writes an evidence record to `{agent_root}/commons/data/ocas-sift/evidence.jsonl`, including no-op runs. The `not_activity_reason` field is mandatory when no side effects occur.
- **Gap detection**: On every wake, checks the evidence log. If gap exceeds 24h for update cron, logs `gap_detected`.
- **Degraded mode**: When search APIs (SearXNG, Brave, Tavily) are unavailable, logs `degraded: <api>` and continues with available sources.
- **Log compaction**: Evidence and decision logs older than 30 days (no-op) or 90 days (error/gap) compacted. Last 7 days retained.

## Storage layout

```
{agent_root}/commons/data/ocas-sift/  → config, sessions, threads, entities, sources, decisions, intents, evidence (all .jsonl), reports/
{agent_root}/commons/journals/ocas-sift/YYYY-MM-DD/{run_id}.json
```

## OKRs

Universal OKRs from spec-ocas-journal.md apply to all runs. Five OKRs: source_accuracy (0.85), tier3_quota_compliance (1.0), entity_extraction_precision (0.90), schedule_adherence (0.95), data_integrity (0.90).

## Optional skill cooperation

- Elephas — emit Signal files for Chronicle promotion after every extraction
- Thread — may read recent browsing context for query rewriting (cooperative read-only; see `spec-ocas-interfaces.md` Cooperative Query Interfaces)
- Weave — may use Weave for entity disambiguation (cooperative read-only; see `spec-ocas-interfaces.md` Cooperative Query Interfaces)
- Chronicle — may read Chronicle (read-only) for entity context
- Look — reverse image search via `google-image-source-search`. When Sift encounters an image URL during research and needs to find its source or matches, delegate to Look's reverse image search capability.

## Journal outputs

- Observation Journal — search and extraction runs
- Research Journal — structured multi-source research sessions

Journals must include an `entities_observed` array listing every entity encountered during the run, each tagged with its relevance:

```json
{
  "entities_observed": [
    { "name": "2026 Solar Eclipse", "type": "Concept/Event", "confidence": "high", "user_relevance": "user" },
    { "name": "NASA", "type": "Organization", "confidence": "high", "user_relevance": "agent_only" }
  ]
}
```

## Initialization

On first invocation of any Sift command, run `sift.init`:

1. Create `{agent_root}/commons/data/ocas-sift/` and subdirectories (`reports/`)
2. Write default `config.json` with ConfigBase fields if absent
3. Create empty JSONL files: `sessions.jsonl`, `threads.jsonl`, `entities.jsonl`, `sources.jsonl`, `decisions.jsonl`, `intents.jsonl`, `evidence.jsonl`
4. Create `{agent_root}/commons/journals/ocas-sift/`
5. Ensure journal payload fields (see interfaces specification) exists (create if missing)
6. Register cron job `sift:update` if not already present (check the platform scheduling registry first)
7. Log initialization as a DecisionRecord in `decisions.jsonl`
8. **N2 MCP setup** (run once; skip if `n2-free-search, google-search` MCP already registered):
   - Check: the platform MCP registry for `n2-free-search, google-search`
   - If not registered, add to platform MCP config:
     ```json
     {
       "mcpServers": {
         "n2-free-search, google-search": {
           "command": "npx",
           "args": ["-y", "n2-free-search, google-search"]
         }
       }
     }
     ```
   - For self-hosted SearXNG, set `SEARXNG_URL` env var and use:
     ```json
     { "env": { "SEARXNG_URL": "http://localhost:8080" } }
     ```

9. **Scrapling setup** (required for `sift.fetch`; run once):
   ```bash
   pip install scrapling[fetchers] html2text
   python3 -c "from scrapling.fetchers import PlaywrightFetcher; PlaywrightFetcher.auto_match_install()"
   ```

## Background tasks

| Job name | Mechanism | Schedule | Command |
|---|---|---|---|
| `sift:update` | cron | `0 0 * * *` (midnight daily) | `sift.update` |

```
# Task declared in SKILL.md frontmatter metadata.{platform}.cron
```

## Self-update

`sift.update` pulls the latest package from the `source:` URL in this file's frontmatter. Runs silently — no output unless the version changed or an error occurred. Compares local vs remote version via GitHub API, downloads tarball if different, extracts in place. Retries once on failure. Output on success: `I updated Sift from version {old} to {new}`.

## Visibility

public

## Support file map

| File | When to read |
|---|---|
| `references/schemas.md` | Before creating sessions, threads, or extraction records |
| `references/search_tiers.md` | Before tier selection or escalation |
| `references/query_rewrite.md` | Before query rewriting |
| `references/journal.md` | Before sift.journal; at end of every run |
| `references/research-workflow.md` | When executing research sessions, especially from cloud environments with CAPTCHA/credit issues |
| `references/pitfalls.md` | Before research runs; when encountering rate limits, auth walls, or cloud IP blocks |

## Update command

This skill self-updates every 24 hours via:

```bash
sift.update
```

This pulls the latest version from GitHub and restarts the skill's background tasks if applicable.
