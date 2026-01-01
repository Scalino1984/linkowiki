# LinkoWiki Admin v2.0 - Feature-Übersicht 🎉

## 🆕 Was ist neu?

### Interaktives Hauptmenü
Starte einfach `linkowiki-admin` ohne Parameter und du bekommst ein übersichtliches Menü:

```
╔════════════════════════════════════════════════════════════════════╗
║  🧠 LinkoWiki Admin - Hauptmenü                                    ║
╚════════════════════════════════════════════════════════════════════╝

  Session Management
    1    Session starten (read-only)
    2    Session starten (write-mode)
    3    Session Shell öffnen
    4    Session Status anzeigen
    5    Session beenden
    6    Session exportieren

  Wiki Browsing
    7    Wiki-Struktur anzeigen
    8    Wiki durchsuchen
    9    Letzte Änderungen anzeigen
    10   Kategorien & Statistiken

  AI Tools
    11   KI-Abfrage (einmalig)
    12   Wiki-Eintrag erstellen (geführt)

  Weitere Optionen
    h    Hilfe anzeigen
    q    Beenden
```

## 🎯 Schnellstart

### 1. Menü starten
```bash
linkowiki-admin
# oder
linkowiki-admin menu
```

### 2. Kommandozeile (wie bisher)
```bash
# Session starten
linkowiki-admin session start -w

# Session Shell
linkowiki-admin session shell

# Wiki anzeigen
linkowiki-admin tree

# KI-Abfrage
linkowiki-admin ai -p "Erkläre Docker" -w
```

## 🔥 Neue Features im Detail

### 📋 Session Export (Option 6)
Exportiert die komplette Session als Markdown-Datei:
- Conversation History
- Angehängte Dateien
- Durchgeführte Änderungen
- Ausstehende Aktionen

Dateien werden gespeichert unter: `session_exports/session_YYYYMMDD_HHMMSS.md`

### 🔍 Wiki durchsuchen (Option 8)
Volltextsuche durch alle Wiki-Einträge:
```
Suchbegriff: docker
✓ 3 Treffer gefunden:

▸ linux/docker
  Line 5: Docker ist eine Container-Plattform...
  Line 12: docker run -d nginx
  ... und 4 weitere

▸ dev/deployment
  Line 8: Deployment mit Docker Compose
```

### 📅 Letzte Änderungen (Option 9)
Zeigt die 15 zuletzt bearbeiteten Dateien:
```
▸ linux/systemctl (2026-01-01 12:30)
▸ security/firewall (2025-12-31 18:45)
▸ dev/git (2025-12-31 15:20)
```

### 📊 Statistiken (Option 10)
Übersicht über dein Wiki:
```
Gesamt:
  Dateien: 42
  Größe: 156.3 KB
  Kategorien: 5

Nach Kategorie:
  linux                8 Dateien   45.2 KB
  security             5 Dateien   23.1 KB
  dev                 12 Dateien   67.8 KB
```

### 📝 Geführte Wiki-Erstellung (Option 12)
Schritt-für-Schritt Assistent für neue Einträge:

1. **Kategorie wählen** (mit Vorschlägen aus existierenden)
2. **Thema eingeben**
3. **Inhalt beschreiben**
4. **Optional: Kontextdatei anhängen**
5. **KI erstellt strukturierten Eintrag**

## 🎨 Verbesserte UI

### Session Shell
```
linkowiki ✓ ❯ erstelle ein linux wiki für systemctl

You
──────────────────────────────────────────────────────────────────────
erstelle ein linux wiki für systemctl

Assistant
──────────────────────────────────────────────────────────────────────
Ich schlage vor, einen Wiki-Eintrag unter linux/systemctl anzulegen.
Der Eintrag sollte folgende Bereiche abdecken:
- Grundlegende Befehle
- Service Management
- Unit Files
- Häufige Probleme

Soll ich den Eintrag erstellen?

📋 Vorgeschlagene Aktionen
──────────────────────────────────────────────────────────────────────
  ▸ CREATE linux/systemctl

  → Tippe apply zum Ausführen oder diskutiere weiter
```

### Farbcodierung
- 🟢 **Grün**: Erfolg, Aktiv
- 🔴 **Rot**: Fehler, Inaktiv
- 🟡 **Gelb**: Warnung, Hinweis
- 🔵 **Cyan**: Kommandos, Kategorien
- 🟣 **Magenta**: Assistant-Antworten

## 🚀 Tipps & Tricks

### 1. Write-Modus im Prompt
Der Prompt zeigt den aktuellen Modus:
- `linkowiki ✓ ❯` = Write-Modus aktiv
- `linkowiki ✗ ❯` = Read-only

### 2. Session Commands
Innerhalb der Session Shell:
```
help        Zeigt alle Kommandos
apply       Führt vorgeschlagene Aktionen aus
reject      Verwirft Aktionen
why         Fragt nach Begründung
options     Zeigt Alternativen
:tree       Wiki-Struktur
:files      Angehängte Dateien
:write on   Write-Modus aktivieren
```

### 3. Schnelle Navigation
Im Hauptmenü:
- Tippe einfach die Nummer
- `h` für Hilfe
- `q` zum Beenden

### 4. Session Export nutzen
Exportiere wichtige Sessions für:
- Dokumentation
- Teilen mit Team
- Audit-Trail
- Backup

## 📖 Weitere Dokumentation

- `doc/SESSION_AI.md` - Session Shell Dokumentation
- `doc/IMPROVEMENTS.md` - Geplante Features & Roadmap
- `CONTRIBUTING.md` - Contribution Guidelines

## 🐛 Bekannte Einschränkungen

- Nur eine Session gleichzeitig
- Suche ohne Regex-Support
- Export nur als Markdown
- Keine Versionskontrolle integriert (noch)

## 🔮 Kommende Features

Siehe `doc/IMPROVEMENTS.md` für komplette Roadmap.

Highlights:
- Git-Integration (Auto-Commit)
- Tag-System
- Session Snapshots
- Web-UI
- Multi-Session Support

---

**Version:** 2.0  
**Datum:** 2026-01-01  
**Autor:** LinkoWiki Team
