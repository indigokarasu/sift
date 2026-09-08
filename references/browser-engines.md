# Browser engines

Webwright's generated scripts call `launch_browser(p)` instead of launching a
browser directly, so the engine is chosen at run time.

| `OBSCURA_ENGINE` | Behaviour |
|---|---|
| `auto` (default) | Connect to Obscura over CDP; fall back to system Chrome if it is unreachable |
| `obscura` | Require Obscura — fail loudly rather than silently changing engine |
| `chrome` | Always use system Chrome |

`OBSCURA_CDP` overrides the endpoint (default `http://127.0.0.1:9222`).

## Why Obscura is preferred

Obscura is a headless browser engine written in Rust with anti-detect built
in. It speaks the Chrome DevTools Protocol, so Playwright drives it through
`connect_over_cdp()` with no other code change.

It matters here because headless Chrome is visibly headless: pages that gate
automation return a stub. Measured on the same host, same URLs, same moment:

| Page | Obscura | headless Chrome |
|---|---|---|
| Google search | 1254 chars of text | 336 |
| Bing search | 96590 | 2328 |
| Hacker News | 40107 ARIA chars | 40107 (identical) |

Resident memory is roughly 30 MB against 200-400 MB for Chrome, which is what
makes concurrent runs affordable on a small host.

Verified compatible with what webwright depends on: `new_context(viewport=…)`
is honoured, `locator.aria_snapshot()` returns the same content Chrome does,
and `browser.close()` disconnects without stopping the shared server.

## Reading a run

The exploration phase prints two lines worth checking:

```
ENGINE: obscura
RENDERED: aria_chars=40214 painted=True
```

`painted` is computed from the screenshot's distinct colour count, not its
file size — a flat image is an unpainted page regardless of how many bytes it
occupies, and a large blank PNG has been mistaken for success before.

## When to force `chrome`

Obscura renders with its own engine rather than Chromium, so its screenshots
are visually simpler (fewer distinct colours: 331 vs 1201 on example.com).
For scraping, ARIA extraction and agent navigation this is irrelevant. For
pixel-comparison work against a real Chrome baseline, set
`OBSCURA_ENGINE=chrome`.
