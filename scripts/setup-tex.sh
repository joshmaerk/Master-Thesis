#!/usr/bin/env bash
set -euo pipefail

if ! command -v tlmgr >/dev/null 2>&1; then
  echo "Error: 'tlmgr' not found. Install TeX Live/MacTeX first."
  exit 1
fi

# Use sudo automatically when TeX Live is system-wide and not writable.
TLMGR=(tlmgr)
if ! tlmgr conf >/dev/null 2>&1; then
  echo "Error: tlmgr is not usable in this TeX setup."
  exit 1
fi

if ! touch "$(kpsewhich -var-value=TEXMFSYSVAR)/.codex-write-test" 2>/dev/null; then
  if command -v sudo >/dev/null 2>&1; then
    TLMGR=(sudo tlmgr)
  else
    echo "Error: No write permission for TeX Live and 'sudo' is unavailable."
    exit 1
  fi
else
  rm -f "$(kpsewhich -var-value=TEXMFSYSVAR)/.codex-write-test"
fi

# Keep tlmgr itself current before installing packages.
"${TLMGR[@]}" update --self

# Packages used by this thesis template.
packages=(
  latexmk
  biber
  titlesec
  fancyhdr
  pdflscape
  caption
  footmisc
  hyperref
  etoolbox
  csquotes
  pdfpages
  tabularx
  booktabs
  array
  lmodern
  tikz
  tocloft
  biblatex
  biblatex-apa
  babel-german
  datetime2
  draftwatermark
)

"${TLMGR[@]}" install "${packages[@]}"

echo
echo "TeX setup complete."
echo "Build with: latexmk -pdf main.tex"
