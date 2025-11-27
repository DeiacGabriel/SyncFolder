# 🔄 Bi-Directional Folder Sync App

Eine moderne Desktop-Anwendung zur automatischen, beidseitigen Synchronisierung von Ordnern in Echtzeit. Entwickelt mit Python für Windows und Linux.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-green)

## ✨ Funktionen

* **Echtzeit-Synchronisierung:** Änderungen in Ordner A werden sofort nach Ordner B übertragen und umgekehrt.
* **Bi-Direktional:** Funktioniert in beide Richtungen gleichzeitig (A ↔ B).
* **Loop-Prevention:** Intelligente Erkennung verhindert Endlosschleifen ("Ping-Pong-Effekt") beim Kopieren.
* **Verborgene Dateien:** Synchronisiert auch versteckte Dateien (z.B. `.git`, `.config`).
* **Manueller Sync:** Button zum manuellen Abgleich (falls die App ausgeschaltet war).
* **Moderne GUI:** Dunkles Design ("Dark Mode").

---

## 🛠 Installation

### Voraussetzungen
Du benötigst [Python 3](https://www.python.org/).

### Schritt 1: Repository klonen / Ordner erstellen
Lege die Datei `sync_app.py` in einen Ordner deiner Wahl.

### Schritt 2: System-Abhängigkeiten installieren

**Für Windows:**
Windows bringt `tkinter` meistens schon mit. Du kannst direkt zu Schritt 3 gehen.

**Für Linux (Ubuntu / Mint / Debian):**
Da du Linux nutzt, musst du `tkinter` oft separat als Systempaket installieren, da es die Basis für die GUI ist:

```bash
sudo apt-get update
sudo apt-get install python3-tk

# Im Projektordner:
python3 -m venv .venv
source .venv/bin/activate  # Unter Windows: .venv\Scripts\activate

# Pakete installieren
pip install customtkinter watchdog

python sync_app.py