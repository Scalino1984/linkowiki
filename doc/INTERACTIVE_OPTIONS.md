# Session Shell v2.0 - Interaktive Optionen & Vollbild-Modus 🎨

## 🆕 Was ist neu?

### 1. **Interaktive Optionen statt Fragen**

Der Assistent bietet jetzt **nummerierte, anklickbare Optionen** an, die du direkt per Zahl auswählen kannst.

#### Vorher (v1.0):
```
Assistant: Wie kann ich helfen?
❓ Rückfragen:
  1. Gibt es ein spezielles Thema, bei dem ich helfen kann?

linkowiki ✓ ❯ _
```

#### Jetzt (v2.0):
```
Assistant: Wie kann ich dir helfen? Wähle aus den folgenden Optionen:

💡 Wähle eine Option:
──────────────────────────────────────────────────────────────────────
  1. Neuen Wiki-Eintrag erstellen
     Erstelle einen neuen strukturierten Wiki-Eintrag

  2. Existierenden Eintrag bearbeiten
     Suche und bearbeite einen bestehenden Eintrag

  3. Wiki durchsuchen
     Finde Informationen in existierenden Einträgen

  4. Kategorien anzeigen
     Zeige alle verfügbaren Wiki-Kategorien

Tippe die Nummer oder schreibe deine eigene Nachricht

linkowiki ✓ ❯ _
```

### 2. **Intelligente Kontextabhängige Optionen**

Der Assistent passt die Optionen an deine Anfrage an:

#### Beispiel: "erstelle docker wiki"
```
Assistant: Ich kann dir beim Docker-Wiki helfen! Was möchtest du abdecken?

💡 Wähle eine Option:
──────────────────────────────────────────────────────────────────────
  1. Grundlagen-Eintrag (Installation, erste Schritte)
     Perfekt für Einsteiger

  2. Docker Compose Tutorial
     Multi-Container Anwendungen orchestrieren

  3. Best Practices & Security
     Produktionsreife Container-Deployments

  4. Troubleshooting Guide
     Häufige Probleme und Lösungen

Tippe die Nummer oder schreibe deine eigene Nachricht
```

### 3. **Vollbild-Modus & Clean Screen**

Neue Kommandos für bessere Übersicht:

```bash
:clear        # Bildschirm leeren, Optionen bleiben sichtbar
:fullscreen   # Vollbild-Modus aktualisieren
```

### 4. **Persistente Statusleiste**

Am Anfang jeder Session siehst du jetzt eine Statusleiste:

```
 LinkoWiki Session Shell 
▓ Mode: Write  |  Files: 2  |  Pending: 1
──────────────────────────────────────────────────────────────────────
```

- **Mode**: Zeigt ob Write-Modus aktiv ist
- **Files**: Anzahl angehängter Dateien
- **Pending**: Anzahl ausstehender Aktionen

### 5. **Nummer-Auswahl**

Tippe einfach die Nummer einer Option:

```
linkowiki ✓ ❯ 1

→ Gewählt: Neuen Wiki-Eintrag erstellen

You
──────────────────────────────────────────────────────────────────────
Neuen Wiki-Eintrag erstellen

Assistant
──────────────────────────────────────────────────────────────────────
Super! Lass uns einen neuen Eintrag erstellen...
```

## 🎯 Wie es funktioniert

### System Prompt Verbesserung

Der Assistent wurde trainiert, **immer konkrete Optionen anzubieten**:

```python
"WICHTIG - Interaktive Optionen:
- Biete IMMER konkrete, nummerierte Optionen an
- Jede Option hat: label (kurz) und description (erklärt was passiert)
- Optionen sind Aktionen/Wege, die der Nutzer wählen kann
- Bei unklarer Anfrage: biete mehrere Wege an
- Bei klarer Anfrage: biete nächste Schritte an"
```

### Datenstruktur

```python
class Option(BaseModel):
    label: str              # Kurzer Titel
    description: str | None  # Optionale Erklärung

class AIResult(BaseModel):
    message: str
    options: list[Option] = []  # Interaktive Optionen
    actions: list[Action] = []
```

## 🔥 Beispiel-Dialoge

### Szenario 1: Neuer Nutzer startet Session

```
linkowiki ✓ ❯ hallo

You
──────────────────────────────────────────────────────────────────────
hallo

Assistant
──────────────────────────────────────────────────────────────────────
Hallo! Willkommen im LinkoWiki. Ich helfe dir beim Verwalten deines
persönlichen Wikis. Was möchtest du tun?

💡 Wähle eine Option:
──────────────────────────────────────────────────────────────────────
  1. Neuen Wiki-Eintrag erstellen
     Lege ein neues Thema an

  2. Existierende Einträge durchsuchen
     Finde vorhandene Informationen

  3. Wiki-Struktur anzeigen
     Übersicht aller Kategorien und Themen

  4. Über LinkoWiki lernen
     Was kann ich alles tun?

Tippe die Nummer oder schreibe deine eigene Nachricht

linkowiki ✓ ❯ 1
```

### Szenario 2: Spezifische Anfrage

```
linkowiki ✓ ❯ ich brauche ein linux systemctl cheatsheet

You
──────────────────────────────────────────────────────────────────────
ich brauche ein linux systemctl cheatsheet

Assistant
──────────────────────────────────────────────────────────────────────
Perfekt! Ich erstelle dir ein systemctl Cheatsheet. Welcher Fokus?

💡 Wähle eine Option:
──────────────────────────────────────────────────────────────────────
  1. Grundbefehle (start, stop, status, restart)
     Die wichtigsten Service-Kommandos

  2. Unit Management (enable, disable, mask)
     Dienste dauerhaft konfigurieren

  3. Erweiterte Features (journal, targets, dependencies)
     Für fortgeschrittene Nutzer

  4. Vollständiges Cheatsheet (alles oben)
     Komplette Referenz

Tippe die Nummer oder schreibe deine eigene Nachricht

linkowiki ✓ ❯ 4

→ Gewählt: Vollständiges Cheatsheet (alles oben)

Assistant
──────────────────────────────────────────────────────────────────────
Verstanden! Ich erstelle ein vollständiges systemctl Cheatsheet unter
linux/systemctl mit allen wichtigen Bereichen.

📋 Vorgeschlagene Aktionen
──────────────────────────────────────────────────────────────────────
  ▸ CREATE linux/systemctl

  → Tippe apply zum Ausführen oder diskutiere weiter

linkowiki ✓ ❯ apply
```

### Szenario 3: Mehrdeutige Anfrage

```
linkowiki ✓ ❯ docker

You
──────────────────────────────────────────────────────────────────────
docker

Assistant
──────────────────────────────────────────────────────────────────────
Docker ist ein großes Thema! Was genau interessiert dich?

💡 Wähle eine Option:
──────────────────────────────────────────────────────────────────────
  1. Docker installieren
     Setup auf verschiedenen Systemen

  2. Docker Basics
     Container erstellen, verwalten, debuggen

  3. Docker Compose
     Multi-Container Apps definieren

  4. Dockerfile Best Practices
     Effiziente Images bauen

  5. Docker Networking
     Container-Kommunikation verstehen

  6. Docker in Production
     Security, Monitoring, Orchestration

Tippe die Nummer oder schreibe deine eigene Nachricht
```

## 💡 Best Practices

### Für Nutzer

1. **Nutze Nummern** - Schneller als Tippen
2. **Eigene Antworten möglich** - Du bist nicht auf Optionen beschränkt
3. **`:clear` verwenden** - Wenn Bildschirm zu voll wird
4. **Optionen durchlesen** - Descriptions geben Kontext

### Für KI-Training

Der Assistent wurde trainiert auf:

```
BEISPIELE für gute Optionen:

Bei 'hallo':
- Option: 'Neuen Wiki-Eintrag erstellen'
- Option: 'Existierenden Eintrag bearbeiten'
- Option: 'Wiki durchsuchen'
- Option: 'Kategorien anzeigen'

Bei 'erstelle docker wiki':
- Option: 'Grundlagen-Eintrag (Installation, erste Schritte)'
- Option: 'Docker Compose Tutorial'
- Option: 'Best Practices & Security'
- Option: 'Troubleshooting Guide'
```

## 🚀 Neue Kommandos

| Kommando | Beschreibung |
|----------|--------------|
| `1, 2, 3...` | Wähle nummerierte Option |
| `:clear` | Bildschirm leeren, Optionen behalten |
| `:fullscreen` | Vollbild-Modus aktualisieren |
| `:help` | Alle Kommandos anzeigen |

## 🎨 UI-Verbesserungen

### Statusleiste
```
 LinkoWiki Session Shell 
▓ Mode: Write  |  Files: 2  |  Pending: 1
──────────────────────────────────────────────────────────────────────
```

### Options-Box
```
💡 Wähle eine Option:
──────────────────────────────────────────────────────────────────────
  1. Option Eins
     Beschreibung der ersten Option

  2. Option Zwei
     Beschreibung der zweiten Option

Tippe die Nummer oder schreibe deine eigene Nachricht
```

### Bestätigung bei Auswahl
```
→ Gewählt: Option Eins
```

## 🔮 Kommende Features

- [ ] **Option-Historie** - Zurück zu vorherigen Optionen
- [ ] **Multi-Select** - Mehrere Optionen kombinieren (z.B. "1,3,5")
- [ ] **Smart Suggestions** - Basierend auf Wiki-Inhalt
- [ ] **Quick Actions** - Häufige Tasks als Optionen
- [ ] **Context Menu** - Rechtsklick in Terminal (wenn supported)
- [ ] **Option-Preview** - Zeige was passiert vor Auswahl
- [ ] **Favoriten-Optionen** - Häufig genutzte speichern

## 📊 Vergleich: Vorher vs. Nachher

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Rückfragen | ✓ Textbasiert | ✓ Nummeriert |
| Interaktivität | ⚠️ Nur Freitext | ✓ Nummer-Auswahl |
| Optionen-Kontext | ✗ Keine Descriptions | ✓ Mit Erklärungen |
| Vollbild-Modus | ✗ Nicht verfügbar | ✓ `:clear`, `:fullscreen` |
| Statusleiste | ✗ Nur im Prompt | ✓ Persistent sichtbar |
| Option-Bestätigung | ✗ Nicht sichtbar | ✓ "→ Gewählt: ..." |

## 🎯 Fazit

Die Session Shell ist jetzt:
- **Interaktiver** - Optionen per Nummer wählbar
- **Benutzerfreundlicher** - Klare Vorschläge statt vager Fragen
- **Kontextbewusst** - Passende Optionen je nach Situation
- **Professioneller** - Statusleiste, Vollbild, Clean UI

Genau wie **GitHub Copilot**, **Codex** und **Claude**! 🚀

---

**Version:** 2.0  
**Datum:** 2026-01-01  
**Autor:** LinkoWiki Team
