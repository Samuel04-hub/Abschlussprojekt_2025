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