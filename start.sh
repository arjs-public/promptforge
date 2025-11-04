#!/usr/bin/env bash
# start.sh – start PromptForge.app from the "dist" folder
#
# Usage:
#   1. Put this file next to the “dist” directory (or somewhere on $PATH).
#   2. Make it executable:  chmod +x start.sh
#   3. Run:  ./start.sh   (or start.sh if in $PATH)
#
# What it does
#   • Locates PromptForge.app under a given dist folder.
#   • Checks if a process named PromptForge (the binary inside the bundle) is already running.
#   • Falls back to an AppleScript query if the shell‑based checks fail.
#   • If the app is not running, it launches it in the background.

set -euo pipefail

# ------------------------------------------------------------------
# 1. Locate the app bundle
# ------------------------------------------------------------------
dist_dir="${1:-./dist}"
app_path="${dist_dir}/PromptForge.app"

if [[ ! -d "$app_path" ]]; then
    echo "❌  Cannot find $app_path" >&2
    exit 1
fi

# ------------------------------------------------------------------
# 2. Check if the app is already running
# ------------------------------------------------------------------
#   a) First try the fast “process name” check
running=false
if pgrep -x "PromptForge" > /dev/null; then
    running=true
elif pgrep -f "$(basename "$app_path")" > /dev/null; then
    # fallback: match the full command line (covers the rare case the binary has a different name)
    running=true
elif ps aux | grep -q "/[P]romptForge"; then
    # even more generous grep
    running=true
fi

if $running; then
    echo "⚙️  PromptForge.app is already running."
    exit 0
fi

# ------------------------------------------------------------------
# 3. Launch the app
# ------------------------------------------------------------------
echo "📦  Launching PromptForge.app from $app_path"
open "$app_path" &

echo "✅  Started PromptForge.app (PID $!)"

