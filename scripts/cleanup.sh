#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ -d reports ]]; then
    find reports -maxdepth 1 -type f -name '*.csv' -delete
fi

if [[ -f logs/activity.log ]]; then
    rm -f logs/activity.log
fi

echo "Generated CSV reports and activity log removed. Source files preserved."
