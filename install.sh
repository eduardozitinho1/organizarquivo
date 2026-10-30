#!/usr/bin/env bash
set -euo pipefail

# Organizarquivo one-line installer
# https://github.com/eduardozitinho1/organizarquivo

PKG="organizarquivo"
UPGRADE=0
for arg in "$@"; do
  case "$arg" in
    --upgrade|-u) UPGRADE=1 ;;
    --help|-h) echo "uso: install.sh [--upgrade]"; exit 0 ;;
  esac
done

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m ok\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mwarn\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31merr\033[0m %s\n' "$*" >&2; exit 1; }

# --- deteccao de ambiente ---
is_termux()    { [ -n "${TERMUX_VERSION:-}" ] || [ -d "/data/data/com.termux" ]; }
is_debian()    { command -v apt-get >/dev/null 2>&1; }
is_macos()     { [ "$(uname -s)" = "Darwin" ]; }
is_windows()   { [ "$(uname -s)" = "MINGW"* ] || [ "$(uname -s)" = "MSYS"* ]; }

# --- metodos ---
try_uv_tool() {
  command -v uv >/dev/null 2>&1 || return 1
  say "instalando via uv tool"
  if [ "$UPGRADE" = 1 ]; then
    uv tool upgrade "$PKG" && ok "uv tool upgrade $PKG"
  else
    uv tool install "$PKG" && ok "uv tool install $PKG"
  fi
}

try_pipx() {
  command -v pipx >/dev/null 2>&1 || return 1
  say "instalando via pipx"
  if [ "$UPGRADE" = 1 ]; then
    pipx upgrade "$PKG" && ok "pipx upgrade $PKG"
  else
    pipx install "$PKG" && ok "pipx install $PKG"
  fi
}

try_apt_termux() {
  is_termux || return 1
  say "instalando via pkg (Termux APT repo)"
  pkg install -y curl gnupg >/dev/null 2>&1 || true
  local keyring="$PREFIX/etc/apt/keyrings"
  local src="$PREFIX/etc/apt/sources.list.d/organizarquivo.list"
  local url="https://eduardozitinho1.github.io/organizarquivo-apt"
  mkdir -p "$keyring"
  curl -fsSL "$url/organizarquivo.gpg" -o "$keyring/organizarquivo.gpg"
  echo "deb [signed-by=$keyring/organizarquivo.gpg] $url termux main" > "$src"
  pkg update -y >/dev/null 2>&1 || true
  pkg install -y organizarquivo-termux && ok "pkg install organizarquivo-termux"
}

try_apt_debian() {
  is_debian || is_macos && return 1
  is_debian || return 1
  say "instalando via apt (repositorio APT)"
  local keyring="/etc/apt/keyrings"
  local src="/etc/apt/sources.list.d/organizarquivo.list"
  local url="https://eduardozitinho1.github.io/organizarquivo-apt"
  sudo install -d -m 0755 "$keyring"
  sudo curl -fsSL "$url/organizarquivo.gpg" -o "$keyring/organizarquivo.gpg"
  echo "deb [signed-by=$keyring/organizarquivo.gpg] $url stable main" | sudo tee "$src" >/dev/null
  sudo apt-get update -qq
  sudo apt-get install -y "$PKG" && ok "apt install $PKG"
}

try_brew() {
  is_macos || return 1
  command -v brew >/dev/null 2>&1 || return 1
  say "macOS detectado, mas ainda nao ha tap Homebrew publicado"
  warn "usando pipx como fallback"
  return 1
}

try_pip_user() {
  command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || return 1
  say "instalando via pip --user"
  local py
  py=$(command -v python3 || command -v python)
  if [ "$UPGRADE" = 1 ]; then
    "$py" -m pip install --user --upgrade "$PKG" && ok "pip --user (upgrade)"
  else
    "$py" -m pip install --user "$PKG" && ok "pip --user"
  fi
}

# --- escolha do metodo ---
if [ "$UPGRADE" = 0 ] && command -v organizarquivo >/dev/null 2>&1; then
  warn "organizarquivo ja esta instalado. use --upgrade para atualizar."
  organizarquivo --version 2>/dev/null || true
  exit 0
fi

tried=()
for method in \
  "try_uv_tool:uv tool" \
  "try_pipx:pipx" \
  "try_apt_termux:pkg (Termux APT)" \
  "try_apt_debian:apt (Debian APT)" \
  "try_brew:brew" \
  "try_pip_user:pip --user"; do
  fn="${method%%:*}"
  label="${method#*:}"
  tried+=("$label")
  if "$fn"; then
    echo
    ok "pronto. teste: organizarquivo --version"
    exit 0
  fi
done

die "nenhum metodo funcionou. Tente manualmente:
  - uv tool install organizarquivo
  - pipx install organizarquivo
  - pip install --user organizarquivo
  - pkg install organizarquivo-termux (Termux)
  - apt install organizarquivo (Debian/Ubuntu)"
