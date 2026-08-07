#!/usr/bin/env bash
# Fast HorizonMath setup for Kepler — seconds, not minutes.
# Deliberately does NOT run `uv sync`, which pulls torch, fpylll, cysignals,
# snappy, snappy-manifolds, anthropic, openai and google-genai (~GBs, slow,
# needs compilers). Single-solution scoring needs none of that.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing minimal deps (numpy, scipy, mpmath)"
pip install --quiet --disable-pip-version-check numpy scipy mpmath

echo "==> Configuring PYTHONPATH (stubs + scripts + repo)"
export PYTHONPATH="$HERE/stubs:$HERE/horizonmath/scripts:$HERE/horizonmath:${PYTHONPATH:-}"

cat > "$HERE/env.sh" <<ENVEOF
export PYTHONPATH="$HERE/stubs:$HERE/horizonmath/scripts:$HERE/horizonmath:\${PYTHONPATH:-}"
ENVEOF

echo "==> Verifying imports"
python -c "import numpy, scipy, mpmath; print('  deps OK')"
python -c "import google.genai; print('  google.genai stub OK')"

echo "==> Verifying problem set"
python - <<'PYEOF'
import json, pathlib
p = pathlib.Path(__file__).parent if "__file__" in dir() else pathlib.Path(".")
data = json.load(open("horizonmath/data/problems_full.json"))
print(f"  {len(data)} problems loaded")
for s in (0, 1, 2, 3):
    print(f"    solvability={s}: {sum(1 for x in data if x['solvability'] == s)}")
PYEOF

echo
echo "Setup complete. In each new shell run:  source $HERE/env.sh"
echo "Then evaluate with:  ./evaluate.sh <solution.py> <problem_id>"
