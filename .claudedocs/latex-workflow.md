# LaTeX Workflow

## Scope

Use this document before substantial edits to `.tex` files, the LaTeX build, layout, glossary, references, figures, tables, or thesis structure.

## Build commands

- Preferred reproducible build: `bash scripts/build.sh`.
- Initial TeX package setup: `bash scripts/setup-tex.sh`.
- Manual local build, when needed: `latexmk -pdf main.tex`.
- The build uses BibLaTeX with Biber; do not switch to BibTeX.
- `.latexmkrc` configures Biber and glossary generation support.

## Main document

- `main.tex` is the main entry point and currently contains the LaTeX preamble.
- `variables.tex` contains thesis metadata.
- `A_Template/glossary.tex` contains acronym definitions.
- `B_Literatur/literatur.bib` is loaded as bibliography resource.

## Content and layout

- Keep scientific prose and layout changes separate where possible.
- Do not change heading sizes, page numbering, captions, margins, spacing, or watermark behavior unless requested.
- Figures are labelled as `Abbildung`; tables are labelled as `Tabelle`.
- Use existing package conventions from `main.tex`; avoid adding packages unless necessary.

## Cross-references and labels

- Use stable, descriptive labels for new sections, figures, tables, and equations.
- Use non-breaking spaces for references, e.g. `Abschnitt~\ref{...}`.
- Prefer `\enquote{...}` for quotation marks in LaTeX prose.

## Glossary and acronyms

- Add new acronyms only in `A_Template/glossary.tex`.
- Use `\gls{...}` for first-use-aware references when appropriate.
- Use `\acrshort{...}` only when the short form is explicitly required.

## Scientific content protection

- Technical LaTeX fixes may adjust syntax, labels, spacing, or references.
- Do not change scientific claims, empirical findings, interpretations, or cited evidence without explicit user instruction.
