# .latexmkrc — Latexmk configuration for Master-Thesis
# Tells latexmk to use Biber (required by biblatex APA style)

$pdf_mode = 1;          # generate PDF via pdflatex
$biber = 'biber';       # use biber as the bibliography processor
$bibtex_use = 2;        # run biber/bibtex as needed and always update .bbl
