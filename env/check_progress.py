#!/usr/bin/env python3
"""Show which solvability=1 problems are done vs remaining.

Usage:
    python check_progress.py [path-to-solutions-dir]

Defaults to ./solutions. Point it at a cloned Keplerdev project folder to
resume a run, e.g.:
    python check_progress.py Keplerdev/projects/2026-08-06-horizonmath-solvability1/solutions
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
problems = json.load(open(HERE / "horizonmath/data/problems_full.json"))
target = [p for p in problems if p["solvability"] == 1]

sol_dir = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "solutions")
done = {f.stem for f in sol_dir.glob("*.py")} if sol_dir.is_dir() else set()

remaining = [p for p in target if p["id"] not in done]
print(f"solvability=1 total: {len(target)} | done: {len(target)-len(remaining)} | remaining: {len(remaining)}")
if remaining:
    print("\nRemaining:")
    for p in remaining:
        print(f"  {p['id']:38s} {p['domain']:20s} {p['output_type']:14s} {p['evaluation_mode']}")
