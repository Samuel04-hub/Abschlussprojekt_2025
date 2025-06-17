# %% Zelle 1
import pandas as pd

dataframe = pd.read_csv("data/activity.csv")
dataframe

#%%
dataframe["HeartRate"].min()
dataframe["HeartRate"].max()
dataframe["HeartRate"].mean()
de_statistics = dataframe["HeartRate"].describe()   
de_statistics

# %%
dataframe.columns
# %%
dataframe["PowerOriginal"].mean()
dataframe["PowerOriginal"].max()

# %%
dataframe["PowerOriginal"].plot()

# %% Wie lange mehr als 300 Watt?

dataframe["PowerOriginal"] >300

dataframe["High Power"] = dataframe["PowerOriginal"] > 300
dataframe["High Power"].sum()
dataframe["High Power"].value_counts()

# %%
dataframe["Zone"] = None
hr_max = dataframe["HeartRate"].max()
hr_max

# %%

untergrenzen_zonen = {}

zone = 1
for faktor in range(50, 100, 10):
    untergrenzen_zonen[f"Zone {zone}"] = float(hr_max * faktor / 100)
    #print("Zone:") = float(hr_max * faktor)
    #print(hr_max * faktor)
    zone = zone + 1

untergrenzen_zonen
   

# %% Füge eine neue Spalte Zone hinzu, die die Zone basierend auf der Herzfrequenz angibt

list_zone = []

dataframe["Zone"] = None

for index, row in dataframe.iterrows():
    
    current_hr = row["HeartRate"]

    if current_hr >= untergrenzen_zonen["Zone 5"]:
        list_zone.append("Zone 5")

    elif current_hr >= untergrenzen_zonen["Zone 4"]:
        list_zone.append("Zone 4")

    elif current_hr >= untergrenzen_zonen["Zone 3"]:
        list_zone.append("Zone 3")
    
    elif current_hr >= untergrenzen_zonen["Zone 2"]:
        list_zone.append("Zone 2")  
    elif current_hr >= untergrenzen_zonen["Zone 1"]:
        list_zone.append("Zone 1") 

    else:
        list_zone.append("Zone 0") 

dataframe["Zone"] = list_zone

dataframe["Zone"].value_counts()

    
# %%
def_groups = dataframe.groupby("Zone").mean()
def_groups [["HeartRate", "PowerOriginal"]]

# %%

import plotly.express as px
import numpy as np



# ...existing code...

def dataplot(hr_max):
    untergrenzen_zonen = {}
    zone = 1

    for faktor in range(50, 100, 10):
        untergrenzen_zonen[f"Zone {zone}"] = float(hr_max * faktor / 100)
        zone = zone + 1
    
    list_zone = []
    dataframe["Zone"] = None

    for index, row in dataframe.iterrows():
        
        current_hr = row["HeartRate"]

        if current_hr >= untergrenzen_zonen["Zone 5"]:
            list_zone.append("Zone 5")

        elif current_hr >= untergrenzen_zonen["Zone 4"]:
            list_zone.append("Zone 4")

        elif current_hr >= untergrenzen_zonen["Zone 3"]:
            list_zone.append("Zone 3")
        
        elif current_hr >= untergrenzen_zonen["Zone 2"]:
            list_zone.append("Zone 2")  
        elif current_hr >= untergrenzen_zonen["Zone 1"]:
            list_zone.append("Zone 1") 

        else:
            list_zone.append("Zone 0") 

    dataframe["Zone"] = list_zone
    
    time= np.arange(0, len(dataframe) )/ 60
    fig = px.line(dataframe, y=["HeartRate", "PowerOriginal"], 
                  x= time,
                  labels={"x": "Time (min)", "value": "Heart Rate (BPM) und Power (W)"},
                  title="Heart Rate and Power Over Time")

    fig.update_traces(selector=dict(name="HeartRate"), line=dict(color="red"))
    fig.update_traces(selector=dict(name="PowerOriginal"), line=dict(color="blue"))

    # Farben für die Zonen
    zone_colors = {
        "Zone 1": "rgba(0, 51, 204, 0.85)",    # sehr kräftiges Blau
        "Zone 2": "rgba(0, 200, 0, 0.85)",     # sehr kräftiges Grün
        "Zone 3": "rgba(255, 215, 0, 0.85)",   # sehr kräftiges Gelb
        "Zone 4": "rgba(255, 102, 0, 0.85)",   # sehr kräftiges Orange
        "Zone 5": "rgba(204, 0, 0, 0.85)",     # sehr kräftiges Rot
        "Zone 0": "rgba(50, 50, 50, 0.85)",    # sehr dunkles Grau
     
    }

    shapes = []
    zone_names = list(untergrenzen_zonen.keys())
    zone_names.sort(key=lambda z: int(z.split()[-1]))  # Sortieren nach Zone 1, 2, ...

    # Zonenbereiche berechnen
    for i, zone in enumerate(zone_names):
        y0 = untergrenzen_zonen[zone]
        if i < len(zone_names) - 1:
            y1 = untergrenzen_zonen[zone_names[i + 1]]
        else:
            y1 = dataframe["HeartRate"].max()
        shapes.append(
            dict(
                type="rect",
                xref="paper", x0=0, x1=1,
                yref="y", y0=y0, y1=y1,
                fillcolor=zone_colors.get(zone, "rgba(200,200,200,0.1)"),
                opacity=0.3,
                layer="below",
                line_width=0,
            )
        )

    # Zone 0 (unterhalb Zone 1)
    shapes.insert(0, dict(
        type="rect",
        xref="paper", x0=0, x1=1,
        yref="y", y0=0, y1=untergrenzen_zonen["Zone 1"],
        fillcolor=zone_colors["Zone 0"],
        opacity=0.3,
        layer="below",
        line_width=0,
    ))

    fig.update_layout(shapes=shapes)

    fig.show()
    return fig

# ...existing code...

   

   
    fig.show()
    return fig
    

# %%
