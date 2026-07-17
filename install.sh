#!/usr/bin/env bash
# dots bootstrap — turn a bare Arch install into this machine's setup.
#
#   curl -fsSL https://raw.githubusercontent.com/redmoondz/dots/master/install.sh | bash
#
# Flags are passed through to install.py:
#   curl -fsSL .../install.sh | bash -s -- --dry-run
set -euo pipefail

REPO_URL="https://github.com/redmoondz/dots.git"
DEST="$HOME/Documents/dots"
BRANCH="master"

abort() { printf 'error: %s\n' "$1" >&2; exit 1; }

[[ $EUID -eq 0 ]] && abort "run as your normal user, not root (makepkg refuses root; sudo is used internally)"
command -v pacman >/dev/null || abort "this bootstrap is for Arch Linux"
command -v sudo   >/dev/null || abort "install sudo and add your user to the wheel group first"

if ! command -v git >/dev/null || ! command -v python3 >/dev/null; then
    echo "==> installing git + python (full -Syu to avoid a partial upgrade)"
    sudo pacman -Syu --needed --noconfirm git python
fi

if [[ -d "$DEST/.git" ]]; then
    echo "==> updating existing clone at $DEST"
    git -C "$DEST" pull --ff-only
else
    echo "==> cloning $REPO_URL -> $DEST"
    mkdir -p "$(dirname "$DEST")"
    git clone -b "$BRANCH" "$REPO_URL" "$DEST"
fi

# When run via `curl | bash`, stdin is the pipe — reattach the terminal so
# install.py can ask its interactive questions.
if [[ ! -t 0 && -r /dev/tty ]]; then
    exec python3 "$DEST/install.py" install "$@" </dev/tty
fi
exec python3 "$DEST/install.py" install "$@"
