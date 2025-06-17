import gpxpy

def analyze_gpx_file(filepath):
    """
    Analysiert eine GPX-Datei und gibt die Gesamtstrecke (in km), die Anzahl der Trackpunkte
    und eine Liste der Koordinaten zurück.
    """
    with open(filepath, 'r', encoding='utf-8') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        total_distance = 0
        point_count = 0
        coordinates = []

        for track in gpx.tracks:
            for segment in track.segments:
                total_distance += segment.length_2d() / 1000  # Meter zu Kilometer
                point_count += len(segment.points)
                for point in segment.points:
                    coordinates.append([point.longitude, point.latitude])  # Für pydeck: [lon, lat]

        return {
            "total_distance_km": round(total_distance, 2),
            "point_count": point_count,
            "coordinates": coordinates
        }

def analyze_wildschoenau():
    return analyze_gpx_file("fit-files/wildschoenau.gpx")

def analyze_pillersee():
    return analyze_gpx_file("fit-files/pillersee.gpx")

