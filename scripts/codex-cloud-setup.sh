#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

log() {
  printf '\n[%s] %s\n' "$(date -u '+%H:%M:%S')" "$*"
}

run_as_root() {
  if [ "$(id -u)" = "0" ]; then
    "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    log "Skipping root command because sudo is unavailable: $*"
  fi
}

apt_install() {
  if [ "${CODEX_CLOUD_APT:-1}" != "1" ] || ! command -v apt-get >/dev/null 2>&1; then
    return 0
  fi

  log "Installing Python build and document-processing OS packages"
  run_as_root apt-get update
  run_as_root apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    build-essential \
    python3 \
    python3-venv \
    python3-pip
}

ensure_python_env() {
  local python_bin="${PYTHON_BIN:-python3}"
  if ! command -v "$python_bin" >/dev/null 2>&1; then
    log "Python command not found: ${python_bin}"
    exit 1
  fi

  log "Creating Python virtual environment"
  "$python_bin" -m venv .venv
  # shellcheck source=/dev/null
  source .venv/bin/activate

  python -m pip install --upgrade pip setuptools wheel

  if [ -f requirements.lock ] && [ "${CODEX_CLOUD_USE_REQUIREMENTS_LOCK:-0}" = "1" ]; then
    log "Installing locked requirements"
    python -m pip install -r requirements.lock
  elif [ -f requirements.txt ]; then
    log "Installing requirements.txt"
    python -m pip install -r requirements.txt
  fi

  if [ -f pyproject.toml ]; then
    log "Installing editable package with dev extras"
    python -m pip install -e ".[dev]"
  fi
}

optional_smoke() {
  if [ "${CODEX_CLOUD_RUN_SMOKE:-0}" != "1" ]; then
    log "Skipping smoke checks. Set CODEX_CLOUD_RUN_SMOKE=1 to run pytest."
    return 0
  fi

  # shellcheck source=/dev/null
  source .venv/bin/activate
  pytest -q
}

log "Preparing public Intent Compression Architecture Codex Cloud environment"
mkdir -p .codex-cloud/{cache,data,evidence,logs,tmp}

apt_install
ensure_python_env
optional_smoke

log "Public ICA setup complete"
log "Typical next step: source .venv/bin/activate && pytest -q"
