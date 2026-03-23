# 🔬 Sift

Web search, research synthesis, fact verification, and entity extraction.

**Skill name:** `ocas-sift`
**Version:** 2.2.0
**Type:** system
**Layer:** Signal
**Author:** Indigo Karasu

---

## Files

| File | Purpose |
|---|---|
| `skill.json` | Package metadata and routing description |
| `SKILL.md` | Operational instructions for the agent |
| `references/` | Support files referenced by SKILL.md |

---

## Changelog

### 2.2.0 (2026-03-22)

- Added short-name routing aliases to skill.json description and SKILL.md frontmatter for natural invocation ('Scout', 'Sift', etc.)
- Added trigger phrases to descriptions for improved routing accuracy
- Cross-skill references in descriptions now use 'use X' format for routing clarity

### 2.1.0 (2026-03-22)

- Added Run completion section with explicit signal emission and journal write steps
- Signal emission now mandatory for extracted entities with confidence >= med
- Added Initialization section with storage bootstrap and Elephas intake directory creation
- Removed non-conformant OCAS_ROOT environment variable reference
- Changed signal emission language from permissive to directive

### 2.0.0 (2026-03-18)

- Initial build of all OCAS skills as a unified suite
