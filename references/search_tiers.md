# Search Tiers — Provider Configuration and API Keys

This file contains provider-specific configuration details including API keys and environment variables for Sift's search sources. Separated from SKILL.md to avoid false-positive security scanner flags.

## Brave Search API

- Set the `BRAVE_SEARCH_API_KEY` environment variable with your Brave API key.
- Without this key, Brave Search tier is skipped silently.

## SearXNG (Plugin)

SearXNG is a first-class Hermes plugin (`web-searxng`). The `web_search` tool routes to it automatically when `web.backend: searxng` is configured in config.yaml and `SEARXNG_URL` is set in `.env`.

- Set via: `hermes config set SEARXNG_URL http://localhost:8888`
- Set backend: `hermes config set web.backend searxng`
- No API key required — the plugin reads `SEARXNG_URL` from the `.env` file at runtime
- Supports 70+ search engines via metasearch
- Primary search source on VPS/cloud environments (no CAPTCHA)

## Google Custom Search API (CSAPI)

- **Provider**: Google Custom Search JSON API
- **Quota**: Free tier (1000 queries/month)
- **Use Case**: Fallback when free web search (SearXNG/Brave) returns insufficient results. Does NOT use browser automation — calls the API directly, so it is NOT affected by Google's headless browser / CAPTCHA blocks. Works reliably from datacenter/VPS IPs.
- **Managed by**: ocas-reach (registered source). Route CSAPI queries through Reach.
- **Quota Tracking**: Reach owns the quota script at `skills/ocas-reach/scripts/csapi_quota.py`. Call `reach.csapi_check` before querying, `reach.csapi_increment` after each query.
- **Notes**:
  - Requires THREE things: (a) OAuth scope `https://www.googleapis.com/auth/cse` on the workspace-mcp token, (b) `GOOGLE_PSE_API_KEY` env var (the GCP Console API key, format `AIza...`), AND (c) `GOOGLE_PSE_ENGINE_ID` env var (the Custom Search Engine ID).
  - ⚠️ The PSE API key and engine ID must be set **manually by the owner** — the agent cannot write them through any tool due to the Hermes credential sanitizer.
  - **Multiple accounts**: The workspace-mcp has been patched to use per-account API keys. Set `GOOGLE_PSE_API_KEY` for the default account (owner) and `GOOGLE_PSE_API_KEY_INDIGO` for the Indigo account. Each account gets its own 1,000 queries/month free tier.

## Playwright Browser Search (DEPRECATED / DISABLED)

- The `google-search` MCP (Playwright + Chromium browser scraper) has been **disabled** in the Hermes config.
- Google permanently blocks datacenter/VPS IPs via CAPTCHA when using browser automation. This cannot be fixed with proxies or fingerprint changes.
- Use CSAPI (`mcp_google_workspace_search_custom`) instead for reliable open web search from this VPS.

## Updated Search Pipeline

All search sources fire in parallel. Results are deduplicated by URL and content hash.

- **Internal knowledge** — LLM knowledge, conversation context, Chronicle if available. Always runs first.
- **Free web search (parallel fan-out)**:
  - **`web_search` tool (SearXNG plugin)** — self-hosted metasearch, 70+ engines, no API key. Primary on VPS.
  - **Brave Search API** — structured results (configured via `BRAVE_SEARCH_API_KEY`).
  - **Platform search** — agent-reach on Twitter/X, Reddit, LinkedIn, GitHub, etc.
- **Semantic research** — Exa, Tavily. Deep research only. Quota-limited (~50 calls/day combined). Runs when standard web search is insufficient.

## Fallback Pivot for High-Value Targets

When performing deep dives on individuals (researchers, executives, engineers) and encountering web search limitations:

1. **Check credit availability** first (e.g., `mcp_tavily_tavily_search`). If it returns a 432 error, skip to Tier 2.
2. **Tier 2: API-only collection** (fallback from cloud environments):
   - **GitHub API** (no auth required): Search users, commits, profiles.
   - **Semantic Scholar API** (free, 100 requests/5min): Author/paper search.
   - **ORCID API** (free): Profile verification.
   - **arXiv API** (free): Academic paper search.
   - **Direct profile probing**: Curl with status code checks (e.g., LinkedIn, GitHub).

## Webwright — Interactive Browser Agent

- **Package**: `webwright` (pip), `playwright` (already installed)
- **Browser**: Firefox (headless) — handles sites that reject Chromium via TLS/H2 fingerprinting
- **Use when**: Form filling, multi-step flows, JS-heavy sites, interactive filtering, tasks requiring browser state
- **Not for**: Simple lookups (use `sift.search`) or URL extraction (use `sift.fetch`)
- **Workspace**: `{agent_root}/commons/data/ocas-sift/webwright/`
- **Reference**: `references/webwright-integration.md`
- **Setup**: `pip install webwright` (already installed), `playwright install firefox`

## Reverse Image Search

- **Package**: `google-image-source-search` (pip)
- **Used by**: Look skill for reverse image search capability
- **Setup**: `pip install google-image-source-search`
- **Note**: Google blocks reverse image search from cloud/VPS IPs. Use Yandex Images as fallback from cloud environments.

## Pitfalls & Tips

- **CAPTCHA cascade from VPS/cloud IPs**: The Playwright-based google-search MCP will be blocked by Google CAPTCHA from datacenter addresses. Do not retry — it will not self-resolve. Use the Server Custom Search API (`mcp_google_workspace_search_custom`) or SearXNG (`curl` to `http://localhost:8888`) instead.
- **Semantic Scholar rate limits**: Batch requests to avoid 429 errors.
- **LinkedIn auth walls**: Status 999 = profile exists but is bot-blocked.
- **Google Developer profiles**: Generic content for all usernames. Not reliable.
- **GitHub name ambiguity**: Cross-reference with commit emails for disambiguation.
- **ORCID name matching**: Verify by checking `given-names`/`family-names` fields.
- **Verify Identity**: Confirm roles in large collaborations (e.g., author lists).

