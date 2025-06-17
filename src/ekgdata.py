import json
import pandas as pd
import plotly.express as px
from src.person import Person
import numpy as np

class EKGdata:
    def __init__(self, ekg_dict):
        self.id = ekg_dict["id"]
        self.date = ekg_dict["date"]
        self.data = ekg_dict["result_link"]
        self.df = pd.read_csv(self.data, sep='\t', header=None, names=['Messwerte in mV','Zeit in ms'])
        self.df = self.df.iloc[:5000]
        self.peaks = []

    @staticmethod
    def load_by_id(input_persons, ekg_id):
        """
        Instanziiert einen EKG-Test anhand der ID und der Personen-Datenbank.
        Gibt ein EKGdata-Objekt zurück, wenn gefunden, sonst None.
        """
        for person in input_persons:
            for ekg in person["ekg_tests"]:
                if ekg["id"] == ekg_id:
                    return EKGdata(ekg)
        return None

    def find_peaks_old(self, threshold=340):
        """
        Findet Peaks in den EKG-Daten und speichert sie als Attribut self.peaks.
        """
        values = self.df["Messwerte in mV"].values
        peaks = []
        for i in range(1, len(values) - 1):
            if values[i-1] < values[i] > values[i+1] and values[i] > threshold:
                peaks.append(i)
        self.list_of_peaks = peaks
        return self.list_of_peaks
    
    def find_peaks(self, threshold=340):
        """
        Findet Peaks in den EKG-Daten und gibt eine Liste der Peak-Indizes zurück.
        """
        self.list_of_peaks = []
        
        for index, row in self.df.iterrows():
            if index == 0 or index == self.df.index.max():
                continue  # Erster und letzter Wert überspringen
            current_value = row["Messwerte in mV"]
            if current_value > self.df.iloc[index - 1]["Messwerte in mV"] and current_value >= self.df.iloc[index + 1]["Messwerte in mV"]:
                if current_value > threshold:
                    self.list_of_peaks.append(index)
        return self.list_of_peaks
    def estimate_hr(self):
      
        # Zeitpunkte der Peaks in ms
        peak_times = [self.df.iloc[self.list_of_peaks[i+1]]['Zeit in ms'] - self.df.iloc[self.list_of_peaks[i]]['Zeit in ms'] for i in range(len(self.list_of_peaks)-1)]
        rr_intervals = sum(peak_times)/len(peak_times)  # in ms
        #mean_rr = np.mean(rr_intervals)     # in ms
        if rr_intervals == 0:
            return 0
        hr = 60000 / rr_intervals # 60000 ms = 1 min
        return hr

    def plot_time_series(self):
        # Erstellt einen Line Plot der ersten 2000 Werte mit der Zeit auf der x-Achse
        self.fig = px.line(self.df, x="Zeit in ms", y="Messwerte in mV")
        # Peaks anzeigen, falls vorhanden
        if self.list_of_peaks:
            peak_times = self.df.iloc[self.list_of_peaks]["Zeit in ms"]
            peak_values = self.df.iloc[self.list_of_peaks]["Messwerte in mV"]
            self.fig.add_scatter(x=peak_times, y=peak_values, mode='markers', marker=dict(color='red', size=8), name="Peaks")
        return self.fig

if __name__ == "__main__":
    input_persons = Person.load_person_data()
    ekg_obj = EKGdata.load_by_id(input_persons, 1)
    if ekg_obj:
        print("EKG geladen:", ekg_obj.id)
        print("Gefundene Peaks:", ekg_obj.find_peaks(340))
        fig = ekg_obj.plot_time_series()
        fig.show(renderer="browser")
        print("Plot erstellt.")
    else:
        print("Kein EKG mit dieser ID gefunden.")
    list_of_peaks = ekg_obj.find_peaks(340)
    hr= ekg_obj.estimate_hr()
    print("Geschätzte Herzfrequenz:", hr)