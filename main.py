
import streamlit as st
import plotly.graph_objects as go
import pydeck as pdk
import pandas as pd
from PIL import Image
from src.analyze_hoehenkurve import analyze_wildschoenau, analyze_pillersee
from src.analyze_data_GPS import analyze_wildschoenau as analyze_gps_wildschoenau, analyze_pillersee as analyze_gps_pillersee
from src.ekgdata import EKGdata
from src.person import Person
from src.analyze_activity_data import dataplot, dataframe

# Streamlit-Seitenkonfiguration
st.set_page_config(page_title="GPX & Höhenkurve & EKG Analyse", layout="centered")
st.title("GPX, Höhenkurve & EKG Analyse")

# --- GPX-Analyse und Höhenkurve ---
st.header("GPX Analyse und Höhenkurve")
tour = st.selectbox("Wähle eine Tour", ("Wildschönau", "Pillersee"))

# GPX-Daten laden
try:
    track_data = analyze_gps_wildschoenau() if tour == "Wildschönau" else analyze_gps_pillersee()
    st.subheader(f"Tour: {tour}")
    st.write(f"Gesamtdistanz: {track_data['total_distance_km']} km")
    st.write(f"Anzahl Trackpunkte: {track_data['point_count']}")

    # PyDeck-Karte anzeigen
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
                map_style="mapbox://styles/mapbox/outdoors-v11"
            )
        )
    else:
        st.write("Keine Koordinaten gefunden.")
except Exception as e:
    st.error(f"Fehler beim Laden der GPX-Daten: {e}")
    st.stop()

# Höhenkurve laden und anzeigen
try:
    df = analyze_wildschoenau() if tour == "Wildschönau" else analyze_pillersee()
except Exception as e:
    st.error(f"Fehler beim Laden der Höhenkurve-Daten: {e}")
    st.stop()

# Doppelte Distance-Werte entfernen und sortieren
df = df.drop_duplicates(subset='Distance').sort_values('Distance')

# Daten interpolieren für mehr Referenzpunkte
new_distance = pd.Series(range(int(df['Distance'].min() * 1000), 
                              int(df['Distance'].max() * 1000) + 1)) / 1000
df = pd.DataFrame({'Distance': new_distance}).merge(
    df[['Distance', 'AltitudeCorrected']], 
    on='Distance', 
    how='left'
).interpolate(method='linear')

# Steigung in Prozent berechnen
df['Slope'] = (df['AltitudeCorrected'].diff() / (df['Distance'].diff() * 1000)) * 100
df['Slope'] = df['Slope'].fillna(0)

# Plotly-Figur für Höhenkurve erstellen
fig = go.Figure(
    data=[
        go.Scatter(
            x=df['Distance'],
            y=df['AltitudeCorrected'],
            mode='lines',
            line=dict(color='blue', width=2),
            hovertemplate='Distanz: %{x:.2f} km<br>Höhe: %{y:.2f} m<br>Steigung: %{customdata:.2f}%',
            customdata=df['Slope']
        )
    ],
    layout=dict(
        title=f"Höhenprofil: {tour}",
        xaxis_title="Distanz (km)",
        yaxis_title="Höhe (m)",
        showlegend=False,
        hovermode='x unified'
    )
)

# Höhenkurve anzeigen
st.plotly_chart(fig, use_container_width=True)

# --- Personen- & EKG-Analyse ---
st.header("Personen- & EKG-Analyse")

# Personen-Daten laden
persons = Person.get_person_data()
person_names = Person.get_person_list(persons)
selected_name = st.selectbox("Wähle eine Person", options=person_names)
selected_person_data = Person.find_person_data_by_name(str(selected_name))

# Bild anzeigen
st.image(Image.open(selected_person_data.picture_path), caption=selected_name)

# Geburtsjahr und Alter anzeigen
st.write(f"Geburtsjahr: {selected_person_data.date_of_birth}")
st.write(f"Alter: {selected_person_data.calc_age()} Jahre")

# Testdatum auswählen
selected_test = st.selectbox(
    "Wähle einen EKG-Test",
    options=[str(i + 1) for i in range(len(selected_person_data.ekg_tests))]
)
testdatum = selected_person_data.ekg_tests[int(selected_test)-1]["date"] if selected_person_data.ekg_tests else None
st.write(f"Datum des Tests: {testdatum}")

# Maximale Herzfrequenz eingabe
hr_max = st.number_input("Maximale Herzfrequenz", min_value=100, max_value=250, value=int(selected_person_data.hr_max), step=1)

# Analyse-Plot anzeigen
st.plotly_chart(dataplot(hr_max))

# Zonenstatistik berechnen und anzeigen
zone_minutes = (dataframe["Zone"].value_counts() / 60)
zone_minutes.index.name = "Zone"
zone_minutes.name = "Dauer (Minuten)"

zone_power = dataframe.groupby("Zone")["PowerOriginal"].mean()
zone_stats = zone_minutes.to_frame().join(zone_power.rename("Ø Power (W)"))

st.write("## Zonenstatistik")
st.dataframe(zone_stats)

# EKG-Daten verarbeiten
if selected_person_data.ekg_tests:
    ekg_obj = EKGdata(selected_person_data.ekg_tests[0])
    ekg_obj.find_peaks()
    hr_est = ekg_obj.estimate_hr()
    st.write(f"Geschätzte Herzfrequenz aus EKG: {hr_est:.1f} bpm")
else:
    st.write("Keine EKG-Daten für diese Person verfügbar.")
