# streamlit run Dashboard.py

import streamlit as st
import pandas as pd
import time

# Daten laden
video_csv = pd.read_csv("csv.csv")

# Funktionen definieren
## Punktestand
players = ["Raphael", "Adrian"]
Punktestand = [
    (0, 22.7, {"sets": [0, 0], "points": [0, 0]}),
    (22.8, 40.5, {"sets": [0, 0], "points": [0, 15]}),
    (40.6, 59.3, {"sets": [0, 0], "points": [15, 15]}),
    (59.4, 77.3, {"sets": [0, 0], "points": [30, 15]}),
    (77.4, 97.3, {"sets": [0, 0], "points": [40, 15]}),
    (97.4, 120, {"sets": [1, 0], "points": [0, 0]}),
    (120.1, 133.3, {"sets": [1, 0], "points": [15, 0]}),
    (133.4, 145.3, {"sets": [1, 0], "points": [30, 0]}),
    (145.4, 160.2, {"sets": [1, 0], "points": [40, 0]}),
    (160.3, 178, {"sets": [2, 0], "points": [0, 0]}),
    (178.1, 207, {"sets": [2, 0], "points": [15, 0]}),
    (207.1, 244, {"sets": [2, 0], "points": [30, 0]}),
    (244.1, 267.5, {"sets": [2, 0], "points": [40, 0]}),
    (267.6, 285, {"sets": [2, 0], "points": [40, 15]}),
    (285.1, 313, {"sets": [2, 0], "points": [40, 30]}),
    (313.1, 316, {"sets": [3, 0], "points": [0, 0]}),
]

def get_current_score(current_time):
    for start_time, end_time, score_data in Punktestand:
        if start_time <= current_time < end_time:
            return score_data
    return {"sets": [0, 0], "points": [0, 0]}

# Streamlit App
st.title("Tennis Analyse")

# Video Slider
current_time = st.slider("Videozeit (in Sekunden):", min_value=0.0, max_value=315.0, step=0.1, value=0.0)

# Video anzeigen
st.video("static/match.mp4", start_time=int(current_time))

# Punktestand anzeigen
score_data = get_current_score(current_time)
sets = score_data["sets"]
points = score_data["points"]

st.markdown(
    f"""
    <div style="width: 100%; border: 2px solid #000; border-radius: 5px; background-color: #f0f0f0; padding: 10px; font-family: Arial, sans-serif; font-size: 16px;">
        <div style="display: flex; justify-content: space-between; padding: 5px 0; font-weight: bold; border-bottom: 2px solid #000;">
            <div>Spieler</div>
            <div>Games</div>
            <div>Punkte</div>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 5px 0; background-color: #e6e6e6;">
            <div><strong>{players[0]}</strong></div>
            <div>{sets[0]}</div>
            <div>{points[0]}</div>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 5px 0;">
            <div><strong>{players[1]}</strong></div>
            <div>{sets[1]}</div>
            <div>{points[1]}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Info zum aktuellen Zeitpunkt anzeigen
st.text(f"Aktuelle Videozeit: {current_time} Sekunden")
