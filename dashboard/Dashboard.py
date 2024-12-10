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

def plot_speed_per_game(data, game, player_ids, figsize=(10, 8 )):
    """
    Erstellt Geschwindigkeit-Diagramme für alle angegebenen Spieler untereinander.

    Parameters:
        data: pandas.DataFrame
            Die Daten mit Geschwindigkeit, Frame und Spieler-IDs.
        game: str
            Das Spiel, das ausgewertet werden soll (z.B. "1").
        player_ids: list
            Liste der Object.IDs der Spieler, die geplottet werden sollen.
        figsize: tuple
            Größe der gesamten Abbildung (Breite, Höhe).

    Returns:
        fig: matplotlib.figure.Figure
            Das erstellte Diagramm als Matplotlib-Figure.
    """
    # Daten für das angegebene Spiel filtern
    data_game = data[data["Game"] == game]
    
    # Erstelle die Subplots entsprechend der Anzahl der Spieler (vertikal angeordnet)
    num_players = len(player_ids)
    fig, axes = plt.subplots(num_players, 1, figsize=figsize, sharex=True, sharey=True)

    # Falls nur ein Spieler angegeben ist, axes in eine Liste umwandeln
    if num_players == 1:
        axes = [axes]

    # Definiere Farben und Namen für die Spieler
    player_colors = {0: "red", 1: "blue"}  # Rot für Spieler 0, Blau für Spieler 1
    player_names = {0: "Adrian", 1: "Raphael"}  # Namen für die Spieler

    # Iteriere über Spieler-IDs und Achsen
    for ax, player_id in zip(axes, player_ids):
        # Daten für den Spieler filtern
        player_data = data_game[data_game["Object.ID"] == player_id]

        # Plot für den Spieler erstellen
        color = player_colors.get(player_id, "black")  # Standardfarbe ist Schwarz, falls Spieler-ID nicht definiert
        name = player_names.get(player_id, f"Spieler {player_id}")  # Standardname ist "Spieler {ID}"
        ax.plot(range(len(player_data)), player_data["Speed"], label=name, linewidth=2, color=color)
        ax.set_title(f"Geschwindigkeit über Zeit - {name}", fontsize=14)
        ax.set_xlabel("Frame", fontsize=12)
        ax.set_ylabel("Geschwindigkeit (m/s)", fontsize=12)
        ax.legend()
        ax.grid(True)

    # Anpassungen für die gesamte Abbildung
    plt.tight_layout()
    return fig


def visualize_winkelhalbierende_per_shot(data, game, shot_index):
    """
    Visualisiert die Winkelhalbierende für einen bestimmten Schlag innerhalb eines Spiels.

    Parameters:
        data: pandas.DataFrame
            Die gesamte CSV-Daten.
        game: str
            Das Spiel, für das die Winkelhalbierende berechnet werden soll.
        shot_index: int
            Der Index des aktuellen Schlages (beginnend bei 0).

    Returns:
        fig: matplotlib.figure.Figure
            Die erzeugte Visualisierung.
    """
    # Filtere Daten für das ausgewählte Spiel und Schläge
    game_data = data[data["Game"] == game]
    shots = game_data[game_data["Spieler schlägt"] == "Ja"]

    # Prüfen, ob der Schlag-Index gültig ist
    if shot_index < 0 or shot_index >= len(shots):
        st.error(f"Ungültiger Schlag-Index: {shot_index}.")
        return None

    # Daten für den aktuellen Schlag
    current_shot = shots.iloc[shot_index]
    frame = current_shot["Frame"]
    object_id = current_shot["Object.ID"]  # Der schlagende Spieler
    opponent_id = 1 - object_id  # Der Gegner

    # Spieler- und Gegnerdaten für den aktuellen Frame
    player = game_data[(game_data["Frame"] == frame) & (game_data["Object.ID"] == object_id)]
    opponent = game_data[(game_data["Frame"] == frame) & (game_data["Object.ID"] == opponent_id)]

    if player.empty or opponent.empty:
        st.error("Keine gültigen Positionen für den aktuellen Schlag gefunden.")
        return None

    # Positionen
    A = (player["Transformed.X"].iloc[0], player["Transformed.Y"].iloc[0])  # Spieler
    B_opponent = (opponent["Transformed.X"].iloc[0], opponent["Transformed.Y"].iloc[0])  # Gegner

    # Punkte C1 und C2 liegen auf der gegnerischen Spielfeldseite (links/rechts der Linie)
    if object_id == 0:  # Spieler 0 schlägt von unten
        C1 = (-5.485, 11.89)  # Linker Punkt oben
        C2 = (5.485, 11.89)   # Rechter Punkt oben
    else:  # Spieler 1 schlägt von oben
        C1 = (-5.485, -11.89)  # Linker Punkt unten
        C2 = (5.485, -11.89)   # Rechter Punkt unten

    # Berechnung der Winkelhalbierenden
    AB = math.sqrt((B_opponent[0] - A[0]) ** 2 + (B_opponent[1] - A[1]) ** 2)
    AC1 = math.sqrt((C1[0] - A[0]) ** 2 + (C1[1] - A[1]) ** 2)
    AC2 = math.sqrt((C2[0] - A[0]) ** 2 + (C2[1] - A[1]) ** 2)

    # Berechnung der Schnittpunkte
    Dx1 = (B_opponent[0] * AC1 + C1[0] * AB) / (AC1 + AB)
    Dy1 = (B_opponent[1] * AC1 + C1[1] * AB) / (AC1 + AB)

    Dx2 = (B_opponent[0] * AC2 + C2[0] * AB) / (AC2 + AB)
    Dy2 = (B_opponent[1] * AC2 + C2[1] * AB) / (AC2 + AB)

    D1 = (Dx1, Dy1)
    D2 = (Dx2, Dy2)

    # Tennisfeld zeichnen
    court_width = 8.23
    court_length = 23.77
    service_line_dist = 6.4
    net_position = 0

    # Visualisierung
    fig, ax = plt.subplots(figsize=(12, 12))
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

    # Spielerpositionen einzeichnen
    ax.scatter(A[0], A[1], color='blue', label=f"Spieler {object_id} (aktiv)", zorder=5)
    ax.scatter(B_opponent[0], B_opponent[1], color='green', label=f"Gegner (Spieler {opponent_id})", zorder=5)

    # Winkelhalbierende einzeichnen
    ax.plot([A[0], B_opponent[0]], [A[1], B_opponent[1]], 'b--', label="Linie A -> B")
    ax.plot([A[0], C1[0]], [A[1], C1[1]], 'b--', label="Linie A -> C1")
    ax.plot([A[0], C2[0]], [A[1], C2[1]], 'b--', label="Linie A -> C2")
    ax.plot([B_opponent[0], C1[0]], [B_opponent[1], C1[1]], 'k-', label="Linie B -> C1")
    ax.plot([B_opponent[0], C2[0]], [B_opponent[1], C2[1]], 'k-', label="Linie B -> C2")

    ax.plot([A[0], D1[0]], [A[1], D1[1]], 'r-', label="Winkelhalbierende 1")
    ax.scatter(D1[0], D1[1], color='red', label="Schnittpunkt D1", zorder=5)

    ax.plot([A[0], D2[0]], [A[1], D2[1]], 'r-', label="Winkelhalbierende 2")
    ax.scatter(D2[0], D2[1], color='red', label="Schnittpunkt D2", zorder=5)

    # Titel und Einstellungen
    plt.title(f"Winkelhalbierende für Schlag {shot_index + 1} (Spiel {game})")
    plt.axis('off')
    plt.tight_layout()
    plt.ylim(-court_length / 2 - 3, court_length / 2 + 3)
    plt.xlim(-court_width / 2 - 3, court_width / 2 + 3)
    plt.legend()
    return fig


# Streamlit App
# Seiten-Auswahl
page = st.sidebar.selectbox("Wähle eine Seite:", ["Gesamtübersicht", "Game 1", "Game 2", "Game 3"])

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
    
elif page == "Game 1":
    st.title("Analyse für das Game 1")
    
    # Geschwindigkeit über Zeit für zwei Spieler nebeneinander
    fig_speed_1 = plot_speed_per_game(csv_data, game="1", player_ids=[0, 1])
    st.pyplot(fig_speed_1)
    
    # Schlag-Regler
    game_shots = csv_data[(csv_data["Game"] == "1") & (csv_data["Spieler schlägt"] == "Ja")]
    shot_count = len(game_shots)
    selected_shot = st.slider("Wähle einen Schlag:", min_value=0, max_value=shot_count - 1, step=1)
    
    # Winkelhalbierende für den ausgewählten Schlag visualisieren
    fig_wink_1 = visualize_winkelhalbierende_per_shot(csv_data, game="1", shot_index=selected_shot)
    if fig_wink_1:
        st.pyplot(fig_wink_1)
        

elif page == "Game 2":
    st.title("Analyse für das Game 2")

    # Geschwindigkeit über Zeit für zwei Spieler nebeneinander
    fig_speed_2 = plot_speed_per_game(csv_data, game="2", player_ids=[0, 1])
    st.pyplot(fig_speed_2)
    
    # Schlag-Regler
    game_shots = csv_data[(csv_data["Game"] == "2") & (csv_data["Spieler schlägt"] == "Ja")]
    shot_count = len(game_shots)
    selected_shot = st.slider("Wähle einen Schlag:", min_value=0, max_value=shot_count - 1, step=1)
    
    # Winkelhalbierende für den ausgewählten Schlag visualisieren
    fig_wink_2 = visualize_winkelhalbierende_per_shot(csv_data, game="2", shot_index=selected_shot)
    if fig_wink_2:
        st.pyplot(fig_wink_2)


elif page == "Game 3":
    st.title("Analyse für das Game 3")

    # Geschwindigkeit über Zeit für zwei Spieler nebeneinander
    fig_speed_3 = plot_speed_per_game(csv_data, game="3", player_ids=[0, 1])
    st.pyplot(fig_speed_3)
    
    # Schlag-Regler
    game_shots = csv_data[(csv_data["Game"] == "3") & (csv_data["Spieler schlägt"] == "Ja")]
    shot_count = len(game_shots)
    selected_shot = st.slider("Wähle einen Schlag:", min_value=0, max_value=shot_count - 1, step=1)
    
    # Winkelhalbierende für den ausgewählten Schlag visualisieren
    fig_wink_3 = visualize_winkelhalbierende_per_shot(csv_data, game="3", shot_index=selected_shot)
    if fig_wink_3:
        st.pyplot(fig_wink_3)