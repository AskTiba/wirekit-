#!/bin/sh
set -e

HERE=$(cd "$(dirname "$0")" && pwd)

mkdir -p "$HOME/.local/bin"
cp "$HERE/wirekit.py" "$HOME/.local/bin/wirekit"
chmod +x "$HOME/.local/bin/wirekit"

case "$(basename "${SHELL:-bash}")" in
  zsh) RC="$HOME/.zshrc" ;;
  *)   RC="$HOME/.bashrc" ;;
esac

if ! grep -q 'alias net=' "$RC" 2>/dev/null; then
  printf '\n# wirekit alias\nalias net="wirekit"\n' >> "$RC"
fi

if ! command -v wirekit >/dev/null 2>&1; then
  printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$RC"
  echo "Note: added ~/.local/bin to PATH in $RC"
fi

echo "Installed wirekit. Reload with: source $RC"
