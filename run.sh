#!/bin/zsh
set -eu
cd "${0:A:h}"
PYTHON="/Users/dabbabot/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$(command -v python3)"
fi
exec "$PYTHON" -u server.py
