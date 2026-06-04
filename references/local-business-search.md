# Local Business Search — RapidAPI Places Workflow

When searching for local businesses, services, or venues (restaurants, tailors, cleaners, etc.), the most reliable source on VPS is **RapidAPI `google-search-master-mega`** with the `_Places` action.

## Why this works when everything else fails

- SearXNG (`localhost:8888`) may be down — always check first
- `web_search` MCP routes to SearXNG — fails if SearXNG is down
- `web_extract` gets 403 on Yelp, Google, Reddit from VPS IPs
- DuckDuckGo HTML scraping returns empty from VPS
- RapidAPI Google Search bypasses all of this

## Workflow

### Step 1: Search for places

```
mcp_rapidapi_rapidapi_call(
  api="google-search-master-mega",
  action="_Places",
  params={"num": 10, "q": "SERVICE_TYPE CITY_NAME"}
)
```

Returns structured results with: `title`, `address`, `rating`, `ratingCount`, `category`, `phoneNumber`, `website`, `cid`.

### Step 2: Cross-reference with web search (optional)

Use `_Search` action for review snippets and Reddit discussions:

```
mcp_rapidapi_rapidapi_call(
  api="google-search-master-mega",
  action="_Search",
  params={"num": 10, "q": "best SERVICE_TYPE CITY_NAME reviews"}
)
```

### Step 3: Fetch review content from URLs

Use `mcp_web_search_web_extract` on URLs from Step 2 (SFGATE, CBS, etc. usually work). Skip Yelp and Reddit (403).

## API Parameter Notes

- `_Places` uses `q` for query, `num` for count
- `_Reviews` uses different params: `fid`, `cid`, or `placeId` (NOT `q`) — and may still fail; prefer `_Places` ratings
- `_Search` uses `q` for query
- Discover available actions first: `mcp_rapidapi_rapidapi_discover(api="google-search-master-mega")`

## Fallback chain for local business search

1. RapidAPI `_Places` → structured ratings + addresses (BEST)
2. RapidAPI `_Search` → review snippets + URLs
3. `web_extract` on individual review URLs (SFGATE, CBS, local news)
4. CSAPI `search_custom` (check quota first)
5. DuckDuckGo HTML (often empty from VPS — try last)
