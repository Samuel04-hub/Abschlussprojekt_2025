import pandas as pd
import os
from typing import Dict, List

def calculate_elevation_gain(altitudes: List[float]) -> float:
    """Berechnet die gesamte Höhenmeterzunahme (nur Anstiege)."""
    elevation_gain = 0.0
    for i in range(1, len(altitudes)):
        diff = altitudes[i] - altitudes[i-1]
        if diff > 0:
            elevation_gain += diff
    return elevation_gain

def analyze_fit_file(file_path: str) -> Dict:
    """Analysiert eine FIT-Datei (als CSV) und gibt die gewünschten Metriken zurück."""
    try:
        # CSV-Datei einlesen
        df = pd.read_csv(file_path)
        
        # Sicherstellen, dass die benötigten Spalten vorhanden sind
        required_columns = ['Distance', 'HeartRate', 'PowerCalculated', 'AltitudeCorrected']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Datei {file_path} enthält nicht alle erforderlichen Spalten.")
        
        # Metriken berechnen
        elevation_gain = calculate_elevation_gain(df['AltitudeCorrected'].tolist())  # Höhenmeter
        heart_rate = df['HeartRate'].tolist()  # Verlauf der Herzfrequenz
        power = df['PowerCalculated'].tolist()  # Verlauf der Leistung
        total_distance = df['Distance'].iloc[-1]  # Gesamtdistanz (km)
        
        # Ergebnisse in einem Dictionary speichern
        result = {
            'file_name': os.path.basename(file_path),
            'elevation_gain_m': round(elevation_gain, 2),
            'total_distance_km': round(total_distance, 2),
            'heart_rate': heart_rate,
            'power': power
        }
        
        return result
    
    except Exception as e:
        print(f"Fehler bei der Verarbeitung von {file_path}: {str(e)}")
        return {}

def analyze_all_fit_files(directory: str) -> List[Dict]:
    """Analysiert alle CSV-Dateien im angegebenen Verzeichnis."""
    results = []
    for file_name in os.listdir(directory):
        if file_name.endswith('.csv'):
            file_path = os.path.join(directory, file_name)
            result = analyze_fit_file(file_path)
            if result:
                results.append(result)
    return results