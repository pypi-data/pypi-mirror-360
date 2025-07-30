# Slub SolrHelper

Willkommen beim Slub SolrHelper!

Dieses Tool hilft Bibliothekaren und Softwareentwicklern dabei, Dokumente in einem Solr-Index einfach anzusehen und zu bearbeiten.

Es handelt sich um eine kleine Webanwendung, die lokal gestartet werden kann.

## Features

### Innovatives Verbindungsmanagement
- **Dynamische Verbindungen**: Wechseln Sie zwischen verschiedenen Solr-Servern ohne Neustart
- **Browser-Speicher**: Verbindungen werden lokal im Browser gespeichert
- **Import/Export**: Teilen Sie Verbindungseinstellungen mit Kollegen
- **Automatische Tests**: Verbindungen werden vor der Verwendung getestet
- **Standard-Verbindung**: Markieren Sie eine Verbindung als Standard für den App-Start

### Erweiterte Suchfunktionen
- **Feldspezifische Suche**: Durchsuchen Sie gezielt einzelne Felder
- **Intelligente Feldauswahl**: Suggest-Funktion filtert verfügbare Felder beim Tippen
- **Substring-Suche**: Findet Teilbegriffe (z.B. "Buch" findet "Lehrbuch", "Buchhandlung")
- **Solr Highlighting**: Hervorgehobene Suchbegriffe in Suchergebnissen
- **Live-Suche**: HTMX-basierte Suche ohne Seitenneuladen

### Dokumentenbearbeitung
- **Atomare Updates**: Sichere Feldbearbeitung ohne Datenverlust (wenn vom Server unterstützt)
- **Dynamische Felder**: Erkennt und zeigt alle Dokumentfelder an, auch die nicht im Schema definierten
- **Neue Felder hinzufügen**: Erweitern Sie Dokumente um zusätzliche Informationen
- **Warnsystem**: Automatische Warnungen bei potenziellem Datenverlust
- **Modal-Bearbeitung**: Benutzerfreundliche Popup-Fenster für Feldbearbeitung

### Technische Features
- **Debug-Modus**: Detaillierte Logging-Ausgaben für Entwicklung (`--debug`)
- **Responsive Design**: Funktioniert auf Desktop und mobilen Geräten
- **Toast-Benachrichtigungen**: Elegante Erfolgs- und Fehlermeldungen
- **Modulare Architektur**: Saubere Code-Organisation für einfache Wartung

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

## Schnellstart für Bibliothekare

### **Flexibler Start (empfohlen für mehrere Server)**
```bash
# Starten ohne feste Verbindung - ermöglicht dynamisches Verbindungsmanagement
uvx solr-helper --no-connection-check start-web

# Oder mit permanenter Installation:
solr-helper --no-connection-check start-web
```

Die Anwendung ist dann unter `http://127.0.0.1:5000` erreichbar.

### **Start mit fester Verbindung**
```bash
# Direkt mit bekannter Verbindung starten
uvx solr-helper start-web --solr-url http://dein-solr:8983 --core dein-core
```

### **Debug-Modus für Entwicklung**
```bash
# Detaillierte Logs und Flask-Debug-Modus
solr-helper --debug --no-connection-check start-web
```

## Verbindungsmanagement

### **Neue Verbindung hinzufügen**
1. Gehen Sie zu `/connections` im Webinterface
2. Klicken Sie "Neue Verbindung hinzufügen"
3. Geben Sie Server-URL (z.B. `http://solr-server:8983`) und Core-Name ein
4. Vergeben Sie einen aussagekräftigen Namen
5. Testen Sie die Verbindung mit dem Test-Button
6. Speichern und verwenden

### **Verbindungen verwalten**
- **Verwenden**: Sofortiger Wechsel zu einer Verbindung (ohne Standard zu ändern)
- **Standard setzen**: Verbindung als Standard für App-Start markieren
- **Bearbeiten**: Verbindungsdetails ändern
- **Löschen**: Nicht mehr benötigte Verbindungen entfernen

### **Verbindungen teilen (Import/Export)**
```javascript
// Export aller Verbindungen (Browser-Konsole F12)
console.log(localStorage.getItem('solr_connections'))

// Import von Verbindungen (Browser-Konsole F12)
localStorage.setItem('solr_connections', 'JSON-String-hier-einfügen')
```

## Erweiterte Suchfunktionen

### **Feldspezifische Suche**
1. Wählen Sie "Textsuche" (statt ID-Suche)
2. **Intelligente Feldauswahl**: Tippen Sie Feldname (z.B. "title")
   → Dropdown filtert automatisch alle passenden Felder
3. Wählen Sie das gewünschte Feld aus der Liste
4. Geben Sie Ihren Suchbegriff ein
5. **Substring-Suche**: "Buch" findet "Lehrbuch", "Buchhandlung", "Buch der Bücher"
6. Erhalten Sie Ergebnisse mit **hervorgehobenen Suchbegriffen**

### **ID-Suche**
- Direkte Suche nach Dokument-IDs
- Sofortige Weiterleitung zum Dokument
- Ideal für bekannte Dokument-Identifikatoren

### **Live-Suchergebnisse**
- Kompakte Vorschau der ersten 5 Treffer
- Link zu vollständigen Ergebnissen
- Keine Seitenneuladen dank HTMX

## Dokumentenbearbeitung

### **Felder bearbeiten**
1. Öffnen Sie ein Dokument durch Klick auf eine ID
2. Klicken Sie "Edit" bei dem Feld, das Sie ändern möchten
3. **Modal-Fenster** öffnet sich mit dem aktuellen Wert
4. Ändern Sie den Wert nach Bedbedarf
5. **Automatische Speicherung**:
   - **Atomare Updates** (wenn Server unterstützt): Nur das geänderte Feld wird aktualisiert
   - **Full-Document-Update** (Fallback): Warnung wird angezeigt vor potenziellem Datenverlust

### **Neue Felder hinzufügen**
1. Scrollen Sie zum Ende der Dokumentansicht
2. Sektion "Neues Feld hinzufügen"
3. **Feldname**: z.B. "kommentar_str", "notiz_txt"
4. **Feldwert**: Ihr gewünschter Inhalt
5. Klicken Sie "Hinzufügen" → Feld wird sofort zum Dokument hinzugefügt

### **Sicherheitsfeatures**
- **Warnsystem**: Automatische Warnungen wenn atomare Updates nicht möglich
- **Datenschutz**: Nur `stored=false` Felder gehen bei Full-Updates verloren
- **Backup**: Original-Dokument wird vor Änderungen gesichert
- **Atomic Updates**: Bevorzugte Methode verhindert Datenverlust

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

### **Lokale Entwicklungsumgebung**
```bash
# Repository klonen
git clone https://github.com/thomsbe/SolrHelper.git
cd SolrHelper

# Mit uv (empfohlen)
uv sync

# Oder mit traditionellem venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -e .
```

### **Entwicklung starten**
```bash
# Debug-Modus mit detaillierten Logs
uv run solr-helper --debug --no-connection-check start-web

# Oder direkt:
solr-helper --debug --no-connection-check start-web
```

### **CLI-Befehle für Entwicklung**
```bash
# Verbindung testen
solr-helper test-connection --solr-url http://dein-solr:8983 --core dein-core

# Schema anzeigen
solr-helper show-schema --solr-url http://dein-solr:8983 --core dein-core

# Web-Oberfläche starten (Produktion)
solr-helper start-web --solr-url http://dein-solr:8983 --core dein-core

# Web-Oberfläche starten (Debug)
solr-helper --debug start-web --solr-url http://dein-solr:8983 --core dein-core
```

### **Architektur-Überblick**
- **Modularer Aufbau**: Separate Module für Routes, Utils, Templates
- **Flask Blueprints**: Saubere Code-Organisation (connection, search, record, api)
- **HTMX-Integration**: Moderne Web-UX ohne komplexes JavaScript
- **Alpine.js**: Reaktive UI-Komponenten für Verbindungsmanagement
- **DaisyUI**: Konsistentes Design-System
- **Loguru**: Strukturiertes Logging

### **Code-Qualität**
- **300-Zeilen-Regel**: Alle Dateien unter 300 Zeilen für LLM-Kompatibilität
- **Blueprint-basiert**: Klare Trennung der Verantwortlichkeiten
- **Type Hints**: Vollständige Typisierung für bessere Wartbarkeit
- **Error Handling**: Robuste Fehlerbehandlung mit aussagekräftigen Meldungen

### **Testing**
```bash
# Tests ausführen
pytest

# Mit Coverage
pytest --cov=src/solr_helper
```

Siehe [docs/technical.md](docs/technical.md) für detaillierte technische Informationen.
