# EKG-Anomalie-Analyse App

## Was macht die EKG-Anomalie-Analyse App genau?

Die **EKG-Anomalie-Analyse App** ist eine moderne, webbasierte Anwendung zur Auswertung und Visualisierung von EKG-Daten. Sie richtet sich an Mediziner:innen, Studierende und Entwickler:innen, die EKG-Signale analysieren und verstehen möchten. Die App bietet drei zentrale Funktionsbereiche:

### 1. Touren-Analyse
Hier kannst du sportliche Aktivitäten (z.B. Wanderungen oder Radtouren) auswerten. Die App liest GPS-Daten (z.B. aus FIT-Dateien), zeigt die zurückgelegte Strecke auf einer Karte, berechnet Höhenprofile und stellt wichtige Tourenstatistiken wie Distanz, Dauer und Höhenmeter übersichtlich dar.

### 2. Personen- & EKG-Test-Verwaltung
In diesem Bereich verwaltest du verschiedene Personen und deren EKG-Tests. Du kannst neue Personen anlegen, ihnen EKG-Messungen zuordnen und die Testergebnisse übersichtlich einsehen. So behältst du den Überblick über alle durchgeführten EKG-Analysen und kannst Vergleiche zwischen verschiedenen Tests oder Personen anstellen.

### 3. EKG-Anomalie-Analyse
Der Kern der App ist die Analyse von EKG-Signalen. Die App lädt EKG-Daten (z.B. aus dem MIT-BIH-Arrhythmie-Datensatz), stellt die Rohsignale (wie MLII und V1) grafisch dar und erkennt automatisch Herzrhythmus-Anomalien anhand medizinischer Annotationen. Die gefundenen Anomalien (z.B. ventrikuläre Extrasystolen, supraventrikuläre Extrasystolen, Fusionsschläge) werden in übersichtlichen Tabellen angezeigt, statistisch ausgewertet und mit klinischen Beschreibungen versehen. Du kannst die Ergebnisse filtern, exportieren und für weiterführende Analysen nutzen.

---

**Zusammengefasst:**  
Die App verbindet sportliche Aktivitätsdaten mit medizinischer EKG-Analyse. Sie hilft dir, Touren und EKG-Tests zu verwalten, EKG-Signale zu visualisieren und Anomalien schnell und zuverlässig zu erkennen und auszuwerten.

---

## Schnellstart

1. **Repository klonen**
    ```bash
    git clone <REPO-URL>
    cd Abschlussprojekt_2025
    ```

2. **PDM installieren (falls noch nicht vorhanden)**  
   PDM ist ein moderner Python-Paketmanager.
    ```bash
    pip install pdm
    ```

3. **Abhängigkeiten installieren**  
   Alle benötigten Bibliotheken sind in der `pyproject.toml` und der `pdm.lock` Datei definiert.
    ```bash
    pdm install
    ```

4. **App starten**
    ```bash
    streamlit run main.py
    ```

---

##  Benötigte Bibliotheken (Auszug aus pyproject.toml)

```toml
dependencies = [
    "gpxpy>=1.6.2",
    "streamlit>=1.45.1",
    "plotly>=6.1.2",
    "matplotlib>=3.10.3",
    "wfdb>=4.3.0"
]
requires-python = "==3.13.*"

## Wichtige Dateien

main.py – Hauptanwendung (Streamlit)

src/ – Enthält alle Analyse- und Hilfsmodule (z.B. für EKG, Touren, Personenverwaltung)

pyproject.toml – Projekt- und Abhängigkeitsverwaltung (PDM)

pdm.lock – Genaue Versionssicherung der Pakete

requirements.txt – Für Deployment auf Plattformen wie Heroku oder Streamlit Cloud


## Deployment
Für das Deployment auf Streamlit Cloud wird automatisch die requirements.txt verwendet.
