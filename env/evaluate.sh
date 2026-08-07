#!/usr/bin/env bash
# Evaluate one solution against HorizonMath.
# Usage: ./evaluate.sh <path-to-solution.py> <problem_id> [--json]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$HERE/stubs:$HERE/horizonmath/scripts:$HERE/horizonmath:${PYTHONPATH:-}"
SOLUTION="$1"; PROBLEM_ID="$2"; shift 2 || true
cd "$HERE/horizonmath"
# resolve the solution path relative to the original caller dir
case "$SOLUTION" in /*) ;; *) SOLUTION="$OLDPWD/$SOLUTION" ;; esac
python scripts/evaluate.py --llm-output "$SOLUTION" --problem-id "$PROBLEM_ID" "$@"
