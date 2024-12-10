import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

# Daten laden
player_positions = pd.read_csv("csv.csv")
frame_rate = 30  # Frames pro Sekunde

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
    # Zeit in Frame umrechnen
    frame = int(time * frame_rate)

    # Filter die Spielerpositionen für den gegebenen Frame
    player_1 = player_positions[(player_positions["frame"] == frame) & (player_positions["Object.ID"] == 0)]
    player_2 = player_positions[(player_positions["frame"] == frame) & (player_positions["Object.ID"] == 1)]

    if player_1.empty or player_2.empty:
        st.warning(f"Keine Positionen für Spieler in Frame {frame} gefunden.")
        return None

    A = (player_1["Transformed.X"].iloc[0], player_1["Transformed.Y"].iloc[0])
    player_2_pos = (player_2["Transformed.X"].iloc[0], player_2["Transformed.Y"].iloc[0])

    # Punkte B und C (statisch für das Tennisfeld)
    B, C = (-5.485, 11.89), (5.485, 11.89)

    # Berechne den Punkt auf der Winkelhalbierenden
    D = calculate_intersection_point(A, B, C)

    # Erstellen der Grafik
    fig, ax = plt.subplots(figsize=(12, 8))

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

    # Achsenbegrenzung und Titel
    ax.set_xlim(-court_width, court_width)
    ax.set_ylim(-court_length / 2, court_length / 2)
    ax.set_title(f"Winkelhalbierende und Spielerpositionen bei t = {time}s")
    ax.set_xlabel("X-Position (m)")
    ax.set_ylabel("Y-Position (m)")
    ax.legend()
    plt.grid()
    return fig

# Streamlit App
st.title("Tennis Analyse mit Spielerpositionen")

# Slider für Zeit
time = st.slider("Zeit (in Sekunden):", min_value=0, max_value=10, step=1)

# Visualisierung der Spielerpositionen und Winkelhalbierenden
fig = visualize_winkelhalbierende_with_players(time, player_positions)
if fig:
    st.pyplot(fig)
    
    
    
    
    
# Funktion zur Visualisierung der Winkelhalbierenden
def visualize_winkelhalbierende(data, frame, object_id, opponent_id):
    """
    Visualisiert die Winkelhalbierende für den angegebenen Spieler (object_id)
    und zeigt die Position des Gegners (opponent_id).
    """
    # Spieler-Daten für den aktuellen Frame
    player = data[(data["Frame"] == frame) & (data["Object.ID"] == object_id)]
    opponent = data[(data["Frame"] == frame) & (data["Object.ID"] == opponent_id)]

    # Debugging: Sicherstellen, dass Daten korrekt geladen werden
    if player.empty:
        st.error(f"Keine Daten für Spieler {object_id} in Frame {frame}")
        return None
    if opponent.empty:
        st.error(f"Keine Daten für Gegner {opponent_id} in Frame {frame}")
        return None

    # Positionen der Spieler
    A = (player["Transformed.X"].iloc[0], player["Transformed.Y"].iloc[0])  # Spieler
    B_opponent = (opponent["Transformed.X"].iloc[0], opponent["Transformed.Y"].iloc[0])  # Gegner

    # Dynamische Punkte B und C für den aktiven Spieler
    if -1.485 <= A[0] <= 1.485:
        B, C = (-5.485, -11.89), (5.485, -11.89)
    elif A[0] < -1.485:
        B, C = (-5.485, -11.89), (4.115, -6.4)
    elif A[0] > 1.485:
        B, C = (-4.115, -6.4), (5.485, -11.89)

    # Schnittpunkt D berechnen
    AB = math.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2)
    AC = math.sqrt((C[0] - A[0]) ** 2 + (C[1] - A[1]) ** 2)
    Dx = (B[0] * AC + C[0] * AB) / (AC + AB)
    Dy = (B[1] * AC + C[1] * AB) / (AC + AB)
    D = (Dx, Dy)

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
    ax.plot([A[0], B[0]], [A[1], B[1]], 'b--', label="Linie A -> B")
    ax.plot([A[0], C[0]], [A[1], C[1]], 'b--', label="Linie A -> C")
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-', label="Linie B -> C")
    ax.plot([A[0], D[0]], [A[1], D[1]], 'r-', label="Winkelhalbierende")
    ax.scatter(D[0], D[1], color='red', label="Schnittpunkt D", zorder=5)

    # Titel und Einstellungen
    plt.title(f"Winkelhalbierende und Spielerpositionen bei Frame {frame} (Spieler {object_id})")
    plt.axis('off')
    plt.tight_layout()
    plt.ylim(-court_length / 2 - 3, court_length / 2 + 3)
    plt.xlim(-court_width / 2 - 3, court_width / 2 + 3)
    plt.legend()
    return fig
