## [2.9.4] - 2026-09-24

### Fixed
- Repaired mangled text in `references/interfaces.md`, `references/user-relevance.md`, `references/query_rewrite.md`, `references/research-pipeline.md`, `references/plans/research-deep-dive.plan.md`, and this file: a botched backend rename had replaced the name "Elephas" with a pointer to a never-authored `references/integration-notes.md`
- `scripts/csapi_quota.py --help` now exits 0 (guard placed before any state read/write); removed a dead `if False` branch in command dispatch
- `scripts/wayback_fallback.py`: `zlib` now imported inside `_decode_body` instead of at module scope
- `tests/test_smoke.py` + CI workflow: replaced removed `scripts/update.sh` checks with `csapi_quota.py` help / unknown-command checks
- Restored `references/local-business-search.md` — local-business workflow via Reach (`reach.query rapidapi`) after the old file went missing

### Changed
- SKILL.md restructured for progressive disclosure: research-workflow checklist, Error Handling table, Gotchas, conditional "When to read" support map; CSAPI quota ownership now delegated to Reach, matching `references/pitfalls.md`
- Frontmatter: `license` moved inside the first 500 chars; `metadata.hermes` (category `research`, tags) added; version 2.9.3 → 2.9.4
- `references/escalation-pattern.md`, `references/pitfalls.md`, and `references/search_tiers.md` browser naming aligned with `references/browser-engines.md`; donsetch added as Tier 2 of the escalation chain
- `references/support-file-map.md` rebuilt as a complete index (dropped the deleted `scripts/update.sh` row, added all current references and scripts)

## [2.8.5] - 2026-04-12

### Fixed
- `sift.fetch`: added explicit content-density check — Scrapling output ≥200 words returns immediately; below threshold falls through to Jina without retrying Scrapling
- Search tier deduplication: N2 MCP is skipped when `SEARXNG_URL` is set and responding (both are SearXNG-backed; was producing duplicate results)

## [2026-04-05] N2 MCP + URL content fetcher

### Added
- N2 MCP (`npx -y n2-free-search`) registered during `sift.init` — free SearXNG-backed search across 70+ engines, no API key required. Replaces DuckDuckGo as zero-credential fallback; also adds `n2_news_search` for recency-focused queries.
- `sift.fetch [url]` — extract clean Markdown from a specific URL. Scrapling (fast/headless) → Jina Reader fallback → clean failure. New `## sift.fetch behavior` section documents the pipeline.
- `sift.init` steps 8–9: N2 MCP registration and Scrapling installation

### Changed
- Search source description updated: all configured sources fire in parallel (no sequential tier escalation for Tier 2)
- `description` in skill.json updated to include URL content extraction as a trigger case

### Validation
- ✓ Version: 2.6.1 → 2.7.0

## [2026-04-04] Spec Compliance Update

### Changes
- Added missing SKILL.md sections per ocas-skill-authoring-rules.md
- Updated skill.json with required metadata fields
- Ensured all storage layouts and journal paths are properly declared
- Aligned ontology and background task declarations with spec-ocas-ontology.md

### Validation
- ✓ All required SKILL.md sections present
- ✓ All skill.json fields complete
- ✓ Storage layout properly declared
- ✓ Journal output paths configured
- ✓ Version: 2.6.0 → 2.6.1

## [2.8.1] - 2026-04-08

### Storage Architecture Update

- Replaced $OCAS_DATA_ROOT variable with platform-native {agent_root}/commons/ convention
- Replaced intake directory pattern with journal payload convention
- Added errors/ as universal storage root alongside journals/
- Inter-skill communication now flows through typed journal payload fields
- No invented environment variables — skills ask the agent for its root directory


## [2.8.0] - 2026-04-08

### Multi-Platform Compatibility Migration

- Adopted agentskills.io open standard for skill packaging
- Replaced skill.json with YAML frontmatter in SKILL.md
- Replaced hardcoded ~/openclaw/ paths with {agent_root}/commons/ for platform portability
- Abstracted cron/heartbeat registration to declarative metadata pattern
- Added metadata.hermes and metadata.openclaw extension points
- Compatible with both OpenClaw and Hermes Agent


## [2.6.0] - 2026-04-02

### Added
- Tier 2 parallel platform search via agent-reach: Twitter/X, Reddit, LinkedIn, GitHub, Weibo, WeChat Articles, Bilibili, XiaoHongShu, YouTube, V2EX, Xueqiu, RSS feeds
- Deduplication by URL and content hash for merged web + platform results
- search_tiers.md updated with parallel execution model and fallback behavior

## [2.5.0] - 2026-04-02

### Added
- `user_relevance` field on all emitted Chronicle signals (default `agent_only` for research, `user` when user-requested)
- Structured entity observations in journal payloads (`entities_observed` with relevance tags)

## 2.4.0 — 2026-03-30

### Added
- `references/plans/research-deep-dive.plan.md` — bundled workflow plan: broad scan → depth pass → entity extraction
- Ontology mapping: Sift extracts Person/AI, Place, Event/Idea, DigitalArtifact types

### Changed
- Thread and Weave cooperative interfaces now reference `spec-ocas-interfaces.md` Cooperative Query Interfaces

## Prior

See git log for earlier history.
