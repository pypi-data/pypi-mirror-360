# Slub SolrHelper

Willkommen beim Slub SolrHelper!

Dieses Tool hilft Bibliothekaren und Softwareentwicklern dabei, Dokumente in einem Solr-Index einfach anzusehen und zu bearbeiten.

Es handelt sich um eine kleine Webanwendung, die lokal gestartet werden kann.

## Features

- Verbindung zu einem beliebigen Solr-Core.
- Web-Oberfläche zur interaktiven Suche und Anzeige von Dokumenten.
- Interaktives Bearbeiten einzelner Dokumentenfelder direkt im Browser.
- Automatische Erkennung der Solr-Server-Fähigkeiten für sichere Updates (Atomic Updates vs. Full Re-Index).

## Installation

Die empfohlene Methode zur Installation und Ausführung des `solr-helper` ist die Verwendung von `uv`, einem extrem schnellen Python-Paketmanager.

### 1. uv installieren

Falls du `uv` noch nicht installiert hast, kannst du dies mit einem der folgenden Befehle tun:

**Linux und macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Weitere Installationsmethoden findest du in der [offiziellen `uv` Dokumentation](https://github.com/astral-sh/uv#installation).

### 2. solr-helper ausführen

Es gibt zwei empfohlene Wege, den `solr-helper` zu nutzen:

**Option A: Direkte Ausführung mit `uvx` (Empfohlen)**

`uvx` ist ein Werkzeug, das `npx` aus der Node.js-Welt ähnelt. Es lädt das Paket in eine temporäre, isolierte Umgebung herunter, führt es aus und räumt danach wieder auf. So bleibt dein System sauber.

```bash
uvx solr-helper start-web --solr-url http://dein-solr:8983 --core dein-core
```

**Option B: Permanente Installation**

Wenn du das Tool systemweit oder in einer bestimmten virtuellen Umgebung installieren möchtest:

```bash
uv pip install solr-helper
```

Danach kannst du es direkt aufrufen:

```bash
solr-helper start-web --solr-url http://dein-solr:8983 --core dein-core
```

## Benutzung der Web-Oberfläche

Um die Web-Anwendung zu starten, führe folgenden Befehl aus:

```bash
solr-helper start-web --solr-url http://dein-solr:8983 --core dein-core
```

Die Anwendung ist dann unter `http://127.0.0.1:5000` erreichbar.

1.  **Suchen:** Gib einen Suchbegriff in das Suchfeld ein, um Dokumente zu finden.
2.  **Anzeigen:** Klicke auf die ID eines Dokuments in der Ergebnisliste, um die Detailansicht zu öffnen.
3.  **Bearbeiten:**
    - Klicke in der Detailansicht auf den "Bearbeiten"-Button neben einem Feld.
    - Ein Formular erscheint, in dem du den neuen Wert eingeben kannst.
    - Beim Speichern wird das Feld im Solr-Index aktualisiert.
    - **Hinweis:** Das Tool prüft, ob der Solr-Server "atomare Updates" unterstützt. Wenn nicht, wird eine Warnung angezeigt, da das Bearbeiten von Feldern zu Datenverlust in anderen, nicht gespeicherten Feldern führen kann.

## Konfiguration

Die Verbindung zu Solr kann auf drei Arten konfiguriert werden (Priorität: CLI > ENV > config.toml > Default):

1. **CLI-Optionen:**
   - `--solr-url` (z.B. `http://localhost:8983`)
   - `--core` (z.B. `testing`)
   - Beispiel:
     ```bash
     solr-helper show-schema --solr-url http://sdvdmgtestsolr01.slub-dresden.de:8984 --core ahn-release
     ```
2. **Umgebungsvariablen:**
   - `SOLRHELPER_SOLR_URL`
   - `SOLRHELPER_CORE`
3. **Konfigurationsdatei:**
   - `config.toml` im Projektverzeichnis oder `~/.solrhelper/config.toml`
   - Beispiel-Inhalt:
     ```toml
     solr_url = "http://localhost:8983"
     core = "testing"
     ```
4. **Defaults:**
   - `solr_url = "http://localhost:8983"`
   - `core = "testing"`

## Entwicklung

Um die Anwendung lokal zu entwickeln:

1.  **Virtuelle Umgebung anlegen:**
    ```bash
    uv venv
    source .venv/bin/activate.fish
    ```
2.  **Abhängigkeiten installieren:**
    ```bash
    uv pip install -e .
    ```
3.  **Solr-Helper CLI nutzen:**
    ```bash
    # Verbindung testen
    solr-helper test-connection --solr-url http://dein-solr:8983 --core dein-core

    # Schema anzeigen
    solr-helper show-schema --solr-url http://dein-solr:8983 --core dein-core

    # Web-Oberfläche starten
    solr-helper start-web --solr-url http://dein-solr:8983 --core dein-core
    ```
