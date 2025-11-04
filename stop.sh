#!/usr/bin/env bash
# stop.sh – Kill the parent process of any running PromptForge.app

set -euo pipefail        # safer shell behaviour

# ------------------------------------------------------------------
# 1. Find all PIDs that match "PromptForge.app" in the command line
# ------------------------------------------------------------------
#   -p  : show only the PID
#   -f  : match against the full command line
#   -n  : exit if nothing found (makes grep silent)
promptforge_pids=($(pgrep -f PromptForge))

if [[ ${#promptforge_pids[@]} -eq 0 ]]; then
    echo "No PromptForge.app processes found."
    exit 0
fi

# ------------------------------------------------------------------
# 2. Gather the unique PPIDs (parent PIDs) of those PIDs
# ------------------------------------------------------------------
#ppids=()
#for pid in "${promptforge_pids[@]}"; do
#    # ps -o ppid= prints only the PPID, no header
#    pp=$(ps -o ppid= -p "$pid" | tr -d '[:space:]')
#    [[ -n "$pp" ]] && ppids+=("$pp")
#done

# Remove duplicates
#ppids=($(printf "%s\n" "${ppids[@]}" | sort -u))

# ------------------------------------------------------------------
# 3. Kill each parent process (except PID 1)
# ------------------------------------------------------------------
for pp in "${promptforge_pids[@]}"; do
    if [[ "$pp" -eq 1 ]]; then
        echo "Skipping PPID 1 (init), not safe to kill."
        continue
    fi

    echo "Killing parent process $pp (child PID(s): ${promptforge_pids[*]})"
    if ! kill -9 "$pp" 2>/dev/null; then
        echo "  → FAILED to kill $pp (you might need sudo)."
    else
        echo "  → Success."
    fi
done

echo "stop.sh finished."

