---
name: ocas-sift
description: >
  Sift: web search, research synthesis, fact verification, entity extraction,
  and URL content extraction. The system's general research engine. Use for
  topic research, web lookups, fact-checking, document summarization,
  comparison research, structured information extraction, or reading a
  specific URL. Trigger phrases: 'search for', 'look up', 'research this
  topic', 'fact check', 'compare', 'summarize this', 'what is', 'find
  information about', 'read this URL', 'fetch this page', 'update sift'. Do
  not use for person-focused OSINT investigations (use Scout) or image
  processing (use Look).
metadata:
  author: Indigo Karasu
  email: mx.indigo.karasu@gmail.com
  version: "2.8.5"
  hermes:
    tags: [search, research, web]
    category: signal
    cron:
      - name: "sift:update"
        schedule: "15 7 * * *"
        command: "sift.update"
  openclaw:
    skill_type: system
    visibility: public
    filesystem:
      read:
        - "{agent_root}/commons/data/ocas-sift/"
        - "{agent_root}/commons/journals/ocas-sift/"
      write:
        - "{agent_root}/commons/data/ocas-sift/"
        - "{agent_root}/commons/journals/ocas-sift/"
    self_update:
      source: "https://github.com/indigokarasu/sift"
      mechanism: "version-checked tarball from GitHub via gh CLI"
      command: "sift.update"
      requires_binaries: [gh, tar, python3, npx]
    requires:
      mcp:
        - name: "n2-free-search"
          description: "Free unlimited web search via SearXNG (70+ engines). Registered during sift.init."
          required: false
      pip:
        - "scrapling[fetchers]"
        - "html2text"
      credentials:
        - name: "brave_search_api_key"
          description: "Brave Search API key for structured web search"
          required: false
        - name: "exa_api_key"
          description: "Exa API key for semantic research"
          required: false
        - name: "tavily_api_key"
          description: "Tavily API key for semantic research"
          required: false
    cron:
      - name: "sift:update"
        schedule: "15 7 * * *"
        command: "sift.update"
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
  - **Platform search** — agent-reach on Twitter/X (via Mirror Rotator $\rightarrow$ Search Bridge), Reddit, LinkedIn, GitHub, etc.
- **Semantic research** — Exa, Tavily. Deep research only. Quota-limited (~50 calls/day combined). Runs when standard web search is insufficient.

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

## Storage layout

```
{agent_root}/commons/data/ocas-sift/
  config.json
  sessions.jsonl
  threads.jsonl
  entities.jsonl
  sources.jsonl
  decisions.jsonl
  reports/

{agent_root}/commons/journals/ocas-sift/
  YYYY-MM-DD/
    {run_id}.json
```

Default config.json:
```json
{
  "skill_id": "ocas-sift",
  "skill_version": "2.3.0",
  "config_version": "1",
  "created_at": "",
  "updated_at": "",
  "search": {
    "default_tier": 2,
    "tier3_daily_limit": 50
  },
  "retention": {
    "days": 30,
    "max_records": 10000
  }
}
```

## OKRs

Universal OKRs from spec-ocas-journal.md apply to all runs.

```yaml
skill_okrs:
  - name: source_accuracy
    metric: fraction of extracted facts confirmed by cross-source agreement
    direction: maximize
    target: 0.85
    evaluation_window: 30_runs
  - name: tier3_quota_compliance
    metric: fraction of days where Tier 3 usage stays within daily limit
    direction: maximize
    target: 1.0
    evaluation_window: 30_runs
  - name: entity_extraction_precision
    metric: fraction of extracted entities with valid source reference
    direction: maximize
    target: 0.90
    evaluation_window: 30_runs
```

## Optional skill cooperation

- Elephas — emit Signal files for Chronicle promotion after every extraction
- Thread — may read recent browsing context for query rewriting (cooperative read-only; see `spec-ocas-interfaces.md` Cooperative Query Interfaces)
- Weave — may use Weave for entity disambiguation (cooperative read-only; see `spec-ocas-interfaces.md` Cooperative Query Interfaces)
- Chronicle — may read Chronicle (read-only) for entity context

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
3. Create empty JSONL files: `sessions.jsonl`, `threads.jsonl`, `entities.jsonl`, `sources.jsonl`, `decisions.jsonl`
4. Create `{agent_root}/commons/journals/ocas-sift/`
5. Ensure journal payload fields (see interfaces specification) exists (create if missing)
6. Register cron job `sift:update` if not already present (check the platform scheduling registry first)
7. Log initialization as a DecisionRecord in `decisions.jsonl`
8. **N2 MCP setup** (run once; skip if `n2-free-search` MCP already registered):
   - Check: the platform MCP registry for `n2-free-search`
   - If not registered, add to platform MCP config:
     ```json
     {
       "mcpServers": {
         "n2-free-search": {
           "command": "npx",
           "args": ["-y", "n2-free-search"]
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

`sift.update` pulls the latest package from the `source:` URL in this file's frontmatter. Runs silently — no output unless the version changed or an error occurred.

1. Read `source:` from frontmatter → extract `{owner}/{repo}` from URL
2. Read local version from SKILL.md frontmatter `metadata.version`
3. Fetch remote version from SKILL.md frontmatter: `gh api "repos/{owner}/{repo}/contents/SKILL.md" --jq '.content' | base64 -d | grep 'version:' | head -1 | sed 's/.*"\(.*\)".*/\1/'`
4. If remote version equals local version → stop silently
5. Download and install:
   ```bash
   TMPDIR=$(mktemp -d)
   gh api "repos/{owner}/{repo}/tarball/main" > "$TMPDIR/archive.tar.gz"
   mkdir "$TMPDIR/extracted"
   tar xzf "$TMPDIR/archive.tar.gz" -C "$TMPDIR/extracted" --strip-components=1
   cp -R "$TMPDIR/extracted/"* ./
   rm -rf "$TMPDIR"
   ```
6. On failure → retry once. If second attempt fails, report the error and stop.
7. Output exactly: `I updated Sift from version {old} to {new}`

## Visibility

public

## Support file map

| File | When to read |
|---|---|
| `references/schemas.md` | Before creating sessions, threads, or extraction records |
| `references/search_tiers.md` | Before tier selection or escalation |
| `references/query_rewrite.md` | Before query rewriting |
| `references/journal.md` | Before sift.journal; at end of every run |

## Update command

This skill self-updates every 24 hours via:

```bash
sift.update
```

This pulls the latest version from GitHub and restarts the skill's background tasks if applicable.

## Integrated: research-fallback-pivot

# Research Fallback Pivot

When performing deep dives on individuals (researchers, executives, engineers) and encountering `web_search` credit limits or Google CAPTCHAs, pivot from "General Search" to "Direct Registry Navigation."

## Trigger Conditions
- `web_search` returns "Insufficient credits".
- `browser_navigate` to Google/Scholar returns a "detected unusual traffic" or CAPTCHA page.
- High-value targets who likely have profiles in structured academic or legal databases.

## Step-by-Step Workflow

### Tier 0: Check credit availability first
Before anything else, try one `mcp_tavily_tavily_search` call. If it returns a 432 "usage limit" error, immediately skip to Tier 2 (API-only). Do not waste additional calls on credit-limited services.

### Tier 1: Web search (if credits available)
- Use `mcp_tavily_tavily_search` or `web_search` for broad queries.
- If credits run out mid-research, pivot immediately to Tier 2.

### Tier 2: API-only collection (proven fallback from cloud environments)

When all web search services are credit-limited AND major search engines (Google, Bing) return CAPTCHA pages from cloud IPs, use this specific API stack in order:

1. **GitHub API** (no auth required, curl-based):
   - User search: `curl -s "https://api.github.com/search/users?q=FULLNAME"`
   - Commit search by email: `curl -s "https://api.github.com/search/commits?q=author-email:EMAIL"`
   - User profile: `curl -s "https://api.github.com/users/LOGIN"` (returns name, company, bio, location, blog)
   - Search Users, Issues, Commits, and Organizations. Email-based commit search is especially precise for corporate addresses.

2. **Semantic Scholar API** (free, 100 requests/5min):
   - Author search: `curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=FULLNAME&limit=5"`
   - Author details: `curl -s "https://api.semanticscholar.org/graph/v1/author/AUTHOR_ID?fields=name,affiliations,paperCount,citationCount,hIndex,papers.title,papers.year,papers.venue,papers.citationCount,papers.authors,papers.externalIds"`
   - Paper search: `curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=TOPIC&limit=3&fields=title,authors,year"`
   - **Rate limit: 429 errors are common.** Space requests 3-5 seconds apart. Batch by getting all needed data per author in one call.

3. **ORCID Public API** (free, JSON):
   - Search: `curl -s -H "Accept: application/json" "https://pub.orcid.org/v3.0/search/?q=FIRSTNAME+LASTNAME&rows=3"`
   - Profile: `curl -s -H "Accept: application/json" "https://pub.orcid.org/v3.0/{ORCID_ID}/person"`
   - Note: Name matching is loose — results often include non-target people with similar names. Verify by checking given-name/family-name fields.

4. **arXiv API** (free, XML):
   - Search: `curl -s "http://export.arxiv.org/api/query?search_query=au:LASTNAME+FIRSTNAME&max_results=5"`
   - Returns author names in `<name>` tags and paper titles. Limited to arXiv-indexed papers only.

5. **Direct profile URL probing** (curl with status code check):
   - `curl -s -o /dev/null -w "%{http_code}" -L --max-time 10 URL` — 200 means profile exists, 404 means not found
   - **LinkedIn:** `https://www.linkedin.com/in/slug/` — returns 200 for valid slugs but content is auth-walled. 999 status = exists but bot-blocked.
   - **Google Developer profiles:** `https://developers.google.com/profile/u/USERNAME` — **useless**, returns 200 for ALL usernames with identical generic content. Do not rely on these.
   - **Google Research:** `https://research.google/people/SLUG/` — returns 404 for most researchers. URL format is not predictable. Not reliable for probing.
   - **DuckDuckGo HTML:** Also returns CAPTCHA/empty results from cloud environments. Do not waste time on `html.duckduckgo.com/html/`.

6. **Curl-based page extraction** for known URLs:
   - When DDG HTML search (initial step) returns results with specific URLs, fetch them directly with `curl -s -L -H "User-Agent: Mozilla/5.0"` and parse with regex.
   - Niche profile sites (conference bios, company leadership pages, industry press) often work well — Women in Tech Summit, Gambling Insider, SwissCognitive, etc.

7. **DBLP** (Computer Science bibliography):
   - Search: `curl -s "https://dblp.org/search/author/api?q=NAME&format=json&h=3"`
   - Publication search: `curl -s "https://dblp.org/search/publ/api?q=KEYWORD&format=json&h=5"`
   - Note: Name matching is loose; returns multiple candidates. Verify each manually.

### Tier 3: Domain-specific pivots

- **Google employees:** Search for their name associated with known Google projects (Gemini, Imagen, Assistant, Lens) on Semantic Scholar and arXiv. Get paper author lists to confirm association.
- **Meta employees:** Search GitHub for `@meta.com` email commits.
- **Patents:** Use `https://patents.google.com/` directly for inventor search.

### Synthesis
Aggregate findings from structured sources to build the profile. Mark confidence levels: "high" for confirmed (direct source match), "med" for inferred (email domain + project association), "low" for unconfirmed (name-only match without verification).

### Tier 2.5: SearXNG local instance (if available)

If a SearXNG instance is running locally (e.g., on localhost:8889), it can serve as an unlimited, credit-free search engine with aggregated results from multiple backends (Google, Brave, DuckDuckGo, Startpage, etc.).

**How to query SearXNG via browser:**
1. Navigate to `http://localhost:8889/search?q=YOUR+QUERY&format=json`
2. Parse the JSON response via `browser_console` (`document.body.innerText`)
3. Results are in the `results` array with `url`, `title`, `content`, `engine`, and `score` fields
4. Fetch full pages by navigating to result URLs with `browser_navigate`, then extract text with `browser_console` or `browser_snapshot`

**Advantages over API-only collection:**
- Returns aggregated results from multiple search engines simultaneously
- No API keys or credits needed
- Supports all query types (not just person/entity lookup)
- Direct URL extraction makes page fetching easy

**Limitations:**
- Requires a running SearXNG instance
- Some engines may be blocked or return access denied from the server's IP
- Result quality depends on which engines SearXNG can reach
- No specialized academic/database APIs, just general web search

**Example workflow:**
```
1. browser_navigate → http://localhost:8889/search?q=QUERY&format=json
2. browser_console → document.body.innerText (parse JSON for top results)
3. browser_navigate → https://result-url.example.com/page
4. browser_console → document.querySelector('article,main').innerText
5. Repeat for additional results or secondary searches
```

## Pitfalls & Tips
- **CAPTCHA cascade:** From cloud environments, ALL major search engines (Google, Bing, DDG HTML) will block headless browsers simultaneously. If two engines block, assume all will — stop browser-based search immediately and switch to Tier 2 API-only collection.
- **Semantic Scholar rate limits:** 429 errors are common when making rapid sequential requests. Batch author data into single calls (include all fields in one request). Wait 3-5 seconds between requests if hitting limits.
- **LinkedIn auth walls:** LinkedIn returns HTTP 200 for valid profile slugs but shows a login wall instead of content. Status 999 means the profile exists but is bot-blocked. LinkedIn profile titles visible in the `<title>` tag can sometimes confirm name and current company.
- **Google Developer profiles are generic:** `developers.google.com/profile/u/{username}` returns 200 for every username with identical generic content. This is NOT a valid way to confirm a person's Google employment.
- **GitHub user search is ambiguous:** Common names (Peter Oh, Gustavo Moura) return many results. Always cross-reference with commit email search (`author-email:EMAIL`) for disambiguation.
- **ORCID name matching is loose:** Search results frequently include non-target people with similar names. Always verify by checking the `given-names` and `family-names` fields in the profile response.
- **Verify Identity:** In large collaborations (e.g., Imagen, Gemini author lists with 50+ people), verify the specific role or authorship order to ensure the target isn't just a peripheral contributor. Use Semantic Scholar's `papers.authors` field to confirm exact position.
- **DBLP JSON API format:** The `.json` suffix on DBLP author pages doesn't work. Use the search API (`dblp.org/search/author/api`) instead.
- **Browser tool CAPTCHA:** Even `browser_navigate` to Google Search triggers CAPTCHA from cloud. Do not attempt browser-based general web search from cloud environments.
