# Sift — sift.fetch Behavior

`sift.fetch [url]` extracts clean Markdown from a specific URL.

**Fetch pipeline (sequential within the command):**
1. **Scrapling** — domain-aware: fast HTTP mode for static sites (~1–3s), headless browser mode for JS-heavy sites (~5–15s). Requires `scrapling[fetchers]` and `html2text` Python packages.
2. **Content-density check** — after Scrapling returns, count words in the `html2text` output (strip markdown links before counting). If output contains **≥ 200 words** of extractable text, return immediately — do not call Jina. If output contains < 200 words, is an error body, an empty response, or a JS-gated loading page: fall through to step 3. Do not retry Scrapling in a different mode if the content-density check fails — go straight to Jina.
3. **Jina Reader** — fallback at `https://r.jina.ai/<url>`. Free tier: 200 requests/day. Skipped for platforms where it performs poorly (WeChat, Zhihu, Juejin, CSDN).
4. **Fail cleanly** — if both methods fail, return a clear error message. No silent empty result. No retry.

Default output: Markdown with headings, links, lists, code blocks, and blockquotes preserved. Pass `--json` for metadata output (url, mode used, content length).

Do not use `sift.fetch` for general search — it fetches a specific known URL only.
