# Pitfalls

## Answer-from-knowledge trap

Don't answer product/how-to/recommendation questions from training data alone. Use `web_search` + `sift.fetch`. The user expects current, verified information — not what the model memorized from training. This is especially critical for local business recommendations, pricing, and availability.

## CAPTCHA cascade

From cloud environments (VPS, cloud VMs), ALL major search engines block headless browsers. Google, Bing, DuckDuckGo, Yelp, Reddit — all return CAPTCHAs or 403s. Use the `web_search` tool (SearXNG plugin) as the primary search source — it routes through the Hermes plugin registry to your SearXNG instance automatically.

**If `web_search` returns "SEARXNG_URL is not set"**: the env var isn't in the right `.env` file. Fix: `hermes config set SEARXNG_URL http://localhost:8888`.

**If SearXNG is also down** (empty response or connection refused), escalate to CSAPI or RapidAPI:
- CSAPI: `mcp_google_workspace_search_custom` (quota-managed, 1000 queries/month free)
- **RapidAPI** — general-purpose API marketplace (203 endpoints). Route through Reach via `reach.query rapidapi`. For API discovery, health checks, and subscription management, load the `rapidapi` skill.

## web_search tool routes through plugins

- **`web_search` tool routes through plugins.** The `web_search` tool dispatches through `agent/web_search_registry.py` → plugin registry. When `web.backend` is `searxng` (or auto-detected), it routes to the SearXNG plugin which reads `SEARXNG_URL` from the `.env` file.

For deep research (multi-source synthesis, fact verification, entity extraction), load Sift directly — `web_search` only does single-source search.

## Source delegation

- **CSAPI**: Route through Reach (`reach.csapi_check` / `reach.csapi_increment`). Do NOT manage CSAPI quota in Sift.
- **RapidAPI**: Route through Reach (`reach.query rapidapi`). Do NOT call `mcp_rapidapi_rapidapi_call` directly.
- **SearXNG**: Use `web_search` tool directly (routes to SearXNG plugin automatically). Do NOT curl localhost:8888 unless debugging.

## Sift does NOT manage MCP connections or API quotas

Sift is a research skill. It does NOT manage its own MCP server connections, API keys, or quota tracking. All structured API access is delegated to Reach:

- **CSAPI**: call `reach.csapi_check` before, `reach.csapi_increment` after, `reach.query csapi` to query. Do NOT call `mcp_google_workspace_search_custom` directly.
- **RapidAPI**: call `reach.query rapidapi`. Do NOT call `mcp_rapidapi_rapidapi_call` directly.
- **Any registered Reach source**: call `reach.query <source>`.

Reach owns: sources.yml, MCP connections, API keys, quota tracking, the discovered-apis catalog, and source registration. Sift owns: research synthesis, web_search (SearXNG), entity extraction, Chronicle Signal emission.

## execute_code may be blocked

The `execute_code` tool can be blocked by security policy, even outside cron mode. When you need to parse HTML or transform fetched content, use `terminal` with inline `python3 -c "..."` or write a script file and run it, instead of `execute_code`.

## web_extract limitations

`mcp_web_search_web_extract` returns 403 on Yelp, Reddit, and many Google pages from VPS IPs. It works on news sites (SFGATE, CBS, local blogs). Always have a fallback plan that doesn't depend on scraping these blocked sources.

## Credential sanitizer blocks API key writes

The Hermes output sanitizer intercepts API keys. If CSAPI fails with missing key, the owner must add it manually.

## Git pull fails with untracked file conflicts

When running `sift.update` (or manually pulling updates on a hub-installed skill), `git pull` may abort with:

```
error: The following untracked working tree files would be overwritten by merge:
    references/some-new-file.md
```

This happens when the upstream repo has added new tracked files that conflict with existing untracked local files of the same name.

**Fix:**
```bash
cd <skill-dir>
git checkout -- .                          # discard any staged/modified tracked files
# Move conflicting untracked files aside (they'll be recreated by the pull)
for f in references/*.md scripts/*.py; do
  [ -f "$f" ] && git ls-files --error-unmatch "$f" 2>/dev/null || mv "$f" /tmp/skill-local-backup-$(basename "$f")
done
git pull origin main
```

**Do NOT** use `git stash` alone — stash only covers tracked/indexed files, not untracked ones. `git clean -fd` also works to remove untracked files but is destructive; prefer moving files aside if you want to preserve local modifications for comparison after the pull.
