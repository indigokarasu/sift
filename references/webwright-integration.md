# Webwright Integration — SearchX Stack

## What Webwright adds to SearchX

The SearchX stack (Sift) handles search and content extraction well. Webwright
fills the gap for **interactive web tasks** that require browser state:

| Capability | Sift (current) | Webwright (new) |
|---|---|---|
| Search for information | Yes | No |
| Extract content from a URL | Yes (sift.fetch) | No |
| Fill out a form | No | Yes |
| Click through a multi-step flow | No | Yes |
| JS-heavy site interaction | Partial (Scrapling) | Yes (Playwright Firefox) |
| Verify filters applied correctly | No | Yes (screenshot evidence) |
| Parameterized reusable scripts | No | Yes (CLI tool mode) |

## Architecture

```
User request
    │
    ├── "search for X" / "look up Y" / "summarize this URL"
    │       └── sift.search / sift.fetch
    │
    └── "do this web task" / "fill out this form" / "click through X"
            └── sift.webwright
                    └── Webwright skill (microsoft/Webwright)
                            └── Playwright Firefox (local, headless)
```

## When to route to Webwright

Route to `sift.webwright` when the user asks to:

- Fill out a form on a specific website
- Complete a multi-step web workflow (sign up, configure, purchase)
- Interact with a JS-heavy site that Scrapling can't handle
- Verify that a filter/feature exists on a page and capture evidence
- Extract data that requires clicking through pagination or tabs
- Any task where the browser itself is the workspace, not just a content source

**Do NOT route to Webwright**:
- Simple lookups → use `sift.search`
- URL content extraction → use `sift.fetch`
- Person/company OSINT → use Scout

## Workspace contract

Webwright runs write to an isolated workspace under
`{agent_root}/commons/data/ocas-sift/webwright/`:

```
webwright/
  plan.md               ← critical points checklist
  screenshots/          ← exploration scratch PNGs
  final_runs/
    run_1/
      final_script.py   ← the instrumented Playwright script
      screenshots/      ← one PNG per critical point
      final_script_log.txt
    run_2/              ← created on re-run after failure
      ...
```

Each task gets its own workspace. The workspace is disposable — only
`final_script.py` and the log are preserved long-term.

## Webwright modes

### Default (one-shot)

`sft.webwright "Fill out the contact form at example.com with name=John"`

Produces a `final_script.py` that solves the task for the literal values.
Good for one-time tasks.

### CLI tool (parameterized)

`sft.webwright.craft "Search flights from {origin} to {date}"`

Produces a reusable `argparse`-wrapped CLI where the defaults match the
original task but the user can re-run with different args later.

## Playwright configuration

- Browser: Firefox (headless=True)
- Viewport: 1280 x 1800 (never full_page screenshots)
- Each run launches a fresh browser — no persistent state
- Akamai-protected sites that reject Chromium work under Firefox

## Stealth mode

When `stealth: true` is passed to `sift.webwright`, apply these additional configurations:

- **Fingerprint randomization**: Override `navigator.webdriver`, `navigator.plugins`, `navigator.languages`, WebGL vendor/renderer strings, canvas noise
- **Stealth user-agent**: Rotate among recent Chrome/Firefox user-agents from a pool
- **Challenge detection**: After page load, check for Cloudflare/Akamai/Datadome challenge patterns (title contains "Just a moment", "Attention Required", "Access denied", or body < 200 chars with challenge HTML)
- **Auto-wait**: If challenge detected, poll every 2s until resolved (max 15s)
- **Retry with backoff**: On failure, retry up to 3 times (2s, 4s, 8s)
- **Proxy rotation**: If `PROXY_URL` is set, use it; if multiple proxies available, rotate on retry

Stealth mode adds 3-20s per request but dramatically increases success rate on protected sites. Use only when standard Webwright fails — it is not the default path.

## Safety rules

- Never install extra pip/apt packages
- Never bypass access controls
- Fail cleanly if a step can't be completed — don't guess
- Always self-verify against plan.md before claiming completion
