#!/usr/bin/env bash
set -euo pipefail

rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
echo "Done. Run: source .venv/bin/activate"
