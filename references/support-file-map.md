# Support File Index

One line per bundled file that SKILL.md does not cover inline. Read entries relevant to your task before assuming a file or tool does not exist.

| File | When to read |
|------|--------------|
| `references/browser-engines.md` | Before tuning which browser engine webwright uses (Obscura / system Chrome) |
| `references/csapi-quota.md` | Before touching CSAPI quota state or key setup |
| `references/d3-graph-pitfalls.md` | When building D3 force-graph visualizations from research output |
| `references/ddg_html_fallback.md` | As a last-resort no-key search when SearXNG and CSAPI are both unavailable |
| `references/donsetch-integration.md` | Before escalating past `sift.fetch` to donsetch |
| `references/dye-transfer-fabric-guide.md` | When researching dye transfer, color run, or stain removal from clothes |
| `references/escalation-pattern.md` | When a fetch hits a bot-wall or challenge page |
| `references/exhaustive-research-methodology.md` | When the user asks for exhaustive / full-content research |
| `references/fetch-behavior.md` | Before debugging `sift.fetch` output quality or fallback thresholds |
| `references/interfaces.md` | When wiring Signal emission or inter-skill cooperation (Chronicle, Thread) |
| `references/journal-example.md` | When you need a worked `entities_observed` journal example |
| `references/journal.md` | Before `sift.journal`; at the end of every run |
| `references/local-business-search.md` | When searching for local businesses, services, or venues |
| `references/mcp-redirect-pattern.md` | When tracing how `web_search`/`web_extract` route to SearXNG |
| `references/pitfalls.md` | Before research runs — full pitfall list |
| `references/plans/research-deep-dive.plan.md` | When running a deep-dive plan (broad scan → depth pass → entity extraction) |
| `references/primary_source_research.md` | When web search fails and you need API-based primary sources |
| `references/query_rewrite.md` | Before query rewriting |
| `references/research-pipeline.md` | When tracing the research pipeline end to end |
| `references/research-workflow.md` | When executing research sessions from cloud environments |
| `references/schemas.md` | Before creating sessions, threads, or extraction records |
| `references/search-tiers-inline.md` | For the condensed inline tier summary |
| `references/search_tiers.md` | Before tier selection; provider keys and the SearXNG engine-health probe |
| `references/searxng-plugin-setup.md` | When setting up or repairing the SearXNG plugin |
| `references/support-file-map.md` | This index |
| `references/user-relevance.md` | Before tagging Signals `"user"` vs `"agent_only"` |
| `references/wayback_fallback.md` | Before relying on archived content; explains staleness marking |
| `references/webwright-integration.md` | Before `sift.webwright` |
| `references/x_discovery.md` | When researching public X/Twitter content without auth |
| `scripts/csapi_quota.py` | Standalone CSAPI monthly counter (check/increment/status/remaining) |
| `scripts/wayback_fallback.py` | Recovery-only Wayback fetch for hard-blocked URLs |
| `scripts/webwright_runner.py` | CLI runner for webwright tasks (`python3 webwright_runner.py "task" [--start-url URL]`) |
| `tests/test_smoke.py` | When changing scripts — `python3 -m unittest discover -s tests` |
