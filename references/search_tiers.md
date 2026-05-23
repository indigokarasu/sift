# Google Search Tier

- **Provider**: Google Custom Search API (CSAPI)
- **Command**: `mcp_google_search` (custom MCP)
- **Quota**: Free tier (1000 queries/month)
- **Use Case**: Deep research, fact verification, structured extraction
- **Notes**:
  - Requires a valid Google Custom Search API key and CX ID.
  - Use `mcp_google_search` for structured results.
  - If MCP is not registered, skip this tier.

# Updated Search Pipeline

All search sources fire in parallel. Results are deduplicated by URL and content hash.

- **Internal knowledge** — LLM knowledge, conversation context, Chronicle if available. Always runs first.
- **Free web search (parallel fan-out)**:
  - **N2 MCP** (`n2_web_search`) — SearXNG-backed, 70+ engines, no API key required.
  - **Brave Search API** — structured web results (if `BRAVE_SEARCH_API_KEY` is set).
  - **Google Search API** — structured results (if MCP is registered).
  - **SearXNG** — self-hosted if `SEARXNG_URL` is set; otherwise, N2 MCP covers this.
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

## Pitfalls & Tips
- **CAPTCHA cascade**: Cloud environments block Google/Bing/DuckDuckGo simultaneously. If two engines block, pivot to Tier 2.
- **Semantic Scholar rate limits**: Batch requests to avoid 429 errors.
- **LinkedIn auth walls**: Status 999 = profile exists but is bot-blocked.
- **Google Developer profiles**: Generic content for all usernames. Not reliable.
- **GitHub name ambiguity**: Cross-reference with commit emails for disambiguation.
- **ORCID name matching**: Verify by checking `given-names`/`family-names` fields.
- **Verify Identity**: Confirm roles in large collaborations (e.g., author lists).