
# build.ocas-sift.v1.1.0.md

## Skill Metadata
name: Sift
skill_id: ocas-sift
version: 1.1.0
category: research
public: true
description: Web search, research, fact-checking, and summarization skill that separates signal from noise across the open web.

author: Indigo Karasu
email: mx.indigo.karasu@gmail.com

principle: |
  Sift retrieves information from the web, evaluates reliability across multiple sources,
  extracts structured knowledge, and produces clear answers and research artifacts.
  It can cooperate with other OCAS skills when present but must function independently.

---

## Responsibility Boundary

Sift specializes in topic research, fact discovery, and general web knowledge.

Scout specializes in investigative intelligence about people and organizations.

If the primary entity of a query is a person, Scout should be invoked.

Sift never performs OSINT investigations on individuals.

Person-focused investigations belong to Scout.

---

# Purpose

Sift performs web discovery and research for the system owner.
It converts vague questions into precise search queries, gathers sources, extracts structured information, evaluates consensus, and produces reliable answers or summaries.

Sift must remain:

• fast
• accurate
• free to operate (using free APIs or free tiers)
• compatible with the OCAS ecosystem but not dependent on it

---

# Core Responsibilities

1. Web search
2. Research synthesis
3. Fact verification
4. Document summarization
5. Structured entity extraction
6. Source reliability evaluation
7. Research journaling

---

# Search Tiers

## Tier 1 – Internal Knowledge

Uses:
• LLM knowledge
• current conversation context
• Chronicle context if available

Purpose:
Very fast answers that do not require external search.

---

## Tier 2 – Free Web Search

Providers (priority order):

• Brave Search API
• SearXNG instance
• DuckDuckGo

Purpose:
Standard research queries.

---

## Tier 3 – Semantic Research (quota limited)

Providers:

• Exa
• Tavily

Used only when:

• deep research is required
• sources are sparse
• semantic retrieval improves accuracy

Quota monitoring is performed by a periodic heartbeat.

---

# Query Rewrite System

Sift rewrites vague queries into explicit search queries using:

• conversation context
• geolocation if available
• Chronicle data if installed
• entity resolution from prior messages

Example

User query:
"best ramen near me"

Rewrite:

ramen restaurants San Francisco reviews
site:eater.com ramen san francisco
site:yelp.com ramen san francisco

---

# Response Modes

Sift automatically classifies query depth.

Modes:

quick_answer
comparison
research
document_analysis

Users may override by writing phrases like:

quick answer
deep dive
compare
summarize

---

# Structured Extraction

When pages are retrieved Sift extracts:

entities
claims
statistics
relationships
citations

Example extraction:

entity: LadybugDB
type: Thing
relationship: fork_of -> Kuzu
confidence: high

---

# Source Reputation Model

Sift maintains a reputation score for domains.

Signals:

• cross-source agreement
• contradiction frequency
• historical accuracy
• structured data quality
• citation frequency

Example:

domain: ladybugdb.com
trust_score: 0.82

Chronicle preferred sources (if available) influence ranking.

---

# Research Sessions

Each search interaction produces a session journal.

Example:

search_session_journal

query:
best embedded graph database

entities:

Thing:
LadybugDB
Neo4j

Concept:
graph database
embedded database

sources:
ladybugdb.com
neo4j.com

provider_telemetry:

brave:
latency_ms: 380
results_used: 3

searxng:
latency_ms: 1100
results_used: 2

---

# Research Threads

Sessions may merge into long-term research threads when entity overlap is detected.

Example:

thread_topic:
graph databases

entities:
LadybugDB
Kuzu
graph database

sessions:
session_001
session_007

---

# Chronicle Interaction

Sift never writes directly to Chronicle.

Instead it emits enrichment candidates.

Example:

candidate_entity:
natuRe Waikiki
type: Place
confidence: medium

Elephas may decide to store the record.

---

## Optional Skill Cooperation

Sift may leverage other OCAS skills if installed.

Examples:

Weave – entity disambiguation
Taste – preference signals in local search
Corvus – curiosity pattern detection
Elephas – Chronicle enrichment evaluation
Praxis – action execution based on research

However Sift must function normally even when these skills are absent.

---

# Local Search Support

Vertical search patterns include:

Google Maps
Yelp
Doordash
Instacart
OpenTable
Tock
Zocdoc

Local media:

Eater
SFist
Honolulu Magazine

---

# Specialized Search Domains

Technical research

GitHub
StackOverflow
arXiv
Google Patents

Product comparison

retail listings
manufacturer sites
review aggregators

---

# URL and Domain-Scoped Queries

If a user provides a URL:

• retrieve page
• perform structured extraction
• summarize content

If the user specifies a domain:

Example

site:arxiv.org graph database

Sift restricts search scope to that domain.

---

# Performance Telemetry

Each session journal records:

provider latency
results usefulness
entity extraction success

Mentor may analyze these records and propose improvements.

---

# Design Constraints

Sift must:

• operate using free search sources
• remain fast for normal queries
• escalate to deeper research only when needed
• never directly modify Chronicle
• produce research journals for system learning

---

## Skill Identity

- Skill name: `ocas-sift`
- Version: `1.1.0`
- Skill type: `system`
- Author: `Indigo Karasu`
- Email: `mx.indigo.karasu@gmail.com`

---

## Journal Outputs

This skill emits the following journal types as defined in the OCAS Journal Specification (spec-ocas-Journals.md):

- Observation Journal
- Research Journal

Sift emits Observation Journal entries for entity and claim extraction and Research Journal entries for completed search sessions with source and provider telemetry.

---

## Visibility

visibility: public

---

## Universal OKRs

This skill must implement the universal OKRs defined in the OCAS Journal Specification (spec-ocas-Journals.md).

Required universal OKRs:

- Reliability: success_rate >= 0.95, retry_rate <= 0.10
- Validation Integrity: validation_failure_rate <= 0.05
- Efficiency: latency trending downward, repair_events <= 0.05
- Context Stability: context_utilization <= 0.70
- Observability: journal_completeness = 1.0

Skill-specific OKRs should be defined in the built SKILL.md to measure domain-relevant outcomes.

---

## Required Package Output

Forge must produce a complete Agent Skill package:

```text
ocas-sift/
  skill.json
  SKILL.md
  references/
    schemas.md
    search_tiers.md
    query_rewrite.md
```

### `skill.json` Requirements

Create a valid `skill.json` with:
- `name`: `ocas-sift`
- `version`: `1.1.0`
- `description`: routing-optimized text
- `author`: `Indigo Karasu`
- `email`: `mx.indigo.karasu@gmail.com`

The description must make clear that this skill is for:
- web search and research synthesis
- fact verification across multiple sources
- document summarization and entity extraction
- source reliability evaluation
- topic research, not person-focused OSINT

### `SKILL.md` Requirements

`SKILL.md` must begin on line 1 with valid YAML frontmatter delimited by `---`.

Target size: 180 to 280 lines.

#### Required `SKILL.md` Sections

The markdown body must contain these sections in this order:

1. `# Sift`
2. `## When to use`
3. `## When not to use`
4. `## Core promise`
5. `## Commands`
6. `## Response modes`
7. `## Search tier selection`
8. `## Source reputation model`
9. `## Structured extraction rules`
10. `## Chronicle interaction`
11. `## Support file map`
12. `## Storage layout`
13. `## Validation rules`

### Commands

The built skill must implement these commands:

- `sift.search` — execute a search query with automatic tier selection and query rewriting
- `sift.research` — run a multi-source research session on a topic, producing a structured research journal
- `sift.verify` — fact-check a specific claim across multiple sources with consensus scoring
- `sift.summarize` — summarize a document or URL with structured entity extraction
- `sift.extract` — extract structured entities, claims, statistics, and relationships from provided content
- `sift.thread.list` — list active research threads with entity overlap detection
- `sift.status` — return current state including active threads, quota usage, and source reputation summary

### Storage Layout

```text
.sift/
  config.json
  sessions.jsonl
  threads.jsonl
  entities.jsonl
  sources.jsonl
  decisions.jsonl
  reports/
```

### Config

File: `.sift/config.json`

Required fields:
- `search.default_tier`: default search tier (1 or 2)
- `search.tier3_enabled`: whether semantic research providers are enabled (default false)
- `quota.tier3_daily_limit`: daily quota for Tier 3 providers
- `reputation.min_trust_score`: minimum trust score for source inclusion
- `extraction.confidence_threshold`: minimum confidence for entity extraction
- `chronicle.emit_candidates`: whether to emit enrichment candidates to Elephas (default true)

### `references/schemas.md`

Must define schemas for:
- `SearchQuery` — query_id, original_query, rewritten_queries, tier, context
- `SearchSession` — session_id, query, provider_telemetry, results, entities_extracted, sources_used
- `ResearchThread` — thread_id, topic, entity_overlap, session_ids, status
- `ExtractedEntity` — entity_id, name, type (Entity|Place|Concept|Thing), relationships, confidence, source_refs
- `SourceReputation` — domain, trust_score, agreement_rate, contradiction_rate, last_updated
- `EnrichmentCandidate` — candidate_entity, type, confidence, source_refs
- `DecisionRecord` — decision_id, decision_type, evidence_refs, outcome, timestamp

### `references/search_tiers.md`

Must explain:
- Tier 1 (internal knowledge): when to use, what sources
- Tier 2 (free web search): provider priority order (Brave, SearXNG, DuckDuckGo), standard usage
- Tier 3 (semantic research): providers (Exa, Tavily), when to escalate, quota monitoring
- escalation criteria between tiers
- provider latency tracking and fallback behavior

### `references/query_rewrite.md`

Must explain:
- how vague queries are expanded using conversation context, geolocation, Chronicle data, and entity resolution
- concrete rewrite examples
- domain-scoped query patterns (site: syntax)
- local search vertical patterns (Maps, Yelp, OpenTable, etc.)
- URL-provided content handling

# End State

Sift acts as the system's information filter.

It retrieves web information, separates signal from noise, extracts structured knowledge, and produces reliable answers usable by both the user and other OCAS skills.

---

## Final Response Format for the Coder

Return:

1. package tree
2. full contents of every file
3. brief validation summary

Do not return planning commentary, process narration, or references to absent documents.
