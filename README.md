# ⚙️ Sift

  <img src="./assets/readme/hero.jpg" width="100%" alt="Sift">

Web search, research synthesis, fact verification, entity extraction, and URL content extraction — the system's general research engine. Use for any task requiring current web information. Do not use for person-focused OSINT (use Scout), image processing (use Look), knowledge-graph pattern analysis (use Corvus), or comms drafting (use Dispatch).

**Skill name:** `ocas-sift`
**Version:** 2.9.4
**Type:**
**Layer:** Execution
**Author:** Indigo Karasu

---

## 📖 Overview

Tiered web search (SearXNG first, CSAPI/RapidAPI fallback via Reach), multi-source synthesis, fact verification, and structured entity extraction. Sift scores source reliability by cross-source agreement and emits enrichment candidates to Chronicle as Signals.

---

## 🔧 Capabilities

- `sift.search` — execute a search query with automatic tier selection and query rewriting
- `sift.research` — run a multi-source research session producing a structured research journal
- `sift.verify` — fact-check a specific claim across multiple sources with consensus scoring
- `sift.summarize` — summarize a document or URL with structured entity extraction
- `sift.extract` — extract entities, claims, statistics, and relationships from content
- `sift.thread.list` — list active research threads with entity overlap detection
- `sift.status` — return current state: active threads, quota usage, source reputation summary
- `sift.journal` — write journal for the current run; called at end of every run
- `sift.fetch [url]` — extract clean Markdown from a URL (Scrapling → Jina Reader → clean failure)
- `donsetch fetch [url]` — anti-bot fetch (real Chrome TLS / solve-and-bounce) when `sift.fetch` hits a bot-wall
- `sift.webwright` — interactive browser task (Playwright; system Chrome via `channel="chrome"`); read `references/webwright-integration.md` before first use

Signals carry `user_relevance`: `"user"` when the run was user-initiated or the entity connects to an existing user-linked Chronicle entry, `"agent_only"` otherwise.

---

## 📊 Outputs

See `SKILL.md` for outputs, journals, and persistence rules.

---

## 📄 Files

| File | Purpose |
|---|---|
| `SKILL.md` | Skill definition |
| `references/` | Supporting documentation |
| `scripts/` | Helper scripts |

---

## Changelog

Recent entries — full history in [`CHANGELOG.md`](./CHANGELOG.md):

- [2.9.4] - 2026-09-24 — reference repairs, `--help` guard for `csapi_quota.py`, Reach quota delegation, SKILL.md restructure
- [2.8.5] - 2026-04-12 — `sift.fetch` content-density check; search tier deduplication
- [2026-04-05] — N2 MCP registration + URL content fetcher

---

## 📚 Documentation

Read `SKILL.md` for operational details, schemas, and validation rules.

Read `references/` for detailed specifications and examples.

---

## 📄 License

MIT License — see `LICENSE` for details.
