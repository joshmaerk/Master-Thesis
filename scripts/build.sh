#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

# Force a fresh build: remove stale auxiliary files (including .bbl)
# so that biber always regenerates the bibliography from scratch.
latexmk -C
rm -f main.bbl main.bcf main.run.xml main.acn main.acr main.alg main.glo main.gls main.glg
latexmk -pdf main.tex

timestamp="$(date +"%Y%m%d-%H%M")"
output_dir="${ROOT_DIR}/builds"
output_file="${timestamp} Master Thesis Joshua Maerker.pdf"

mkdir -p "${output_dir}"
cp -f "${ROOT_DIR}/main.pdf" "${output_dir}/${output_file}"

echo "Build complete: ${output_dir}/${output_file}"
