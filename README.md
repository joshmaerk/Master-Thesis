# Master-Thesis

## TeX setup (new machine)

This project expects TeX Live/MacTeX with `tlmgr`.

1. Install TeX Live (MacTeX on macOS).
2. Run:

```bash
bash scripts/setup-tex.sh
```

The script uses `sudo` automatically if TeX Live is installed system-wide.

3. Compile:

```bash
latexmk -pdf main.tex
```

## One-command build with timestamped PDF

Run:

```bash
bash scripts/build.sh
```

This creates:

```text
builds/YYYYMMDD-HHMM Master Thesis Joshua Maerker.pdf
```

If `latexmk` or `pdflatex` is still not found in your current shell, restart the terminal or run:

```bash
eval "$(/usr/libexec/path_helper)"
```
