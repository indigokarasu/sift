# 🔍 Sift

Sift conducts multi-source web research and synthesis. It searches, fact-checks claims against multiple sources, extracts entities and relationships, and maintains research threads. Sift separates signal from noise through consensus scoring and source reputation modeling. Every fact-check is auditable with source agreement metrics.

---

## 📖 Overview

Web search, research synthesis, fact verification, and entity extraction. Separates signal from noise across the open web.

---

## 🔧 Tool Surface

- `sift.research` — run multi-source research session producing structured journal
- `sift.verify` — fact-check claim across sources with consensus scoring
- `sift.summarize` — summarize document/URL with entity extraction
- `sift.extract` — extract entities, claims, statistics, relationships from content
- `sift.thread.list` — active research threads with entity overlap detection
- `sift.sources.reputation` — per-domain trust scores and historical accuracy
- `sift.status` — active threads, quota usage, source reputation summary

---

## 📊 Output & Journals

Produces: Produces research session journals, fact-check reports with consensus scores, and entity extraction records.

---

## ⏱️ Heartbeat & Background Tasks

**Periodic Quota Monitoring & Source Updates**: Sift monitors research quota, updates source reputation scores based on recent accuracy, and escalates between tier 2 (default) and tier 3 (deep research) based on result sufficiency.

---

## 📚 Documentation

Read `SKILL.md` for operational details, schemas, and validation rules.

See `references/` for detailed specifications and examples.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
