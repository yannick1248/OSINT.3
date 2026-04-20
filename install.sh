#!/usr/bin/env bash
# OSINT OMEGA — installation automatisée.
#
# Niveaux :
#   ./install.sh core       # uniquement osint_omega (Python) — DEFAUT
#   ./install.sh full       # core + backend FastAPI + frontend Next.js
#   ./install.sh tools      # clone/installe les outils OSINT externes optionnels
#
# `core` n'exige AUCUN sudo ; `full` et `tools` peuvent nécessiter apt/go/npm.
# Le script est idempotent et s'arrête au premier échec.

set -euo pipefail

LEVEL="${1:-core}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
TOOLS_DIR="$ROOT/tools"

banner() { printf '\n\033[1;36m[OSINT OMEGA] %s\033[0m\n' "$*"; }
warn()   { printf '\033[1;33m[warn] %s\033[0m\n' "$*" >&2; }

install_core() {
  banner "Installation de osint_omega (paquet Python)"
  python3 -m pip install --upgrade pip
  python3 -m pip install -e "$ROOT/osint_omega[dev]"
  mkdir -p "$ROOT/data/logs"
  banner "OK — python omega.py --help"
}

install_full() {
  install_core
  if [ -d "$ROOT/backend" ]; then
    banner "Installation du backend FastAPI"
    python3 -m pip install -e "$ROOT/backend[dev]"
  fi
  if [ -d "$ROOT/frontend" ] && command -v npm >/dev/null 2>&1; then
    banner "Installation du frontend Next.js"
    ( cd "$ROOT/frontend" && npm install --no-audit --no-fund )
  else
    warn "npm introuvable — étape frontend ignorée."
  fi
}

install_tools() {
  banner "Clonage des outils OSINT externes (optionnels)"
  mkdir -p "$TOOLS_DIR"
  cd "$TOOLS_DIR"

  clone_or_update() {
    local url="$1" dir="$2"
    if [ -d "$dir/.git" ]; then
      ( cd "$dir" && git pull --ff-only ) || warn "update failed: $dir"
    else
      git clone --depth 1 "$url" "$dir" || warn "clone failed: $url"
    fi
  }

  # Reconnaissance
  clone_or_update https://github.com/soxoj/maigret maigret
  clone_or_update https://github.com/laramies/theHarvester theHarvester
  python3 -m pip install --upgrade holehe

  # Infrastructure / énumération
  clone_or_update https://github.com/smicallef/spiderfoot spiderfoot

  # Dark web
  clone_or_update https://github.com/DedSecInside/TorBot TorBot
  clone_or_update https://github.com/josh0xA/darkdump darkdump

  if command -v go >/dev/null 2>&1; then
    banner "Installation des outils Go (Subfinder, httpx, OnionScan, gosearch)"
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    go install -v github.com/s-rah/onionscan@latest || warn "onionscan: build may fail."
    go install -v github.com/ibnaleem/gosearch@latest || warn "gosearch: build may fail."
  else
    warn "Go introuvable — outils projectdiscovery ignorés."
  fi

  banner "Outils externes traités (les absences sont gérées par le moteur)."
}

case "$LEVEL" in
  core)  install_core ;;
  full)  install_full ;;
  tools) install_tools ;;
  *) echo "usage: $0 {core|full|tools}" >&2 ; exit 2 ;;
esac
