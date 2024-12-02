# streamlit run Dashboard.py 

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as patches

# Punktestand-Funktion
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

# Funktion zur Erstellung der Kennzahlen-Tabelle (Spieler als Spalten)
def calculate_metrics_transposed(data):
    metrics = {
        "Kennzahl": [
            "Durchschn. Geschwindigkeit (m/s)",
            "Max. Geschwindigkeit (m/s)",
            "Geschwindigkeit bei steh. Gegner (m/s)"
        ]
    }

    for obj_id in data['Object.ID'].unique():
        # Daten des aktuellen Spielers
        player_data = data[data['Object.ID'] == obj_id]
        opponent_data = data[data['Object.ID'] != obj_id]
        
        # Durchschnittliche Geschwindigkeit
        avg_speed = player_data['Speed'].mean()

        # Maximalgeschwindigkeit
        max_speed = player_data['Speed'].max()

        # Durchschnittliche Geschwindigkeit, wenn der Gegner nahezu stillsteht (Speed ~ 0)
        stationary_opponent = opponent_data[opponent_data['Speed'] < 0.5]
        if not stationary_opponent.empty:
            stationary_speed = player_data[player_data['Frame'].isin(stationary_opponent['Frame'])]['Speed'].mean()
        else:
            stationary_speed = None

        # Hinzufügen der Daten für diesen Spieler
        metrics[f"Spieler {obj_id}"] = [
            round(avg_speed, 2),
            round(max_speed, 2),
            round(stationary_speed, 2) if stationary_speed else "N/A"
        ]

    # Erstellen eines DataFrames
    metrics_df = pd.DataFrame(metrics)
    metrics_df.set_index("Kennzahl", inplace=True)
    return metrics_df


# Funktion zur Erstellung der kombinierten Heatmap
def combined_heatmap(data):
    # Tennisfeldabmessungen (angepasst an Y und X-Werte)
    y_min, y_max = -12, 12
    x_min, x_max = -9, 9

    # Erstellen der Grafik
    fig, ax = plt.subplots(figsize=(8, 5))

    # Tennisfeld zeichnen
    ax.add_patch(patches.Rectangle((x_min, y_min),
                                   x_max - x_min, y_max - y_min,
                                   fill=False, edgecolor="black", lw=2))

    # Netz
    plt.plot([x_min, x_max], [0, 0], color='black', lw=2)

    # Heatmaps für Spieler 2 (rot) und Spieler 1 (blau)
    cmap1 = sns.color_palette("Reds", as_cmap=True)   # Spieler 2
    cmap2 = sns.color_palette("Blues", as_cmap=True)  # Spieler 1

    for obj_id, cmap in zip(data['Object.ID'].unique(), [cmap2, cmap1]):  # Reihenfolge getauscht
        subset = data[data['Object.ID'] == obj_id]
        sns.kdeplot(data=subset, x='Transformed.X', y='Transformed.Y', cmap=cmap, fill=True, alpha=0.5, ax=ax, label=f"Spieler {obj_id}")

    # Achsenlimits
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Titel und Beschriftung
    plt.title('Heatmap der Spielerpositionen')
    plt.legend()
    return fig

# Streamlit App
st.title("Tennis Analyse")

# Slider für Videozeit
current_time = st.slider("Videozeit (in Sekunden):", min_value=0.0, max_value=315.0, step=0.1, value=0.0)

# Video aktualisiert sich basierend auf dem Slider
st.video("static/match.mp4", start_time=int(current_time))

# Punktestand berechnen
score_data = get_current_score(current_time)
sets = score_data["sets"]
points = score_data["points"]

# Punktestand HTML
score_html = f"""
<div style="
    position: relative;
    background-color: rgba(0, 0, 0, 0.8);
    color: white;
    border-radius: 10px;
    padding: 10px 15px;
    text-align: center;
    font-family: Arial, sans-serif;
    font-size: 14px; margin-top: 20px;">
    <div style="font-weight: bold; font-size: 16px; margin-bottom: 5px; word-spacing: 200px;">Punktestand Set Punkte</div>
    <div style="display: flex; justify-content: space-between;">
        <div style="flex: 1; text-align: left;">{players[0]}</div>
        <div style="flex: 1; text-align: center;">{sets[0]}</div>
        <div style="flex: 1; text-align: right;">{points[0]}</div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
        <div style="flex: 1; text-align: left;">{players[1]}</div>
        <div style="flex: 1; text-align: center;">{sets[1]}</div>
        <div style="flex: 1; text-align: right;">{points[1]}</div>
    </div>
</div>
"""
st.markdown(score_html, unsafe_allow_html=True)

# Daten laden
csv_data = pd.read_csv("csv.csv")

# Heatmap anzeigen
st.markdown("### Heatmap der Spielerpositionen")
fig = combined_heatmap(csv_data)
st.pyplot(fig)

# Kennzahlen berechnen
st.markdown("### Kennzahlen für Spieler")
metrics_table_transposed = calculate_metrics_transposed(csv_data)
st.table(metrics_table_transposed)
