"""
import pandas as pd

def lade_hoehenkurve(csv_path):
    df = pd.read_csv(csv_path, sep=";")
    df = df.sort_values("Distance")  
    return df

def analyze_wildschoenau():
    return lade_hoehenkurve("fit-files/wildschoenau.csv")

def analyze_pillersee():
    return lade_hoehenkurve("fit-files/pillersee.csv")
    """


# src/analyze_hoehenkurve.py
import pandas as pd
from pathlib import Path

def _lade_hoehenkurve(csv_path: str | Path) -> pd.DataFrame:
    """
    Lädt eine CSV-Datei mit Höhenkurve, bereitet sie auf und sortiert nach Distanz.
    Erwartet Komma-getrennte Dateien wie

        "Duration","Distance","Latitude", ...

    Returns
    -------
    pd.DataFrame
        Distance [km]  (float)
        AltitudeCorrected [m]  (float)
        + alle übrigen Spalten
    """
    df = pd.read_csv(csv_path, sep=",", engine="python")

    # Leerzeichen und Anführungszeichen aus Spaltennamen entfernen
    df.columns = df.columns.str.strip()

    # Existenz der nötigen Spalten prüfen
    required = {"Distance", "AltitudeCorrected"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(
            f"Pflichtspalte(n) fehlen: {', '.join(missing)}. "
            f"Gefunden: {df.columns.tolist()}"
        )

    # Typkonvertierung: alles ist zunächst string –> float
    df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")  # km
    df["AltitudeCorrected"] = pd.to_numeric(df["AltitudeCorrected"], errors="coerce")

    # Reihen mit NaN verwerfen
    df = df.dropna(subset=list(required))

    return df.sort_values("Distance")

def analyze_wildschoenau() -> pd.DataFrame:
    return _lade_hoehenkurve("fit-files/wildschoenau.csv")

def analyze_pillersee() -> pd.DataFrame:
    return _lade_hoehenkurve("fit-files/pillersee.csv")
