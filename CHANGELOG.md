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

# CHANGELOG

## [2.6.0] - 2026-04-02

### Added
- Tier 2 parallel platform search via agent-reach: Twitter/X, Reddit, LinkedIn, GitHub, Weibo, WeChat Articles, Bilibili, XiaoHongShu, YouTube, V2EX, Xueqiu, RSS feeds
- Deduplication by URL and content hash for merged web + platform results
- search_tiers.md updated with parallel execution model and fallback behavior

## [2.5.0] - 2026-04-02

### Added
- `user_relevance` field on all emitted Elephas signals (default `agent_only` for research, `user` when user-requested)
- Structured entity observations in journal payloads (`entities_observed` with relevance tags)

## 2.4.0 — 2026-03-30

### Added
- `references/plans/research-deep-dive.plan.md` — bundled workflow plan: broad scan → depth pass → entity extraction
- Ontology mapping: Sift extracts Person/AI, Place, Event/Idea, DigitalArtifact types

### Changed
- Thread and Weave cooperative interfaces now reference `spec-ocas-interfaces.md` Cooperative Query Interfaces

## Prior

See git log for earlier history.
