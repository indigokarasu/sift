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
