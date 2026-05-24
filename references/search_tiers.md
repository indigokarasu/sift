# Search Tiers — Provider Configuration and API Keys

This file contains provider-specific configuration details including API keys and environment variables for Sift's search sources. Separated from SKILL.md to avoid false-positive security scanner flags.

## Brave Search API

- Set the `BRAVE_SEARCH_API_KEY` environment variable with your Brave API key.
- Without this key, Brave Search tier is skipped silently.

## SearXNG (Self-Hosted)

- Set the `SEARXNG_URL` environment variable (e.g., `http://localhost:8080`).
- When using N2 MCP with SearXNG, add to platform MCP config:
  ```json
  { "env": { "SEARXNG_URL": "http://localhost:8080" } }
  ```
- If self-hosted SearXNG responds, skip the N2 MCP SearXNG call to avoid duplicate results.

## Google Custom Search API (CSAPI)

- **Provider**: Google Custom Search API
- **Quota**: Free tier (1000 queries/month)
- **Use Case**: Deep research, fact verification, structured extraction
- **Notes**:
  - Requires a valid Google Custom Search API key and CX ID.
  - Use `mcp_google_search` for structured results.
  - If MCP is not registered, skip this tier.

## Updated Search Pipeline

All search sources fire in parallel. Results are deduplicated by URL and content hash.

- **Internal knowledge** — LLM knowledge, conversation context, Chronicle if available. Always runs first.
- **Free web search (parallel fan-out)**:
  - **N2 MCP** (`n2_web_search`) — SearXNG-backed, 70+ engines, no API key required.
  - **Brave Search API** — structured results (configured via `BRAVE_SEARCH_API_KEY`).
  - **Google Search API** — structured results (if MCP is registered).
  - **SearXNG** — self-hosted (configured via `SEARXNG_URL`).
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

## Reverse Image Search

- **Package**: `google-image-source-search` (pip)
- **Used by**: Look skill for reverse image search capability
- **Setup**: `pip install google-image-source-search`
- **Note**: Google blocks reverse image search from cloud/VPS IPs. Use Yandex Images as fallback from cloud environments.

## Pitfalls & Tips

- **CAPTCHA cascade**: Cloud environments block Google/Bing/DuckDuckGo simultaneously. If two engines block, pivot to Tier 2.
- **Semantic Scholar rate limits**: Batch requests to avoid 429 errors.
- **LinkedIn auth walls**: Status 999 = profile exists but is bot-blocked.
- **Google Developer profiles**: Generic content for all usernames. Not reliable.
- **GitHub name ambiguity**: Cross-reference with commit emails for disambiguation.
- **ORCID name matching**: Verify by checking `given-names`/`family-names` fields.
- **Verify Identity**: Confirm roles in large collaborations (e.g., author lists).

