#!/bin/bash
# Stop-Hook: rendert KI Einsatz.tex nach jeder Claude-Code-Session neu.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$REPO/services/ki_log/ki_log.py" render 2>/dev/null || true
