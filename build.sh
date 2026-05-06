#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

OUTPUT="TablePro.alfredworkflow"
SRC=workflow

python3 generate-icons.py

rm -f "$OUTPUT"
(cd "$SRC" && zip -qr "../$OUTPUT" .)

echo "Built $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
echo "Double-click to install in Alfred."
