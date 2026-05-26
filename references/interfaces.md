# Sift — Chronicle Interaction & Inter-Skill Interfaces

Sift never writes directly to Chronicle. It emits enrichment candidates via Signal files to the `signal` payload field in the journal entry. Elephas decides promotion.

## Inter-skill interfaces

Sift writes Signal files to Elephas (via journal signal payload): the `signal` payload field in the journal entry

Every Signal must include the `user_relevance` field (`"user"` or `"agent_only"`). Elephas decides promotion.

Sift may read from Thread (when present) for recent browsing context to improve query rewriting. This is a cooperative read, not a dependency.

See `spec-ocas-interfaces.md` for signal format.
