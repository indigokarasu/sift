## 2026-04-13 - Pre-lowercasing String Collections & O(N) Max Scan
**Learning:** Lowercasing string collections inside nested loop generator expressions (`any(tag in s.lower() for s in items)`) causes redundant string lowercasing allocations. Pre-lowercasing the collection and search target once outside iteration yields ~2x speedups. Additionally, linear numeric extraction (`max()`) on directory sequence names is faster O(N) than `sorted()` and avoids lexicographical ordering bugs (`run_10` vs `run_2`).
**Action:** Pre-transform string collections outside verification loops and use max numeric extraction over string sorting for sequence IDs.

## 2026-04-13 - Python re.sub Caching vs Redundant File I/O Loop Optimization
**Learning:** Python's standard `re.sub` module caches up to 512 compiled regex patterns internally (`re._cache`), making manual `re.compile()` pre-compilation yield minimal (< 1%) speedups for string substitutions. In contrast, batching file persistence operations (`save_state()`) outside iteration loops and caching dict lookups yields significant efficiency gains by avoiding redundant disk I/O and JSON serialization.
**Action:** Focus I/O optimizations on batching disk persistence outside iteration loops rather than micro-optimizing cached standard library regex patterns.

## 2026-04-13 - Top-Level Optional Dependency Import Caching
**Learning:** Attempting `import <optional_pkg>` inside a hot function path when the package is missing causes expensive `sys.path` module resolution lookups and `ImportError` exceptions on every call (~500x slower). Caching optional module imports at top level (`try: import ... except ImportError: pkg = None`) resolves package availability once at startup.
**Action:** Move optional module imports to top level and check `if pkg is not None:` inside function calls rather than re-importing in function scope.

## 2026-04-13 - Prefix Slicing for Block Pattern Detection & Explicit Encoding Fast Paths
**Learning:** Lowercasing multi-megabyte string payloads for substring pattern matching (`html.lower()`) allocates large intermediate copies in memory. Since block error messages (e.g. Wayback interstitials) reside in response headers or the top of document markup (<64KB), slicing the prefix (`html[:65536].lower()`) avoids multi-megabyte allocations and achieves ~36x speedups. Additionally, fast-pathing explicit `identity` content encodings avoids redundant string lowercasing and substring checks (~2.4x speedup).
**Action:** Use prefix slicing when checking error patterns on potentially large string documents and add fast paths for identity encodings.

## 2026-04-13 - Fast Directory Iteration via os.scandir and EAFP
**Learning:** `Path.glob()` and `Path.exists()` instantiate full `Path` objects for every matching entry and perform redundant filesystem `stat` system calls. Replacing `Path.glob()` and `Path.exists()` with `os.scandir()` and `try...except FileNotFoundError` yields ~4.2x speedups during run sequence lookups and file verification in directory trees.
**Action:** Prefer `os.scandir()` and `try...except FileNotFoundError` over `Path.glob()` / `.exists()` when scanning large directory structures in Python.

## 2026-04-13 - Length Guard Short-Circuiting for Pattern Matching
**Learning:** Lowercasing multi-KB page snapshots and pattern matching against string tuples before checking length requirements causes wasted allocation and string scanning on normal pages. Evaluating cheap numeric length guards (`body_chars < 2000`) before string lowercasing and pattern searching completely bypasses string operations for normal rendered content (~760x speedup).
**Action:** Place cheap size/length guards before expensive string lowercasing and multi-pattern searches when both conditions are required.

## 2026-04-13 - Pre-Joined String Delimitation for Batch Substring Searches
**Learning:** Evaluating generator expressions with substring checks over list collections (`any(tag in s for s in list)`) inside outer iteration loops causes O(M * N) list traversals and generator allocations. Joining string collections into a single newline-delimited text blob (`"\n".join(items)`) outside the outer loop reduces verification checks to fast C-level string containment checks (`tag in joined_text`), yielding ~1.8x speedups.
**Action:** Pre-join string collections with newlines when checking substring membership across multi-item lists in verification loops.

## 2026-04-13 - Combined Regex Passes & Fast-Path Line Normalization
**Learning:** Sequential string replacement regexes (`re.sub`) over HTML documents cause redundant multi-megabyte string scans. Combining block tag and `<br>` replacement regexes into a single pass (`(?i)(?:</(?:block_tags)>|<br\s*/?>)`) reduces regex engine passes. Additionally, guarding line whitespace normalization with cheap containment checks (`"  " in s or "\t" in s`) before calling `s.split()` avoids list allocations on clean lines (~1.16x speedup).
**Action:** Combine sequential replacement regexes into single-pass patterns and guard string split/join normalizations with cheap substring checks.

## 2026-04-13 - Post-Join Batch String Lowercasing
**Learning:** Lowercasing list items via generator expressions before joining (`"\n".join(s.lower() for s in items)`) incurs generator evaluation overhead and per-string function calls. Joining items first and calling `.lower()` once on the joined string (`"\n".join(items).lower()`) shifts string lowercasing into C-level standard library execution, yielding ~3.3x speedups.
**Action:** Join string sequences before applying uniform string lowercasing transformations when preparing text blobs for pattern search.

## 2026-04-13 - Inline Blank-Line Collapsing & Post-Pass Regex Elimination
**Learning:** Appending empty line strings for every blank line during HTML line iteration creates large lists with thousands of redundant empty string objects and requires a post-join regular expression pass (`re.sub(r"\n{3,}", "\n\n", html)`). Capping consecutive blank lines inline (`blank_count <= 1`) during iteration prevents triple newlines (`\n\n\n`) from ever being constructed, eliminating peak memory allocations for redundant string objects and avoiding post-pass regex scans entirely (~1.15x–1.23x speedup).
**Action:** Collapse consecutive delimiter lines inline during split iteration to prevent over-generation and eliminate downstream regex cleanup passes.
