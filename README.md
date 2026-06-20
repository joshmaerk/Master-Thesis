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

## Zotero tagging for `92_Abstract`

To auto-tag literature in Zotero (quality + topic + method tags), use:

```bash
python3 services/zotero_tag_abstracts.py --collection-name 92_Abstract
```

This runs as a dry-run by default. To write tags back to Zotero:

```bash
python3 services/zotero_tag_abstracts.py --collection-name 92_Abstract --apply
```

Configuration is read from `services/.env` (`ZOTERO_API_KEY`, `ZOTERO_USER_ID`, optional group settings) or via CLI flags.
