# Services – Hilfstools für die Masterarbeit

Dieses Verzeichnis enthält Hilfsskripte zur Verwaltung der Masterarbeit.

---

## Zotero-Sync (`zotero_sync.py`)

Das Skript lädt alle Einträge aus einer Zotero-Bibliothek über die
[Zotero Web API v3](https://www.zotero.org/support/dev/web_api/v3/start)
und schreibt sie als BibTeX in `B_Literatur/literatur.bib`.

### Voraussetzungen

- Python 3.10 oder neuer
- `requests`-Bibliothek

```bash
pip install requests
# oder
pip install -r services/requirements.txt
```

---

### Einrichtung

#### 1. Zotero-API-Schlüssel erstellen

1. Zotero öffnen → **Bearbeiten** → **Einstellungen** → Reiter **Feeds/API**
2. Klick auf **Neuen privaten Schlüssel erstellen**
3. Name vergeben (z. B. „Masterarbeit-Sync")
4. Berechtigung: **Bibliothek lesen** (read) – reicht aus
5. Schlüssel notieren (wird nur einmal angezeigt)

#### 2. Zotero-User-ID ermitteln

Auf derselben Einstellungsseite (**Feeds/API**) steht:
> „Ihre User-ID für API-Aufrufe: **1234567**"

#### 3. `.env`-Datei anlegen

```bash
cp services/.env.example services/.env
```

Datei `services/.env` mit einem Texteditor öffnen und Werte eintragen:

```dotenv
ZOTERO_API_KEY=abc123xyz...
ZOTERO_USER_ID=1234567
```

> **Wichtig:** Die `.env`-Datei enthält geheime Zugangsdaten und wird
> nicht in Git eingecheckt (Eintrag in `.gitignore`).

---

### Verwendung

Aus dem **Projektstamm** ausführen:

```bash
# Normale Synchronisation (erstellt Backup der alten .bib)
python3 services/zotero_sync.py

# Nur herunterladen, keine Datei schreiben
python3 services/zotero_sync.py --dry-run

# Ohne Backup-Erstellung
python3 services/zotero_sync.py --no-backup

# Abweichender Ausgabepfad
python3 services/zotero_sync.py --output pfad/zur/datei.bib

# Hilfe
python3 services/zotero_sync.py --help
```

#### Typischer Ablauf

```
Verbinde mit Zotero API …
Gefunden: 85 Einträge in der Bibliothek
  Geladen: 85/85
BibTeX-Einträge empfangen: 85
Backup erstellt: B_Literatur/literatur_backup_20260222_143012.bib
Gespeichert: B_Literatur/literatur.bib
Sync abgeschlossen.
```

---

### Gruppenbiblothek verwenden

Falls die Quellen in einer Zotero-Gruppenbibl. verwaltet werden:

```dotenv
ZOTERO_LIBRARY_TYPE=group
ZOTERO_GROUP_ID=9876543
```

Die Gruppen-ID findet sich in der URL der Gruppenbibl.:
`zotero.org/groups/**9876543**/…`

---

### Automatisierung (optional)

#### Makefile-Ziel

```makefile
sync-bib:
	python3 services/zotero_sync.py
```

#### GitHub Actions Workflow

Ein manuell auslösbarer Workflow steht unter `.github/workflows/build-latex.yml`
zur Verfügung. Um den Sync vor dem Build zu integrieren, kann dort ein Schritt
ergänzt werden:

```yaml
- name: Sync Zotero bibliography
  env:
    ZOTERO_API_KEY: ${{ secrets.ZOTERO_API_KEY }}
    ZOTERO_USER_ID: ${{ secrets.ZOTERO_USER_ID }}
  run: |
    pip install requests
    python3 services/zotero_sync.py --no-backup
```

Secrets im GitHub-Repo anlegen:
**Settings → Secrets and variables → Actions → New repository secret**

---

### Hinweise

| Thema | Detail |
|---|---|
| Rate-Limiting | Zotero erlaubt ~30 Anfragen/Minute; das Skript wartet 100 ms zwischen Seiten |
| Paginierung | Automatisch (100 Einträge pro Seite, Zotero-Maximum) |
| Backup | Wird automatisch erstellt: `literatur_backup_YYYYMMDD_HHMMSS.bib` |
| Encoding | UTF-8 (Zotero-Standard für BibTeX-Export) |
| Zotero-Schlüsselformat | Übernimmt die in Zotero konfigurierten Zitationskeys |

---

### Fehlerbehebung

**`ZOTERO_API_KEY ist nicht gesetzt`**
→ `.env`-Datei vorhanden und korrekt befüllt?

**HTTP 403 Forbidden**
→ API-Schlüssel fehlt die Leseberechtigung → neuen Schlüssel mit „Library read" erstellen.

**HTTP 429 Too Many Requests**
→ Zu viele Anfragen; kurz warten und erneut versuchen.

**Leere `.bib`-Datei nach dem Sync**
→ `--dry-run` zur Diagnose nutzen; ggf. `ZOTERO_USER_ID` und Bibliothekstyp prüfen.

---

## Zotero-Tagging fuer `92_Abstract` (`zotero_tag_abstracts.py`)

Das Skript taggt Quellen in einer Zotero-Collection automatisch entlang von:

- `qual:*` (Qualitaet: Quellentyp, Peer-Review, Impact, VHB/ABS soweit verfuegbar)
- `thema:*` (Themen: z. B. SDT, Fuehrung, Entscheidung, GenAI, Bankensektor)
- `methode:*` (Methodik: z. B. Experiment, Review, Interview, Survey, konzeptionell)

### Voraussetzungen

- Python 3.10+
- gueltige Zotero-API-Zugangsdaten mit Schreibrechten fuer Tags

### Konfiguration

Standardmaessig nutzt das Skript dieselben ENV-Werte wie `zotero_sync.py`:

- `ZOTERO_API_KEY`
- `ZOTERO_USER_ID`
- `ZOTERO_LIBRARY_TYPE` (`user` oder `group`)
- `ZOTERO_GROUP_ID` (nur bei Group-Library)

Werte koennen alternativ direkt als CLI-Parameter gesetzt werden.

### Verwendung

```bash
# Dry-Run (Standard): zeigt geplante Aenderungen, schreibt nichts in Zotero
python3 services/zotero_tag_abstracts.py --collection-name 92_Abstract

# Nur Kategoriensystem ausgeben (ohne API-Zugriff)
python3 services/zotero_tag_abstracts.py --print-taxonomy

# Tags tatsaechlich in Zotero schreiben
python3 services/zotero_tag_abstracts.py --collection-name 92_Abstract --apply

# Mit Untercollections
python3 services/zotero_tag_abstracts.py \
  --collection-name 92_Abstract \
  --include-subcollections \
  --apply

# Eindeutig ueber Collection-Key
python3 services/zotero_tag_abstracts.py --collection-key ABCD1234 --apply
```

Standardmaessig ersetzt das Skript bereits vorhandene, vom Skript verwaltete Praefix-Tags (`qual:`, `thema:`, `methode:`), damit die Kategorisierung konsistent bleibt.
Mit `--keep-managed-tags` bleiben diese Alt-Tags erhalten.

Ein Laufreport wird als JSON unter `utils/zotero_tagging_92_abstract_report.json` geschrieben (Pfad via `--report-path` konfigurierbar).
