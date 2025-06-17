"""
import streamlit as st
import pydeck as pdk
from src.analyze_data_GPS import analyze_wildschoenau, analyze_pillersee

st.title("GPX Analyse")

# Auswahlbox für die Tour
tour = st.selectbox(
    "Wähle eine Tour",
    ("Wildschönau", "Pillersee")
)

# Daten laden je nach Auswahl
if tour == "Wildschönau":
    track_data = analyze_wildschoenau()
else:
    track_data = analyze_pillersee()

st.header(tour)
st.write(f"Gesamtdistanz: {track_data['total_distance_km']} km")
st.write(f"Anzahl Trackpunkte: {track_data['point_count']}")

if track_data["coordinates"]:
    lats = [lat for lon, lat in track_data["coordinates"]]
    lons = [lon for lon, lat in track_data["coordinates"]]
    midpoint = [sum(lats)/len(lats), sum(lons)/len(lons)]

    layer = pdk.Layer(
        "PathLayer",
        data=[{"path": track_data["coordinates"], "name": tour}],
        get_path="path",
        get_color=[255, 0, 0],
        width_scale=10,
        width_min_pixels=3,
    )

    view_state = pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=13,
        pitch=0,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/outdoors-v11"  # <-- Echte Karte im Hintergrund!
        )
    )
else:
    st.write("Keine Koordinaten gefunden.")

"""
import streamlit as st
from PIL import Image
from datetime import date, datetime
from src.ekgdata import EKGdata
from src.person import Person
from src.analyze_activity_data import dataplot, dataframe

st.write("# Hello, Streamlit!")
st.write("## Zweite Ueberschrift")
st.write("Dies ist eine einfache Streamlit App mit Klassen.")

# Personen laden und Auswahl anzeigen
persons = Person.get_person_data()
person_names = Person.get_person_list(persons)
selected_name = st.selectbox("Wähle eine Person", options=person_names)
#selected_person = next(p for p in persons if p.get_full_name() == selected_name)
selected_person_data = Person.find_person_data_by_name(str(selected_name))
# Bild anzeigen
st.image(Image.open(selected_person_data.picture_path), caption=selected_name)

st.write(f"Geburtsjahr: {selected_person_data.date_of_birth}")
st.write(f"Alter: {selected_person_data.calc_age()} Jahre")
# Testdatum anzeigen
selected_test = st.selectbox("Wähle einen EKG-Test", options=[str(i + 1) for i in range(len(selected_person_data.ekg_tests))])
testdatum = selected_person_data.ekg_tests[int(selected_test)-1]["date"] if selected_person_data.ekg_tests else None
st.write(f"Datum des Tests: {testdatum}")

# Maximalpuls-Eingabe (aus Klasse vorbelegen)
hr_max = st.number_input("Maximale Herzfrequenz", min_value=100, max_value=250, value=int(selected_person_data.hr_max), step=1)

# Analyse-Plot anzeigen (öffnet kein extra Fenster!)
st.plotly_chart(dataplot(hr_max))

# Zonenstatistik berechnen und anzeigen
zone_minutes = (dataframe["Zone"].value_counts() / 60)
zone_minutes.index.name = "Zone"
zone_minutes.name = "Dauer (Minuten)"

zone_power = dataframe.groupby("Zone")["PowerOriginal"].mean()
zone_stats = zone_minutes.to_frame().join(zone_power.rename("Ø Power (W)"))

st.write("## Zonenstatistik")
st.dataframe(zone_stats)

# Beispiel: Erstes EKG der ausgewählten Person verwenden
if selected_person_data.ekg_tests:
    ekg_obj = EKGdata(selected_person_data.ekg_tests[0])
    ekg_obj.find_peaks()
    hr_est = ekg_obj.estimate_hr()
    st.write(f"Geschätzte Herzfrequenz aus EKG: {hr_est:.1f} bpm")
else:
    st.write("Keine EKG-Daten für diese Person verfügbar.")
