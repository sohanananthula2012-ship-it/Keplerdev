#!/bin/bash
# Runs INSIDE the Daytona sandbox. Clones repo, installs deps, launches parallel
# persistent SA workers that push improvements to GitHub.
set -u
cd /root
pip install -q numpy ortools 2>&1 | tail -1
rm -rf repo
git clone -q https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git repo
PROJ=/root/repo/projects/2026-08-08-dts-7-5-min-scope
cd "$PROJ/scripts"
[ -f "$PROJ/outputs/global_best.json" ] || cp "$PROJ/outputs/dts_best_125.json" "$PROJ/outputs/global_best.json"
NW=${1:-4}
for w in $(seq 1 "$NW"); do
  nohup python3 dts_worker.py "$w" 105 "$PROJ" > "$PROJ/outputs/worker_${w}.log" 2>&1 &
done
sleep 3
echo "launched $NW workers; running dts_worker procs:"
ps -eo pid,args | grep dts_worker | grep -v grep | wc -l
