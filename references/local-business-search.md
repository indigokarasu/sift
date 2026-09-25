# Local Business Search — Structured Places Data via Reach

When to read: when searching for local businesses, services, or venues (restaurants,
tailors, cleaners, gyms, repair shops), where structured address/rating data beats
generic web results.

## Why this path

SearXNG (`localhost:8888`) is the first choice, but from a VPS IP the usual
consumers of local-business content are hostile: `web_extract` gets 403 on Yelp,
Google, and Reddit; DuckDuckGo HTML frequently returns empty; browser search is
CAPTCHA-blocked. A Places API returns structured fields — title, address, rating,
rating count, category, phone, website — that survive all of that.

## Workflow

1. **Places search** — route through Reach (Sift never calls RapidAPI directly):
   `reach.query rapidapi` with `api=google-search-master-mega`, `action=_Places`,
   `params={"num": 10, "q": "SERVICE_TYPE CITY_NAME"}`.
   Returns: title, address, rating, ratingCount, category, phoneNumber, website, cid.
2. **Qualitative signal** — a `_Search` action through the same route returns review
   snippets and review URLs when ratings alone are not enough.
3. **Read the reviews** — fetch promising review URLs with `sift.fetch`. Local news
   and magazine domains (SFGATE, CBS local, city blogs) work; skip Yelp/Reddit
   (403 from VPS IPs).

## Parameter notes

- `_Places` uses `q` + `num`; `_Search` uses `q`; `_Reviews` takes `fid`/`cid`/`placeId`
  (not `q`) and often fails — prefer `_Places` ratings plus review snippets instead.
- Discover available actions first via the `rapidapi` skill or `reach.query rapidapi`.

## Fallback chain

1. RapidAPI `_Places` — structured ratings + addresses (best signal-to-noise)
2. RapidAPI `_Search` — review snippets and URLs
3. `sift.fetch` on individual review URLs (news/blog domains)
4. CSAPI via Reach (`reach.csapi_check` first, then `reach.query csapi`)
5. DuckDuckGo HTML (`references/ddg_html_fallback.md`) — often empty from VPS, last resort

For business *discovery* beyond a single query — scanning a city, comparing a category —
use the anti-bot escalation chain (`references/escalation-pattern.md`) or `sift.webwright`.
