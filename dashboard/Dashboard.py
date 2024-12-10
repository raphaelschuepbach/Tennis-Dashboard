# streamlit run Dashboard.py 

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as patches
import math

# Daten laden
csv_data = pd.read_csv("csv.csv")
    
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

    # Erstellen der Grafik
    fig, ax = plt.subplots(figsize=(12, 12))

# Tennisfeld zeichnen
    court_width = 8.23
    court_length = 23.77
    service_line_dist = 6.4
    net_position = 0

    # Außenlinien
    ax.add_patch(patches.Rectangle((-court_width / 2, -court_length / 2),
                                   court_width, court_length,
                                   fill=False, edgecolor="black", lw=2))
    
    # Netz
    ax.plot([-court_width / 2, court_width / 2], [net_position, net_position], color='black', lw=2)
    
    # Aufschlaglinien
    ax.plot([-court_width / 2, court_width / 2], [net_position + service_line_dist, net_position + service_line_dist], color='black', lw=1)
    ax.plot([-court_width / 2, court_width / 2], [net_position - service_line_dist, net_position - service_line_dist], color='black', lw=1)
    
    # Mittellinie
    ax.plot([0, 0], [net_position - service_line_dist, net_position + service_line_dist], color='black', lw=1)


    # Heatmaps für Spieler 2 (rot) und Spieler 1 (blau)
    cmap1 = sns.color_palette("Reds", as_cmap=True)   # Spieler 2
    cmap2 = sns.color_palette("Blues", as_cmap=True)  # Spieler 1

    for obj_id, cmap in zip(data['Object.ID'].unique(), [cmap1, cmap2]):  # Reihenfolge getauscht
        subset = data[(data['Object.ID'] == obj_id) & (data['Spiel läuft'] == 'Ja')]
        sns.kdeplot(data=subset, x='Transformed.X', y='Transformed.Y', cmap=cmap, fill=True, alpha=0.7, ax=ax, label=f"Spieler {obj_id}")

    ax.set_xlim(-court_width, court_width)
    ax.set_ylim((-court_length / 2) - 3, (court_length / 2) + 3)

    # Titel und Beschriftung
    plt.title('Heatmap der Spielerpositionen')
    plt.legend()
    plt.axis('off')
    return fig


def calculate_intersection_point(A, B, C):
    """
    Berechnet den Schnittpunkt D auf der Seite BC, wo die Winkelhalbierende vom Punkt A auf BC trifft.
    """
    AB = math.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2)
    AC = math.sqrt((C[0] - A[0]) ** 2 + (C[1] - A[1]) ** 2)
    Dx = (B[0] * AC + C[0] * AB) / (AC + AB)
    Dy = (B[1] * AC + C[1] * AB) / (AC + AB)
    return (Dx, Dy)

def visualize_winkelhalbierende_with_players(time, player_positions):
    """
    Visualisiert die Winkelhalbierende, Spielerpositionen und das Tennisfeld.
    """
    # Zeit in Frame umrechnen (bereits vorhandene Frame-Spalte nutzen)
    frame_rate = 30
    frame = int(time * frame_rate)

    # Spielerpositionen für den angegebenen Frame filtern
    player_1 = player_positions[(player_positions["Frame"] == frame) & (player_positions["Object.ID"] == 0)]
    player_2 = player_positions[(player_positions["Frame"] == frame) & (player_positions["Object.ID"] == 1)]

    # Prüfen, ob Daten für beide Spieler vorhanden sind
    if player_1.empty or player_2.empty:
        st.warning(f"Keine Positionen für Spieler in Frame {frame} gefunden.")
        return None

    # Spielerpositionen extrahieren
    A = (player_1["Transformed.X"].iloc[0], player_1["Transformed.Y"].iloc[0])
    player_2_pos = (player_2["Transformed.X"].iloc[0], player_2["Transformed.Y"].iloc[0])

    # Punkte B und C (statisch für das Tennisfeld)
    B, C = (-5.485, 11.89), (5.485, 11.89)

    # Punkt D auf der Winkelhalbierenden berechnen
    D = calculate_intersection_point(A, B, C)

    # Tennisfeld und Winkelhalbierende zeichnen
    fig, ax = plt.subplots(figsize=(12, 12))

    # Tennisfeld-Abmessungen
    singles_width = 8.23  # Breite des Einzelspielfelds in Metern
    doubles_width = 11.0  # Breite des Doppelfelds in Metern
    court_length = 23.77  # Länge des Spielfelds in Metern
    service_line_dist = 6.4  # Abstand der Aufschlaglinie vom Netz
    baseline_dist = court_length / 2  # Abstand der Grundlinie vom Netz

    # Außenlinien (Doppelfeld)
    ax.add_patch(patches.Rectangle((-doubles_width / 2, -baseline_dist),
                                   doubles_width, court_length,
                                   fill=False, edgecolor="black", lw=2))

    # Einzelspielfeld
    ax.add_patch(patches.Rectangle((-singles_width / 2, -baseline_dist),
                                   singles_width, court_length,
                                   fill=False, edgecolor="black", lw=2))

    # Netz
    ax.plot([-doubles_width / 2, doubles_width / 2], [0, 0], color='black', lw=2)

    # Grundlinien
    ax.plot([-singles_width / 2, singles_width / 2], [baseline_dist, baseline_dist], color='black', lw=2)
    ax.plot([-singles_width / 2, singles_width / 2], [-baseline_dist, -baseline_dist], color='black', lw=2)

    # Aufschlaglinien
    ax.plot([-singles_width / 2, singles_width / 2], [service_line_dist, service_line_dist], color='black', lw=1)
    ax.plot([-singles_width / 2, singles_width / 2], [-service_line_dist, -service_line_dist], color='black', lw=1)

    # Mittellinie
    ax.plot([0, 0], [-service_line_dist, service_line_dist], color='black', lw=1)

    # Winkelhalbierende und Spielerpositionen zeichnen
    ax.plot([A[0], B[0]], [A[1], B[1]], 'b--')
    ax.plot([A[0], C[0]], [A[1], C[1]], 'b--')
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-')
    ax.plot([A[0], D[0]], [A[1], D[1]], 'r-', label="Winkelhalbierende")
    ax.scatter(D[0], D[1], color='red', label="Schnittpunkt D", zorder=5)
    ax.scatter(A[0], A[1], color='blue', label="Spieler 1 (Punkt A)", zorder=5)
    ax.scatter(player_2_pos[0], player_2_pos[1], color='orange', label="Spieler 2", zorder=5)

    # Bereiche entlang der Winkelhalbierenden markieren
    green_area = patches.Rectangle((D[0] - 2, 11.89 - 1.5), 4, 1.5, color='green', alpha=0.3)
    yellow_area_left = patches.Rectangle((D[0] - 3, 11.89 - 1.5), 1, 1.5, color='yellow', alpha=0.3)
    yellow_area_right = patches.Rectangle((D[0] + 2, 11.89 - 1.5), 1, 1.5, color='yellow', alpha=0.3)
    red_area_left = patches.Rectangle((D[0] - 5, 11.89 - 1.5), 2, 1.5, color='red', alpha=0.3)
    red_area_right = patches.Rectangle((D[0] + 3, 11.89 - 1.5), 2, 1.5, color='red', alpha=0.3)

    ax.add_patch(green_area)
    ax.add_patch(yellow_area_left)
    ax.add_patch(yellow_area_right)
    ax.add_patch(red_area_left)
    ax.add_patch(red_area_right)

    # Achsenbegrenzungen und Titel
    ax.set_xlim(-singles_width, singles_width)
    ax.set_ylim((-court_length / 2) - 3, (court_length / 2) + 3)
    ax.set_title(f"Winkelhalbierende und Spielerpositionen bei t = {time}s")
    ax.set_xlabel("X-Position (m)")
    ax.set_ylabel("Y-Position (m)")
    ax.legend()
    plt.tight_layout()
    plt.axis('off')
    plt.grid()

    return fig


# Streamlit App
# Seiten-Auswahl
page = st.sidebar.selectbox("Wähle eine Seite:", ["Gesamtübersicht", "Adrian", "Raphael"])

if page == "Gesamtübersicht":
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

    # Heatmap anzeigen
    st.markdown("### Heatmap der Spielerpositionen")
    fig = combined_heatmap(csv_data)
    st.pyplot(fig)

    # Kennzahlen berechnen
    st.markdown("### Kennzahlen für Spieler")
    metrics_table_transposed = calculate_metrics_transposed(csv_data)
    st.table(metrics_table_transposed)
    
elif page == "Adrian":
    st.title("Analyse für Adrian")

    # Zeitslider
    time = st.slider("Zeit (in Sekunden):", min_value=0.0, max_value=315.0, step=0.1, key="adrian_time")
    
    # Geschwindigkeit über Zeit
    player1_data = csv_data[csv_data["Object.ID"] == 0]
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot(player1_data["Frame"], player1_data["Speed"], label="Adrian", linewidth=2, color="red")
    ax1.set_title("Geschwindigkeit über Zeit - Adrian", fontsize=14)
    ax1.set_xlabel("Frame", fontsize=12)
    ax1.set_ylabel("Geschwindigkeit (m/s)", fontsize=12)
    ax1.legend()
    ax1.grid(True)
    st.pyplot(fig1)
    
    # Winkelhalbierende
    fig_winkel = visualize_winkelhalbierende_with_players(time, csv_data)
    if fig_winkel:
        st.pyplot(fig_winkel)

elif page == "Raphael":
    st.title("Analyse für Raphael")

    # Zeitslider
    time = st.slider("Zeit (in Sekunden):", min_value=0.0, max_value=315.0, step=0.1, key="raphael_time")

    # Geschwindigkeit über Zeit
    player2_data = csv_data[csv_data["Object.ID"] == 1]
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.plot(player2_data["Frame"], player2_data["Speed"], label="Raphael", linewidth=2, color="blue")
    ax2.set_title("Geschwindigkeit über Zeit - Raphael", fontsize=14)
    ax2.set_xlabel("Frame", fontsize=12)
    ax2.set_ylabel("Geschwindigkeit (m/s)", fontsize=12)
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)
    
    # Winkelhalbierende
    fig_winkel = visualize_winkelhalbierende_with_players(time, csv_data)
    if fig_winkel:
        st.pyplot(fig_winkel)

