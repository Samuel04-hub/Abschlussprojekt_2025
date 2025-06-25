import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from PIL import Image
from src.analyze_fit_files_tour import analyze_all_fit_files
from src.analyze_hoehenkurve import analyze_wildschoenau, analyze_pillersee
from src.analyze_data_GPS import analyze_wildschoenau as analyze_gps_wildschoenau, analyze_pillersee as analyze_gps_pillersee
from src.ekgdata import EKGdata
from src.person import Person
from src.analyze_activity_data import dataplot, dataframe

# Streamlit-Seitenkonfiguration
st.set_page_config(page_title="Touren & EKG Analyse", layout="centered")
st.title("Touren- und EKG-Analyse")

# Sidebar für Navigation
page = st.sidebar.selectbox("Wähle eine Analyse", ["Touren-Analyse", "Personen- & EKG-Analyse"])

# --- Touren-Analyse (FIT, GPX, Höhenkurve) ---
if page == "Touren-Analyse":
    st.header("Touren-Analyse")

    # --- FIT-Dateien Analyse ---
    st.subheader("Analyse von FIT-Dateien")
    directory = "C:/Abschlussprojekt_2025/fit-files"
    results = analyze_all_fit_files(directory)

    if results:
        tour_names = [r['file_name'].replace('.csv', '') for r in results]
        selected_fit_tour = st.selectbox("Wähle eine FIT-Tour aus:", tour_names, key="fit_tour_select")
        selected_result = next((r for r in results if r['file_name'] == f"{selected_fit_tour}.csv"), None)

        if selected_result:
            table_data = {
                "Tour": [selected_fit_tour],
                "Höhenmeter (m)": [selected_result['elevation_gain_m']],
                "Gesamtdistanz (km)": [selected_result['total_distance_km']],
                "Durchschnittsherzfrequenz (bpm)": [round(sum(selected_result['heart_rate']) / len(selected_result['heart_rate']), 2)],
                "Durchschnittsleistung (Watt)": [round(sum(selected_result['power']) / len(selected_result['power']), 2)]
            }
            df = pd.DataFrame(table_data)
            st.subheader(f"Zusammenfassung der Tour: {selected_fit_tour}")
            st.table(df)

            df_csv = pd.read_csv(f"{directory}/{selected_fit_tour}.csv")
            st.subheader(f"Herzfrequenz ({selected_fit_tour})")
            fig_hr = px.line(
                x=df_csv['Distance'],
                y=selected_result['heart_rate'],
                title=f"Herzfrequenz ({selected_fit_tour})",
                labels={"x": "Distanz (km)", "y": "Herzfrequenz (bpm)"}
            )
            st.plotly_chart(fig_hr, use_container_width=True)

            st.subheader(f"Leistung ({selected_fit_tour})")
            fig_power = px.line(
                x=df_csv['Distance'],
                y=selected_result['power'],
                title=f"Leistung ({selected_fit_tour})",
                labels={"x": "Distanz (km)", "y": "Leistung (Watt)"}
            )
            st.plotly_chart(fig_power, use_container_width=True)
        else:
            st.error(f"Keine Daten für die ausgewählte Tour {selected_fit_tour} gefunden.")
    else:
        st.error("Keine gültigen FIT-Dateien gefunden.")

    # --- GPX-Analyse und Höhenkurve ---
    st.subheader("GPX-Analyse und Höhenkurve")
    tour = st.selectbox("Wähle eine GPX-Tour", ("Wildschönau", "Pillersee"), key="gpx_tour_select")

    # GPX-Daten laden
    try:
        track_data = analyze_gps_wildschoenau() if tour == "Wildschönau" else analyze_gps_pillersee()
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

    df = df.drop_duplicates(subset='Distance').sort_values('Distance')
    new_distance = pd.Series(range(int(df['Distance'].min() * 1000), 
                                  int(df['Distance'].max() * 1000) + 1)) / 1000
    df = pd.DataFrame({'Distance': new_distance}).merge(
        df[['Distance', 'AltitudeCorrected']], 
        on='Distance', 
        how='left'
    ).interpolate(method='linear')

    df['Slope'] = (df['AltitudeCorrected'].diff() / (df['Distance'].diff() * 1000)) * 100
    df['Slope'] = df['Slope'].fillna(0)

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
    st.plotly_chart(fig, use_container_width=True)

# --- Personen- & EKG-Analyse ---
elif page == "Personen- & EKG-Analyse":
    st.header("Personen- & EKG-Analyse")

    persons = Person.get_person_data()
    person_names = Person.get_person_list(persons)
    selected_name = st.selectbox("Wähle eine Person", options=person_names, key="person_select")
    selected_person_data = Person.find_person_data_by_name(str(selected_name))

    st.image(Image.open(selected_person_data.picture_path), caption=selected_name)
    st.write(f"Geburtsjahr: {selected_person_data.date_of_birth}")
    st.write(f"Alter: {selected_person_data.calc_age()} Jahre")

    selected_test = st.selectbox(
        "Wähle einen EKG-Test",
        options=[str(i + 1) for i in range(len(selected_person_data.ekg_tests))],
        key="ekg_test_select"
    )
    testdatum = selected_person_data.ekg_tests[int(selected_test)-1]["date"] if selected_person_data.ekg_tests else None
    st.write(f"Datum des Tests: {testdatum}")

    hr_max = st.number_input("Maximale Herzfrequenz", min_value=100, max_value=250, value=int(selected_person_data.hr_max), step=1, key="hr_max_input")
    st.plotly_chart(dataplot(hr_max))

    zone_minutes = (dataframe["Zone"].value_counts() / 60)
    zone_minutes.index.name = "Zone"
    zone_minutes.name = "Dauer (Minuten)"
    zone_power = dataframe.groupby("Zone")["PowerOriginal"].mean()
    zone_stats = zone_minutes.to_frame().join(zone_power.rename("Ø Power (W)"))

    st.subheader("Zonenstatistik")
    st.dataframe(zone_stats)

    if selected_person_data.ekg_tests:
        ekg_obj = EKGdata(selected_person_data.ekg_tests[0])
        ekg_obj.find_peaks()
        hr_est = ekg_obj.estimate_hr()
        st.write(f"Geschätzte Herzfrequenz aus EKG: {hr_est:.1f} bpm")
    else:
        st.write("Keine EKG-Daten für diese Person verfügbar.")



