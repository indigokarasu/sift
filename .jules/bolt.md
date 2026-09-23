## 2026-04-13 - Pre-lowercasing String Collections & O(N) Max Scan
**Learning:** Lowercasing string collections inside nested loop generator expressions (`any(tag in s.lower() for s in items)`) causes redundant string lowercasing allocations. Pre-lowercasing the collection and search target once outside iteration yields ~2x speedups. Additionally, linear numeric extraction (`max()`) on directory sequence names is faster O(N) than `sorted()` and avoids lexicographical ordering bugs (`run_10` vs `run_2`).
**Action:** Pre-transform string collections outside verification loops and use max numeric extraction over string sorting for sequence IDs.

## 2026-04-13 - Python re.sub Caching vs Redundant File I/O Loop Optimization
**Learning:** Python's standard `re.sub` module caches up to 512 compiled regex patterns internally (`re._cache`), making manual `re.compile()` pre-compilation yield minimal (< 1%) speedups for string substitutions. In contrast, batching file persistence operations (`save_state()`) outside iteration loops and caching dict lookups yields significant efficiency gains by avoiding redundant disk I/O and JSON serialization.
**Action:** Focus I/O optimizations on batching disk persistence outside iteration loops rather than micro-optimizing cached standard library regex patterns.

## 2026-04-13 - Top-Level Optional Dependency Import Caching
**Learning:** Attempting `import <optional_pkg>` inside a hot function path when the package is missing causes expensive `sys.path` module resolution lookups and `ImportError` exceptions on every call (~500x slower). Caching optional module imports at top level (`try: import ... except ImportError: pkg = None`) resolves package availability once at startup.
**Action:** Move optional module imports to top level and check `if pkg is not None:` inside function calls rather than re-importing in function scope.
