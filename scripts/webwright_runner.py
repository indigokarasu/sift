#!/usr/bin/env python3
"""
Webwright runner for OCAS-Sift.

Usage:
    python webwright_runner.py "task description" [--start-url URL] [--workspace PATH] [--craft]

This script implements the Webwright workflow as a Hermes-compatible tool:
1. Plan      → write plan.md with critical points
2. Explore   → run scratch Playwright scripts, save screenshots
3. Author    → write instrumented final_script.py
4. Execute   → run final_script.py
5. Verify   → check screenshots + log against plan.md

No API keys required — uses native Playwright.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def next_run_id(workspace: Path) -> int:
    existing = sorted(workspace.glob("final_runs/run_*"))
    if not existing:
        return 1
    last = existing[-1].name  # e.g. "run_3"
    n = int(last.split("_")[1])
    return n + 1


def ensure_workspace(base: Path, task_id: str) -> Path:
    ws = base / task_id
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "screenshots").mkdir(exist_ok=True)
    return ws


def write_plan(ws: Path, task: str, critical_points: list[str]) -> Path:
    plan_path = ws / "plan.md"
    lines = [f"# Task\n{task}\n", "\n# Critical Points"]
    for i, cp in enumerate(critical_points, 1):
        lines.append(f"- [ ] CP{i}: {cp}")
    plan_path.write_text("\n".join(lines) + "\n")
    return plan_path


def generate_exploration_script(start_url: str, workspace: Path) -> str:
    # NOTE: do not use str.format() here. The generated code contains literal
    # braces (viewport={"width": ...}) which format() reads as replacement
    # fields — that raised KeyError: '"width"' on every single invocation and
    # the runner never reached Playwright. Substitute an explicit placeholder
    # instead, so the emitted script may contain arbitrary Python.
    template = r"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

WORKSPACE = Path("__WORKSPACE__")
SCREENSHOTS = WORKSPACE / "screenshots"

async def explore():
    async with async_playwright() as p:
        # Use the system Chrome already present on the host. The bundled
        # chromium revision in the local cache does not match this playwright
        # build, and firefox was never downloaded at all, so channel="chrome"
        # avoids fetching a browser purely to run a page. --no-sandbox is
        # needed when running as root.
        browser = await p.chromium.launch(
            headless=True, channel="chrome", args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 1280, "height": 1800})
        page = await ctx.new_page()
        await page.goto("__START_URL__", wait_until="domcontentloaded")
        SCREENSHOTS.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(SCREENSHOTS / "explore_1_start.png"))
        print("URL:", page.url)
        print("TITLE:", await page.title())
        snap = await page.locator("body").aria_snapshot()
        print("ARIA:", snap[:2000])
        await browser.close()

asyncio.run(explore())
"""
    return (template
            .replace("__START_URL__", start_url)
            .replace("__WORKSPACE__", str(workspace)))


def run_script(script_path: Path, cwd: Path) -> tuple[str, str, int]:
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True, text=True, cwd=str(cwd), timeout=120
    )
    return result.stdout, result.stderr, result.returncode


def verify_run(ws: Path, run_dir: Path, critical_points: list[str]) -> dict:
    log_path = run_dir / "final_script_log.txt"
    screenshots_dir = run_dir / "screenshots"
    results = {"passed": [], "failed": [], "log": "", "screenshots": []}

    if log_path.exists():
        results["log"] = log_path.read_text()

    if screenshots_dir.exists():
        results["screenshots"] = sorted([
            str(p.relative_to(ws)) for p in screenshots_dir.glob("*.png")
        ])

    # Basic verification: check that CPs have corresponding evidence
    for i, cp in enumerate(critical_points, 1):
        log_text = results["log"]
        has_screenshot = any(f"cp{i}" in s.lower() or f"critical_{i}" in s.lower()
                           for s in results["screenshots"])
        has_log_evidence = f"CP{i}" in log_text or f"cp{i}" in log_text
        if has_screenshot or has_log_evidence:
            results["passed"].append(f"CP{i}: {cp}")
        else:
            results["failed"].append(f"CP{i}: {cp}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Webwright runner for Sift")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--start-url", default="https://www.google.com",
                       help="Starting URL")
    parser.add_argument("--workspace", default=None,
                       help="Custom workspace path")
    parser.add_argument("--craft", action="store_true",
                       help="CLI tool mode (parameterized)")
    parser.add_argument("--cps", nargs="+", default=[],
                       help="Critical points as separate arguments")
    args = parser.parse_args()

    # Resolve workspace
    base = Path(args.workspace) if args.task else Path.home() / ".hermes/sift/webwright"
    task_slug = args.task.lower().replace(" ", "_")[:40]
    ws = ensure_workspace(base, task_slug)

    # Default critical points if none provided
    cps = args.cps if args.cps else [
        f"Complete the task: {args.task}",
        "Capture screenshots as evidence",
    ]

    print(f"[Webwright] Task: {args.task}")
    print(f"[Webwright] Workspace: {ws}")

    # Write plan
    plan_path = write_plan(ws, args.task, cps)
    print(f"[Webwright] Plan written: {plan_path}")

    # Create run directory
    run_id = next_run_id(ws)
    run_dir = ws / "final_runs" / f"run_{run_id}"
    run_dir.mkdir(parents=True)
    (run_dir / "screenshots").mkdir()
    print(f"[Webwright] Run directory: {run_dir}")

    # Phase 1: Exploration
    print("\n[Webwright] Phase 1: Exploration")
    explore_script = generate_exploration_script(args.start_url, ws)
    explore_path = ws / "explore_tmp.py"
    explore_path.write_text(explore_script)

    stdout, stderr, rc = run_script(explore_path, ws)
    if stdout:
        print(stdout)
    if stderr:
        print(f"[explore stderr] {stderr[:500]}", file=sys.stderr)
    explore_path.unlink(missing_ok=True)

    # The return code was previously ignored, so a failed exploration flowed
    # straight into authoring and the run still summarised as ready. Exploration
    # is what produces the screenshots the later phases are verified against, so
    # a failure here has to be stated.
    explore_ok = (rc == 0)
    if not explore_ok:
        print(f"[Webwright] Exploration FAILED (exit {rc}). "
              f"No screenshots were captured, so nothing downstream can be "
              f"verified against them.", file=sys.stderr)
        if "No module named 'playwright'" in (stderr or ""):
            print("[Webwright] Cause: Playwright is not installed in this "
                  "interpreter. Install it and its browser before rerunning:\n"
                  "    pip install playwright && python -m playwright install firefox",
                  file=sys.stderr)
        print("[Webwright] Continuing to author a skeleton, but treat this run "
              "as INCOMPLETE.", file=sys.stderr)

    # Phase 2: Generate final script skeleton
    print(f"\n[Webwright] Phase 2: Authoring final_script.py")
    mode_tag = "CLI tool mode" if args.craft else "one-shot mode"

    skeleton = f'''#!/usr/bin/env python3
"""Webwright task: {args.task}
Mode: {mode_tag}
Generated by webwright_runner.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

WORKSPACE = Path("{run_dir}")
LOG = WORKSPACE / "final_script_log.txt"
SCREENSHOTS = WORKSPACE / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

async def main():
    LOG.write_text("")
    log = open(LOG, "a")

    async with async_playwright() as p:
        # Use the system Chrome already present on the host. The bundled
        # chromium revision in the local cache does not match this playwright
        # build, and firefox was never downloaded at all, so channel="chrome"
        # avoids fetching a browser purely to run a page. --no-sandbox is
        # needed when running as root.
        browser = await p.chromium.launch(
            headless=True, channel="chrome", args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={{"width": 1280, "height": 1800}})
        page = await ctx.new_page()

        # Navigate
        await page.goto("{args.start_url}", wait_until="domcontentloaded")
        log.write(f"step 1 action: Navigate to {args.start_url}\\n")

        # === TASK-SPECIFIC CODE START ===
        # TODO: Implement the task steps here
        # For each critical point:
        #   1. Interact with the page
        #   2. Save screenshot: SCREENSHOTS / "final_execution_<N>_<action>.png"
        #   3. Log: log.write(f"step <N> action: <description>\\n")
        #
        # Critical points:
{chr(10).join(f"        # - CP{i+1}: {cp}" for i, cp in enumerate(cps))}
        # === TASK-SPECIFIC CODE END ===

        # Final datum
        result = "TODO: Extract the final datum"
        log.write(f"RESULT: {{result}}\\n")
        print(f"[Webwright] Result: {{result}}")

        log.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
'''

    final_path = run_dir / "final_script.py"
    final_path.write_text(skeleton)
    print(f"[Webwright] Skeleton written: {final_path}")
    print(f"[Webwright] Next: Edit final_script.py to implement task steps, then run it")
    print(f"[Webwright] Run: python {final_path}")

    # Summary
    print(f"\n{'='*60}")
    print(f"Webwright run_{run_id} "
          f"{'ready' if explore_ok else 'INCOMPLETE (exploration failed)'}")
    print(f"  Plan:       {plan_path}")
    print(f"  Script:     {final_path}")
    _shot = ws / "screenshots" / "explore_1_start.png"
    print(f"  Explore:    {_shot}" if _shot.exists()
          else "  Explore:    (none — exploration produced no screenshot)")
    print(f"\nWorkflow: Plan → Explore → Author → Execute → Verify")
    print(f"Current state: Authoring (edit the TODO in final_script.py)")
    print('='*60)


if __name__ == "__main__":
    main()
