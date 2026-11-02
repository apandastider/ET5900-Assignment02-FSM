#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bash "$ROOT/scripts/release_preflight.sh"
OUT="${1:-$HOME/et5900-fsm-assignment-student.zip}"
cd "$(dirname "$ROOT")"
base="$(basename "$ROOT")"
zip -rq "$OUT" "$base" -x '*/__pycache__/*' '*.pyc' '*/build/*' '*/install/*' '*/log/*' '*/.git/*' '*REFERENCE_ONLY.sdf' '*/docs/INSTRUCTOR_ACCEPTANCE.md' '*.zip'
echo "Created $OUT"
