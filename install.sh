#!/bin/sh
set -e

HERE=$(cd "$(dirname "$0")" && pwd)

mkdir -p "$HOME/.local/bin"
cp "$HERE/subnet_calc.py" "$HOME/.local/bin/subnet_calc"
chmod +x "$HOME/.local/bin/subnet_calc"

case "$(basename "${SHELL:-bash}")" in
  zsh) RC="$HOME/.zshrc" ;;
  *)   RC="$HOME/.bashrc" ;;
esac

if ! grep -q 'alias net=' "$RC" 2>/dev/null; then
  printf '\n# subnet calculator alias\nalias net="subnet_calc"\n' >> "$RC"
fi

if ! command -v subnet_calc >/dev/null 2>&1; then
  printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$RC"
  echo "Note: added ~/.local/bin to PATH in $RC"
fi

echo "Installed subnet_calc. Reload with: source $RC"
