import json
import pandas as pd
import plotly.express as px
from person import Person

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

    def find_peaks(self, threshold=340):
        """
        Findet Peaks in den EKG-Daten und speichert sie als Attribut self.peaks.
        """
        values = self.df["Messwerte in mV"].values
        peaks = []
        for i in range(1, len(values) - 1):
            if values[i-1] < values[i] > values[i+1] and values[i] > threshold:
                peaks.append(i)
        self.peaks = peaks
        return peaks

    def plot_time_series(self):
        # Erstellt einen Line Plot der ersten 2000 Werte mit der Zeit auf der x-Achse
        fig = px.line(self.df.head(2000), x="Zeit in ms", y="Messwerte in mV")
        # Peaks anzeigen, falls vorhanden
        if self.peaks:
            peak_times = self.df.iloc[self.peaks]["Zeit in ms"]
            peak_values = self.df.iloc[self.peaks]["Messwerte in mV"]
            fig.add_scatter(x=peak_times, y=peak_values, mode='markers', marker=dict(color='red', size=8), name="Peaks")
        return fig

if __name__ == "__main__":
    input_persons = Person.load_person_data()
    ekg_obj = EKGdata.load_by_id(input_persons, 3)
    if ekg_obj:
        print("EKG geladen:", ekg_obj.id)
        print("Gefundene Peaks:", ekg_obj.find_peaks(340))
        fig = ekg_obj.plot_time_series()
        fig.show(renderer="browser")
        print("Plot erstellt.")
    else:
        print("Kein EKG mit dieser ID gefunden.")