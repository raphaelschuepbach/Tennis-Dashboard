import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math


csv_data = pd.read_csv("csv.csv")

def calculate_intersection_point(A, B, C):
    """
    Berechnet den Schnittpunkt D auf der Seite BC, wo die Winkelhalbierende vom Punkt A auf BC trifft.
    """
    vector_AB = (B[0] - A[0], B[1] - A[1])
    vector_AC = (C[0] - A[0], C[1] - A[1])

    length_AB = math.sqrt(vector_AB[0]**2 + vector_AB[1]**2)
    length_AC = math.sqrt(vector_AC[0]**2 + vector_AC[1]**2)

    vector_AB_normalized = (vector_AB[0] / length_AB, vector_AB[1] / length_AB)
    vector_AC_normalized = (vector_AC[0] / length_AC, vector_AC[1] / length_AC)

    vector_bisector = (vector_AB_normalized[0] + vector_AC_normalized[0], vector_AB_normalized[1] + vector_AC_normalized[1])

    # Schnittpunkt D berechnen
    t = ((C[1] - B[1]) * (B[0] - A[0]) - (C[0] - B[0]) * (B[1] - A[1])) / ((C[1] - B[1]) * vector_bisector[0] - (C[0] - B[0]) * vector_bisector[1])
    Dx = A[0] + t * vector_bisector[0]
    Dy = A[1] + t * vector_bisector[1]
    return (Dx, Dy)

def visualize_winkelhalbierende_per_shot(data, game, shot_index):
    """
    Visualisiert die Winkelhalbierende, Spielerpositionen und das Tennisfeld.
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
    opponent_id = 1 - object_id  # Der Gegner (umgekehrt)
 
    # Spieler- und Gegnerdaten für den aktuellen Frame
    player = game_data[(game_data["Frame"] == frame) & (game_data["Object.ID"] == object_id)]
    opponent = game_data[(game_data["Frame"] == frame) & (game_data["Object.ID"] == opponent_id)]
 
    if player.empty or opponent.empty:
        st.error("Keine gültigen Positionen für den aktuellen Schlag gefunden.")
        return None
 
    # Positionen des schlagenden Spielers und des Gegners
    A = (player["Transformed.X"].iloc[0], player["Transformed.Y"].iloc[0])  # Spieler
    player_2_pos = (opponent["Transformed.X"].iloc[0], opponent["Transformed.Y"].iloc[0])  # Gegner
     
    if object_id == 0:
        field_width = 10.97  # Anpassen an deine Daten
        B = (-field_width / 2, 11.89)
        C = (field_width / 2, 11.89)
        X = 11.89
        Z = 1.5
    else:
        field_width = 10.97
        B = (-field_width / 2, -11.89)
        C = (field_width / 2, -11.89)
        X = -11.89
        Z = -1.5

    # Berechne den Punkt auf der Winkelhalbierenden
    D = calculate_intersection_point(A, B, C)

    

    # Tennisfeld zeichnen
    fig, ax = plt.subplots(figsize=(12, 12))
 
    # Tennisfeldabmessungen (in Metern)
    length = 23.77  
    width = 8.23   
    double_width = 10.97  
    service_line_dist = 6.40  
    net_position = 0 
    
    # Zusätzlicher Platz um das Feld (3 Meter)
    extra_space = 0

    
    # Tennisfeld (Grundlinien und Seitenlinien für Einzel)
    ax.add_patch(patches.Rectangle((-width / 2 - extra_space, -length / 2 - extra_space),
                                width + 2 * extra_space, length + 2 * extra_space,
                                fill=False, edgecolor="black", lw=2))
    
    # Seitenlinien für Doppel (außerhalb des Einzelfelds)
    ax.add_patch(patches.Rectangle((-double_width / 2 - extra_space, -length / 2 - extra_space),
                                double_width + 2 * extra_space, length + 2 * extra_space,
                                fill=False, edgecolor="black", lw=2))

    # Netz
    ax.plot([-double_width / 2 - extra_space, double_width / 2 + extra_space],
         [net_position, net_position], color='black', lw=2)

    # Aufschlaglinien
    ax.plot([-width / 2 - extra_space, width / 2 + extra_space],
         [service_line_dist, service_line_dist], color='black', lw=2)
    ax.plot([-width / 2 - extra_space, width / 2 + extra_space],
         [-service_line_dist, -service_line_dist], color='black', lw=2)

    # Mittellinie
    ax.plot([0, 0], [-service_line_dist, service_line_dist], color='black', lw=2)

    # Zeichne das Dreieck
    ax.plot([A[0], B[0]], [A[1], B[1]], 'b--', label="Seite AB")
    ax.plot([A[0], C[0]], [A[1], C[1]], 'b--', label="Seite AC")
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-', label="Seite BC")

    # Zeichne die Winkelhalbierende
    ax.plot([A[0], D[0]], [A[1], D[1]], 'r-', label="Winkelhalbierende")

    # Zeichne den Punkt auf der Winkelhalbierenden
    ax.scatter(D[0], D[1], color='red', label="Schnittpunkt D", zorder=5)

    # Spielerpositionen
    ax.scatter(A[0], A[1], color='blue', label="Spieler 1 (Punkt A)", zorder=5)
    ax.scatter(player_2_pos[0], player_2_pos[1], color='orange', label="Spieler 2", zorder=5)

    # Färbe die Bereiche entlang der X-Achse (basierend auf D)
    green_area = patches.Rectangle((D[0] - 2, X - Z), 4, Z, color='green', alpha=0.3)
    yellow_area_left = patches.Rectangle((D[0] - 3, X - Z), 1, Z, color='yellow', alpha=0.3)
    yellow_area_right = patches.Rectangle((D[0] + 2, X - Z), 1, Z, color='yellow', alpha=0.3)
    red_area_left = patches.Rectangle((D[0] - 5, X - Z), 2, Z, color='red', alpha=0.3)
    red_area_right = patches.Rectangle((D[0] + 3, X - Z), 2, Z, color='red', alpha=0.3)
    
    ax.add_patch(green_area)
    ax.add_patch(yellow_area_left)
    ax.add_patch(yellow_area_right)
    ax.add_patch(red_area_left)
    ax.add_patch(red_area_right)

    # Achsenbegrenzung und Titel
    ax.set_xlim(-width, width)
    ax.set_ylim((-length / 2) -3, (length / 2) + 3)
    ax.set_title(f"Winkelhalbierende und Spielerpositionen bei t = ")
    ax.set_xlabel("X-Position (m)")
    ax.set_ylabel("Y-Position (m)")
    ax.legend()
    plt.grid()
    return fig

# Streamlit App
st.title("Tennis Analyse mit Spielerpositionen")

page = st.sidebar.selectbox("Wähle eine Seite:", ["Gesamtübersicht", "Game 1", "Game 2", "Game 3"])  
    
if page == "Game 2":
    st.title("Analyse für das Game 2")
    game_shots = csv_data[(csv_data["Game"] == "2") & (csv_data["Spieler schlägt"] == "Ja")]
    shot_count = len(game_shots)
    selected_shot = st.slider("Wähle einen Schlag:", min_value=0, max_value=shot_count - 1, step=1)
    
    # Visualisierung der Spielerpositionen und Winkelhalbierenden
    fig = visualize_winkelhalbierende_per_shot(csv_data, "2", selected_shot)
    if fig:
        st.pyplot(fig)
    
    

 
    # Schlag-Regler
    
   
      
    
