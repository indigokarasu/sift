# Pitfalls & Tips

Common pitfalls and tips for Sift research sessions, especially when operating from cloud/VPS environments.

- **CAPTCHA cascade:** From cloud environments, ALL major search engines (Google, Bing, DDG HTML) will block headless browsers simultaneously. If two engines block, assume all will — stop browser-based search immediately and switch to Tier 2 API-only collection.
- **Semantic Scholar rate limits:** 429 errors are common when making rapid sequential requests. Batch author data into single calls (include all fields in one request). Wait 3-5 seconds between requests if hitting limits.
- **LinkedIn auth walls:** LinkedIn returns HTTP 200 for valid profile slugs but shows a login wall instead of content. Status 999 means the profile exists but is bot-blocked. LinkedIn profile titles visible in the `<title>` tag can sometimes confirm name and current company.
- **Google Developer profiles are generic:** `developers.google.com/profile/u/{username}` returns 200 for every username with identical generic content. This is NOT a valid way to confirm a person's Google employment.
- **GitHub user search is ambiguous:** Common names (Peter Oh, Gustavo Moura) return many results. Always cross-reference with commit email search (`author-email:EMAIL`) for disambiguation.
- **ORCID name matching is loose:** Search results frequently include non-target people with similar names. Always verify by checking the `given-names` and `family-names` fields in the profile response.
- **Verify Identity:** In large collaborations (e.g., Imagen, Gemini author lists with 50+ people), verify the specific role or authorship order to ensure the target isn't just a peripheral contributor. Use Semantic Scholar's `papers.authors` field to confirm exact position.
- **DBLP JSON API format:** The `.json` suffix on DBLP author pages doesn't work. Use the search API (`dblp.org/search/author/api`) instead.
- **Browser tool CAPTCHA:** Even `browser_navigate` to Google Search triggers CAPTCHA from cloud. Do not attempt browser-based general web search from cloud environments.
- **Reverse image search from cloud:** Google blocks all reverse image search from cloud/VPS IPs — both the `google-image-source-search` library and browser-based Google Lens. Use Yandex Images via browser (`yandex.com/images/search?url=...`) instead — it works reliably from cloud IPs and renders results server-side.
