"""
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


import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.analyze_anomalien import analyze_ecg_anomalies

def main():
    st.title("EKG-Verlauf und Anomalie-Auswertung: MIT-BIH Datensatz 208")
    
    # Load and analyze data
    try:
        signal_df, annotation_df, anomaly_summary = analyze_ecg_anomalies('208', data_dir='mitdb/1.0.0')
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        st.info("Stelle sicher, dass du eine Internetverbindung hast oder die Dateien 208.dat, 208.hea und 208.atr lokal in C:\\Abschlussprojekt_2025 verfügbar sind.")
        return
    
    # Sidebar for time range selection
    st.sidebar.header("Zeitfenster auswählen")
    max_time = signal_df['Time (s)'].max()
    time_range = st.sidebar.slider(
        "Zeitbereich (Sekunden)",
        min_value=0.0,
        max_value=float(max_time),
        value=(0.0, min(30.0, max_time)),  # Default: Erste 30 Sekunden
        step=0.1
    )
    
    # Filter signal and annotations for selected time range
    filtered_signal_df = signal_df[
        (signal_df['Time (s)'] >= time_range[0]) & 
        (signal_df['Time (s)'] <= time_range[1])
    ]
    filtered_annotation_df = annotation_df[
        (annotation_df['Time (s)'] >= time_range[0]) & 
        (annotation_df['Time (s)'] <= time_range[1]) & 
        (annotation_df['Symbol'] != 'N')  # Nur Anomalien
    ]
    
    # Calculate statistics
    total_beats = len(annotation_df)
    anomaly_beats = len(annotation_df[annotation_df['Symbol'] != 'N'])
    anomaly_rate = (anomaly_beats / total_beats * 100) if total_beats > 0 else 0
    duration_minutes = max_time / 60
    anomaly_freq_per_min = anomaly_beats / duration_minutes if duration_minutes > 0 else 0
    
    # Display general statistics
    st.header("Allgemeine Statistiken")
    st.write(f"**Gesamtdauer**: {max_time:.2f} Sekunden ({duration_minutes:.2f} Minuten)")
    st.write(f"**Gesamtzahl der Schläge**: {total_beats}")
    st.write(f"**Anzahl der Anomalien**: {anomaly_beats} ({anomaly_rate:.2f}% der Schläge)")
    st.write(f"**Anomalien pro Minute**: {anomaly_freq_per_min:.2f}")
    
    # Plot ECG signals
    st.header("EKG-Signale mit Anomalien")
    
    # Plot channel 1 (MLII)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=filtered_signal_df['Time (s)'],
        y=filtered_signal_df['MLII (mV)'],
        mode='lines',
        name='MLII Signal',
        line=dict(color='blue')
    ))
    if not filtered_annotation_df.empty:
        anomaly_times = filtered_annotation_df['Time (s)']
        anomaly_values = filtered_signal_df.set_index('Time (s)')['MLII (mV)'].reindex(anomaly_times, method='nearest').values
        fig1.add_trace(go.Scatter(
            x=anomaly_times,
            y=anomaly_values,
            mode='markers',
            name='Anomalien',
            marker=dict(symbol='x', size=10, color='red'),
            text=filtered_annotation_df['Description'] + " (" + filtered_annotation_df['Time (s)'].round(2).astype(str) + "s)",
            hoverinfo='text'
        ))
    fig1.update_layout(
        title='EKG-Signal (MLII)',
        xaxis_title='Zeit (s)',
        yaxis_title='Amplitude (mV)',
        hovermode='x',
        showlegend=True
    )
    st.plotly_chart(fig1, use_container_width=True)
    
        # Plot channel 2 (V1)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=filtered_signal_df['Time (s)'],
        y=filtered_signal_df['V1 (mV)'],
        mode='lines',
        name='V1 Signal',
        line=dict(color='green')
    ))
    if not filtered_annotation_df.empty:
        anomaly_values_v1 = filtered_signal_df.set_index('Time (s)')['V1 (mV)'].reindex(anomaly_times, method='nearest').values
        fig2.add_trace(go.Scatter(
            x=anomaly_times,
            y=anomaly_values_v1,
            mode='markers',
            name='Anomalien',
            marker=dict(symbol='x', size=10, color='red'),
            text=filtered_annotation_df['Description'] + " (" + filtered_annotation_df['Time (s)'].round(2).astype(str) + "s)",
            hoverinfo='text'
        ))
    fig2.update_layout(
        title='EKG-Signal (V1)',
        xaxis_title='Zeit (s)',
        yaxis_title='Amplitude (mV)',
        hovermode='x',
        showlegend=True
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Display anomaly summary with clinical context
    st.header("Zusammenfassung der Anomalien")
    clinical_context = {
        'V': "Ventrikuläre Extrasystole (VEB): Vorzeitiger Schlag aus den Ventrikeln. Häufige VEBs können auf Herzkrankheiten hinweisen.",
        'S': "Supraventrikuläre Extrasystole (SVEB): Vorzeitiger Schlag aus den Vorhöfen. Oft weniger schwerwiegend, aber kann Vorhofflimmern anzeigen.",
        'F': "Fusionsschlag: Mischung aus normalem und ektopischem Schlag. Weist auf komplexe Arrhythmien hin.",
        'Q': "Nicht klassifizierbarer Schlag: Unklarer Ursprung, selten.",
        '|': "Ausgefallener Schlag: Zeigt Pausen oder blockierte Impulse.",
        '/': "Schrittmacherschlag: Durch einen Herzschrittmacher ausgelöst."
    }
    for symbol, info in anomaly_summary.items():
        st.write(f"**{symbol} ({info['description']})**: {info['count']} Vorkommen")
        st.write(f"Klinische Bedeutung: {clinical_context.get(symbol, 'Keine spezifische Information verfügbar.')}")
        times_in_range = [t for t in info['times'] if time_range[0] <= t <= time_range[1]]
        if times_in_range:
            times_str = ", ".join([f"{t:.2f}s" for t in times_in_range[:5]])
            if len(times_in_range) > 5:
                times_str += "..."
            st.write(f"Zeiten im ausgewählten Bereich: {times_str}")
        else:
            st.write("Keine Vorkommen im ausgewählten Zeitbereich.")
    
    # Display filtered annotations
    st.header("Anomalien im ausgewählten Zeitbereich")
    if not filtered_annotation_df.empty:
        st.dataframe(
            filtered_annotation_df[['Time (s)', 'Symbol', 'Description']].round({'Time (s)': 2}),
            use_container_width=True
        )
    else:
        st.write("Keine Anomalien im ausgewählten Zeitbereich.")

if __name__ == '__main__':
    main()
"""

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
from src.analyze_anomalien import analyze_ecg_anomalies

# Streamlit-Seitenkonfiguration
st.set_page_config(page_title="Touren & EKG Analyse", layout="centered")
st.title("Touren- und EKG-Analyse")

# Sidebar für Navigation
page = st.sidebar.selectbox("Wähle eine Analyse", ["Touren-Analyse", "Personen- & EKG-Analyse", "EKG-Anomalie-Analyse"])

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

# --- EKG-Anomalie-Analyse ---
elif page == "EKG-Anomalie-Analyse":
    st.header("EKG-Verlauf und Anomalie-Auswertung: MIT-BIH Datensatz 208")
    
    # Load and analyze data
    try:
        signal_df, annotation_df, anomaly_summary = analyze_ecg_anomalies('208', data_dir='mitdb/1.0.0')
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        st.info("Stelle sicher, dass du eine Internetverbindung hast oder die Dateien 208.dat, 208.hea und 208.atr lokal in C:\\Abschlussprojekt_2025 verfügbar sind.")
        signal_df, annotation_df, anomaly_summary = None, None, None
    
    # Nur fortfahren, wenn Daten erfolgreich geladen wurden
    if signal_df is not None and annotation_df is not None and anomaly_summary is not None:
        # Sidebar for time range selection
        st.sidebar.header("Zeitfenster auswählen")
        max_time = signal_df['Time (s)'].max()
        time_range = st.sidebar.slider(
            "Zeitbereich (Sekunden)",
            min_value=0.0,
            max_value=float(max_time),
            value=(0.0, min(30.0, max_time)),  # Default: Erste 30 Sekunden
            step=0.1
        )
        
        # Filter signal and annotations for selected time range
        filtered_signal_df = signal_df[
            (signal_df['Time (s)'] >= time_range[0]) & 
            (signal_df['Time (s)'] <= time_range[1])
        ]
        filtered_annotation_df = annotation_df[
            (annotation_df['Time (s)'] >= time_range[0]) & 
            (annotation_df['Time (s)'] <= time_range[1]) & 
            (annotation_df['Symbol'] != 'N')  # Nur Anomalien
        ]
        
        # Calculate statistics
        total_beats = len(annotation_df)
        anomaly_beats = len(annotation_df[annotation_df['Symbol'] != 'N'])
        anomaly_rate = (anomaly_beats / total_beats * 100) if total_beats > 0 else 0
        duration_minutes = max_time / 60
        anomaly_freq_per_min = anomaly_beats / duration_minutes if duration_minutes > 0 else 0
        
        # Display general statistics
        st.subheader("Allgemeine Statistiken")
        st.write(f"**Gesamtdauer**: {max_time:.2f} Sekunden ({duration_minutes:.2f} Minuten)")
        st.write(f"**Gesamtzahl der Schläge**: {total_beats}")
        st.write(f"**Anzahl der Anomalien**: {anomaly_beats} ({anomaly_rate:.2f}% der Schläge)")
        st.write(f"**Anomalien pro Minute**: {anomaly_freq_per_min:.2f}")
        
        # Plot ECG signals
        st.subheader("EKG-Signale mit Anomalien")
        
        # Plot channel 1 (MLII)
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=filtered_signal_df['Time (s)'],
            y=filtered_signal_df['MLII (mV)'],
            mode='lines',
            name='MLII Signal',
            line=dict(color='blue')
        ))
        if not filtered_annotation_df.empty:
            anomaly_times = filtered_annotation_df['Time (s)']
            anomaly_values = filtered_signal_df.set_index('Time (s)')['MLII (mV)'].reindex(anomaly_times, method='nearest').values
            fig1.add_trace(go.Scatter(
                x=anomaly_times,
                y=anomaly_values,
                mode='markers',
                name='Anomalien',
                marker=dict(symbol='x', size=10, color='red'),
                text=filtered_annotation_df['Description'] + " (" + filtered_annotation_df['Time (s)'].round(2).astype(str) + "s)",
                hoverinfo='text'
            ))
        fig1.update_layout(
            title='EKG-Signal (MLII)',
            xaxis_title='Zeit (s)',
            yaxis_title='Amplitude (mV)',
            hovermode='x',
            showlegend=True
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Plot channel 2 (V1)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=filtered_signal_df['Time (s)'],
            y=filtered_signal_df['V1 (mV)'],
            mode='lines',
            name='V1 Signal',
            line=dict(color='green')
        ))
        if not filtered_annotation_df.empty:
            anomaly_values_v1 = filtered_signal_df.set_index('Time (s)')['V1 (mV)'].reindex(anomaly_times, method='nearest').values
            fig2.add_trace(go.Scatter(
                x=anomaly_times,
                y=anomaly_values_v1,
                mode='markers',
                name='Anomalien',
                marker=dict(symbol='x', size=10, color='red'),
                text=filtered_annotation_df['Description'] + " (" + filtered_annotation_df['Time (s)'].round(2).astype(str) + "s)",
                hoverinfo='text'
            ))
        fig2.update_layout(
            title='EKG-Signal (V1)',
            xaxis_title='Zeit (s)',
            yaxis_title='Amplitude (mV)',
            hovermode='x',
            showlegend=True
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Display anomaly summary with clinical context
        st.subheader("Zusammenfassung der Anomalien")
        clinical_context = {
            'V': "Ventrikuläre Extrasystole (VEB): Vorzeitiger Schlag aus den Ventrikeln. Häufige VEBs können auf Herzkrankheiten hinweisen.",
            'S': "Supraventrikuläre Extrasystole (SVEB): Vorzeitiger Schlag aus den Vorhöfen. Oft weniger schwerwiegend, aber kann Vorhofflimmern anzeigen.",
            'F': "Fusionsschlag: Mischung aus normalem und ektopischem Schlag. Weist auf komplexe Arrhythmien hin.",
            'Q': "Nicht klassifizierbarer Schlag: Unklarer Ursprung, selten.",
            '|': "Ausgefallener Schlag: Zeigt Pausen oder blockierte Impulse.",
            '/': "Schrittmacherschlag: Durch einen Herzschrittmacher ausgelöst."
        }
        for symbol, info in anomaly_summary.items():
            st.write(f"**{symbol} ({info['description']})**: {info['count']} Vorkommen")
            st.write(f"Klinische Bedeutung: {clinical_context.get(symbol, 'Keine spezifische Information verfügbar.')}")
            times_in_range = [t for t in info['times'] if time_range[0] <= t <= time_range[1]]
            if times_in_range:
                times_str = ", ".join([f"{t:.2f}s" for t in times_in_range[:5]])
                if len(times_in_range) > 5:
                    times_str += "..."
                st.write(f"Zeiten im ausgewählten Bereich: {times_str}")
            else:
                st.write("Keine Vorkommen im ausgewählten Zeitbereich.")
        
        # Display filtered annotations
        st.subheader("Anomalien im ausgewählten Zeitbereich")
        if not filtered_annotation_df.empty:
            st.dataframe(
                filtered_annotation_df[['Time (s)', 'Symbol', 'Description']].round({'Time (s)': 2}),
                use_container_width=True
            )
        else:
            st.write("Keine Anomalien im ausgewählten Zeitbereich.")
