# streamlit run Dashboard.py
 
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as patches
import math
import numpy as np
 
# Daten laden
csv_data = pd.read_csv("csv.csv")
   
# Punktestand-Funktion
players = ["Raphael", "Adrian"]

player_names = {
    0: 'Adrian',
    1: 'Raphael'
}
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

def count_zone_occurrences(data, game, zone, object_id):
    # Filtere Daten für das angegebene Spiel
    game_data = data[(data["Game"] == game) & (data["Spieler schlägt"] == "Ja") & (data["Object.ID"] == object_id)]

    count = 0

    for _, shot in game_data.iterrows():
        frame = shot["Frame"]
        player_data = data[(data["Frame"] == frame) & (data["Object.ID"] == 1 - object_id)]
        
        A = shot["Transformed.X"], shot["Transformed.Y"]

        if -2 <= A[0] <= 2:
            field_width = 10.97
            if object_id == 0:
                B, C, X, Z = (-field_width / 2, 11.89), (field_width / 2, 11.89), 11.89, 1.5
            else:
                B, C, X, Z = (-field_width / 2, -11.89), (field_width / 2, -11.89), -11.89, -1.5

        elif A[0] < -2:
            field_width = 8.23
            if object_id == 0:
                B, C, X, Z = (-field_width / 2, 11.89), (7.5, 11.89), 11.89, 1.5
            else:
                B, C, X, Z = (-field_width / 2, -11.89), (7.5, -11.89), -11.89, -1.5

        else:
            field_width = 8.23
            if object_id == 0:
                B, C, X, Z = (-7.5, 11.89), (field_width / 2, 11.89), 11.89, 1.5
            else:
                B, C, X, Z = (-7.5, -11.89), (field_width / 2, -11.89), -11.89, -1.5

        D = calculate_intersection_point(A, B, C)

        zone_limits = {
            "grün": (D[0] - 0.5, D[0] + 0.5),
            "gelb_links": (D[0] - 0.5, D[0] - 2),
            "gelb_rechts": (D[0] + 0.5, D[0] + 2),
            "rot_links": (D[0] - 2, D[0] - 5.5),
            "rot_rechts": (D[0] + 2, D[0] + 5.5)
        }

        if zone == "grün":
            limits = zone_limits[zone]
        elif zone == "gelb":
            limits = zone_limits["gelb_links"], zone_limits["gelb_rechts"]
        elif zone == "rot":
            limits = zone_limits["rot_links"], zone_limits["rot_rechts"]
        else:
            continue

        if not player_data.empty:
            player_x = player_data["Transformed.X"].iloc[0]

            if zone == "grün":
                if limits[0] <= player_x <= limits[1]:
                    count += 1
            else:
                limits = tuple(sorted(l) for l in limits)
                if (limits[0][0] <= player_x <= limits[0][1] or limits[1][0] <= player_x <= limits[1][1]):
                    count += 1

    return count
 
# Funktion zur Erstellung der Kennzahlen-Tabelle (Spieler als Spalten)
def calculate_metrics_transposed(data):
    metrics = {
        "Kennzahl": [
            "Durchschn. Geschwindigkeit (m/s)",
            "Max. Geschwindigkeit (m/s)",
            "Zurückgelegte Gesamtdistanz (m)",
            "Durchschn. Geschwindigkeit (m/s) bei Schlag",
            "Anzahl Aufenthalte in Zone Grün, bei Schlag des Gegner",
            "Anzahl Aufenthalte in Zone Gelb, bei Schlag des Gegner",
            "Anzahl Aufenthalte in Zone Rot, bei Schlag des Gegner"
            
        ]
    }
    
    # Daten filtern (Zeilen mit 'Spiel läuft nicht' entfernen)
    filtered_data = data[data['Game'].isin(['1', '2', '3'])]

    # Daten sortieren
    filtered_data = filtered_data.sort_values(by=['Object.ID', 'Frame'])
    
    spieler_schlägt = filtered_data[filtered_data['Spieler schlägt'] == 'Ja']

    # Berechnung der Differenzen nur bei aufeinanderfolgenden Frames
    filtered_data['Delta.X'] = filtered_data.groupby(['Object.ID', 'Game'])['Transformed.X'].diff()
    filtered_data['Delta.Y'] = filtered_data.groupby(['Object.ID', 'Game'])['Transformed.Y'].diff()

    # Filtere nur aufeinanderfolgende Frames
    filtered_data = filtered_data[filtered_data['Frame'].diff() == 1]

    # Euklidische Distanz berechnen
    filtered_data['Distanz'] = np.sqrt(filtered_data['Delta.X']**2 + filtered_data['Delta.Y']**2)

    # Gesamtdistanz pro Spieler berechnen
    gesamt_distanz = filtered_data.groupby('Object.ID')['Distanz'].sum().reset_index()
    gesamt_distanz.columns = ['Object.ID', 'Gesamtstrecke (m)']

    
    for obj_id in data['Object.ID'].unique():
        # Daten des aktuellen Spielers
        player_data = data[(data['Object.ID'] == obj_id) & (data['Spiel läuft'] == 'Ja')]

        # Durchschnittliche Geschwindigkeit
        avg_speed = player_data['Speed'].mean()

        avg_speed_schlag = spieler_schlägt[spieler_schlägt['Object.ID'] == obj_id]['Speed'].mean()
        # Maximalgeschwindigkeit
        max_speed = player_data['Speed'].max()
        
        zone_grün_1 = count_zone_occurrences(data, "1", "grün", 1- obj_id)
        zone_grün_2 = count_zone_occurrences(data, "2", "grün", 1- obj_id)
        zone_grün_3 = count_zone_occurrences(data, "3", "grün", 1- obj_id)
        zone_grün = zone_grün_1 + zone_grün_2 + zone_grün_3
        
        zone_gelb_1 = count_zone_occurrences(data, "1", "gelb", 1- obj_id)
        zone_gelb_2 = count_zone_occurrences(data, "2", "gelb", 1- obj_id)
        zone_gelb_3 = count_zone_occurrences(data, "3", "gelb", 1- obj_id)
        zone_gelb = zone_gelb_1 + zone_gelb_2 + zone_gelb_3
        
        zone_rot_1 = count_zone_occurrences(data, "1", "rot", 1- obj_id)
        zone_rot_2 = count_zone_occurrences(data, "2", "rot", 1- obj_id)
        zone_rot_3 = count_zone_occurrences(data, "3", "rot", 1- obj_id)
        zone_rot = zone_rot_1 + zone_rot_2 + zone_rot_3

        # Spielername abrufen
        player_name = player_names.get(obj_id, f"Spieler {obj_id}")  # Name für Spieler anhand der Object.ID
        
        # Spielerbezogene Gesamtdistanz
        player_gesamt_distanz = gesamt_distanz[gesamt_distanz['Object.ID'] == obj_id]['Gesamtstrecke (m)'].values[0]

        # Hinzufügen der Daten zu den Metriken
        metrics[player_name] = [
            f"{round(avg_speed, 2):.2f}",
            f"{round(max_speed, 2):.2f}",
            f"{round(player_gesamt_distanz, 2):.2f}",
            f"{round(avg_speed_schlag, 2):.2f}",
            f"{int(zone_grün)}",
            f"{int(zone_gelb)}",
            f"{int(zone_rot)}"
            ]
    
    # Erstellen eines DataFrames
    metrics_df = pd.DataFrame(metrics)
    metrics_df.set_index("Kennzahl", inplace=True)
    return metrics_df

 
def calculate_metrics_transposed_games(data, games):
    metrics = {
        "Kennzahl": [
            "Durchschn. Geschwindigkeit (m/s) in Game {}".format(games),
            "Max. Geschwindigkeit (m/s) in Game {}".format(games),
            "Zurückgelegte Distanz (m) in Game {} ".format(games),
            "Durchschn. Geschwindigkeit (m/s) bei Schlag in Game {}".format(games),
            "Anzahl Aufenthalte in Zone Grün, bei Schlag des Gegner in Game {} ".format(games),
            "Anzahl Aufenthalte in Zone Gelb, bei Schlag des Gegner in Game {} ".format(games),
            "Anzahl Aufenthalte in Zone Rot, bei Schlag des Gegner in Game {} ".format(games),
            
        ]
    }
    
    # Daten filtern (Zeilen mit 'Spiel läuft nicht' entfernen)
    filtered_data = data[(data['Game']== games)]

    # Daten sortieren
    filtered_data = filtered_data.sort_values(by=['Object.ID', 'Frame'])

    # Berechnung der Differenzen nur bei aufeinanderfolgenden Frames
    filtered_data['Delta.X'] = filtered_data.groupby(['Object.ID', 'Game'])['Transformed.X'].diff()
    filtered_data['Delta.Y'] = filtered_data.groupby(['Object.ID', 'Game'])['Transformed.Y'].diff()

    # Filtere nur aufeinanderfolgende Frames
    filtered_data = filtered_data[filtered_data['Frame'].diff() == 1]

    # Euklidische Distanz berechnen
    filtered_data['Distanz'] = np.sqrt(filtered_data['Delta.X']**2 + filtered_data['Delta.Y']**2)

    #
    spieler_schlägt = filtered_data[filtered_data['Spieler schlägt'] == 'Ja']

    # Distanz pro Spiel und Spieler berechnen
    distanz_pro_game = filtered_data.groupby(['Object.ID', 'Game'])['Distanz'].sum().reset_index()
    distanz_pro_game.columns = ['Object.ID', 'Game', 'Distanz (m)']

    
    
    for obj_id in filtered_data['Object.ID'].unique():
        # Daten des aktuellen Spielers
        player_data = filtered_data[(filtered_data['Object.ID'] == obj_id)]

        # Durchschnittliche Geschwindigkeit
        avg_speed = player_data['Speed'].mean()

        # Maximalgeschwindigkeit
        max_speed = player_data['Speed'].max()
        
        avg_speed_schlag = spieler_schlägt[spieler_schlägt['Object.ID'] == obj_id]['Speed'].mean()
        
        zone_grün = count_zone_occurrences(data, games,"grün", 1- obj_id,)
        zone_gelb = count_zone_occurrences(data, games,"gelb", 1- obj_id)
        zone_rot = count_zone_occurrences(data, games,"rot", 1-obj_id)

        # Spielername abrufen
        player_name = player_names.get(obj_id, f"Spieler {obj_id}")  # Name für Spieler anhand der Object.ID

        # Spielerbezogene Distanz pro Spiel
        player_distanz_pro_game = distanz_pro_game[distanz_pro_game['Object.ID'] == obj_id]
        
        # Distanz pro Spiel
        distanz_game_1 = player_distanz_pro_game[player_distanz_pro_game['Game'] == games]['Distanz (m)'].values
        
        # Sicherstellen, dass die Werte vorhanden sind (falls kein Wert für ein bestimmtes Spiel vorhanden ist)
        distanz_game_1 = distanz_game_1[0] if len(distanz_game_1) > 0 else 0
        

        # Hinzufügen der Daten zu den Metriken
        metrics[player_name] = [
            f"{round(avg_speed, 2):.2f}",
            f"{round(max_speed, 2):.2f}",
            f"{round(distanz_game_1, 2):.2f}",
            f"{round(avg_speed_schlag, 2):.2f}",
            f"{int(zone_grün)}",
            f"{int(zone_gelb)}",
            f"{int(zone_rot)}"
            ]

    
    # Erstellen eines DataFrames
    metrics_df = pd.DataFrame(metrics)
    metrics_df.set_index("Kennzahl", inplace=True)
    return metrics_df

# Funktion zur Erstellung der kombinierten Heatmap
def combined_heatmap(data, current_frame):
    # Erstellen der Grafik
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

    # Heatmaps für Spieler 1 (blau) und Spieler 0 (rot)
    color_maps = {1: sns.color_palette("Blues", as_cmap=True), 0: sns.color_palette("Reds", as_cmap=True)}

    for obj_id in [0, 1]:  # Festgelegte Reihenfolge
        cmap = color_maps[obj_id]

        # Filtere Daten für die Heatmap
        subset = data[(data['Object.ID'] == obj_id) & (data['Spiel läuft'] == 'Ja')]
        sns.kdeplot(data=subset, x='Transformed.X', y='Transformed.Y', cmap=cmap, fill=True, alpha=0.7, ax=ax, label=f"Spieler {obj_id}")

        # Aktuelle Position des Spielers anzeigen
        current_position = data[(data['Object.ID'] == obj_id) & (data['Frame'] == current_frame)]
        if not current_position.empty:
            x = current_position['Transformed.X'].iloc[0]
            y = current_position['Transformed.Y'].iloc[0]
            ax.plot(x, y, 'o', color='black', markersize=12, label=f"Aktuelle Position {obj_id}")

    ax.set_xlim(-width, width)
    ax.set_ylim((-length / 2) - 3, (length / 2) + 3)

    # Titel und Beschriftung
    plt.title('Heatmap der Spielerpositionen')
    plt.axis('off')
    return fig

 
import matplotlib.pyplot as plt

def plot_speed_per_game(data, game, player_ids, frame):
    """
    Erstellt Geschwindigkeit-Diagramme für alle angegebenen Spieler in einem Plot.

    Parameters:
        data: pandas.DataFrame
            Die Daten mit Geschwindigkeit, Frame und Spieler-IDs.
        game: str
            Das Spiel, das ausgewertet werden soll (z.B. "1").
        player_ids: list
            Liste der Object.IDs der Spieler, die geplottet werden sollen.
        frame: int
            Der Frame, bei dem ein Punkt hervorgehoben werden soll.

    Returns:
        fig: matplotlib.figure.Figure
            Das erstellte Diagramm als Matplotlib-Figure.
    """
    # Daten für das angegebene Spiel filtern
    data_game = data[data["Game"] == game]

    # Erstelle die Abbildung
    fig, ax = plt.subplots(figsize=(10, 6))

    # Definiere Farben und Namen für die Spieler
    player_colors = {0: "red", 1: "blue"}  # Rot für Spieler 0, Blau für Spieler 1
    player_names = {0: "Adrian", 1: "Raphael"}  # Namen für die Spieler
    marker_colors = {0: "black", 1: "green"}  # Markerfarben für die Spieler

    for player_id in player_ids:
        # Daten für den aktuellen Spieler filtern
        player_data = data_game[data_game["Object.ID"] == player_id]

        # Index des Frames finden
        indices = player_data.index[player_data["Frame"] == frame].tolist()
        if indices:
            relative_index = player_data.index.get_loc(indices[0])
            highlight_speed = player_data.loc[indices[0], "Speed"]
        else:
            relative_index = None
            highlight_speed = None

        # Plot für den Spieler erstellen
        color = player_colors.get(player_id, "black")  # Standardfarbe
        name = player_names.get(player_id, f"Spieler {player_id}")  # Standardname
        marker_color = marker_colors.get(player_id, "black")  # Markerfarbe

        ax.plot(
            range(len(player_data)), 
            player_data["Speed"], 
            label=name, 
            linewidth=2, 
            color=color
        )
        
        # Hervorgehobenen Punkt plotten, falls Frame gefunden
        if relative_index is not None:
            ax.plot(
                relative_index, 
                highlight_speed, 
                "o", 
                markersize=8, 
                markeredgecolor="black", 
                markerfacecolor=marker_color, 
                label=f"Speed in Frame {frame} ({name})"
            )

    # Achsentitel und Legende
    ax.set_title(f"Geschwindigkeit über Game {game}", fontsize=14)
    ax.set_xlabel("Frame", fontsize=12)
    ax.set_ylabel("Geschwindigkeit (m/s)", fontsize=12)
    ax.legend()
    ax.grid(False)

    # Anpassungen für die gesamte Abbildung
    plt.tight_layout()
    return fig

 
import matplotlib.pyplot as plt

def plot_speed_gesamt(data, player_ids):
    """
    Erstellt ein Geschwindigkeit-Diagramm für mehrere Spieler in einem Plot.

    Parameters:
        data: pandas.DataFrame
            Die Daten mit Geschwindigkeit, Frame und Spieler-IDs.
        player_ids: list
            Liste der Object.IDs der Spieler, die geplottet werden sollen.

    Returns:
        fig: matplotlib.figure.Figure
            Das erstellte Diagramm als Matplotlib-Figure.
    """
    # Erstelle die Abbildung
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Definiere Farben und Namen für die Spieler
    player_colors = {0: "red", 1: "blue"}  # Rot für Spieler 0, Blau für Spieler 1
    player_names = {0: "Adrian", 1: "Raphael"}  # Namen für die Spieler
    
    for player_id in player_ids:
        # Daten für den aktuellen Spieler filtern
        player_data = data[(data["Object.ID"] == player_id) & (data["Spiel läuft"] == "Ja")]
        
        # Bestimme Farbe und Name
        color = player_colors.get(player_id, "black")  # Standardfarbe ist Schwarz
        name = player_names.get(player_id, f"Spieler {player_id}")  # Standardname
        
        # Plotten der Geschwindigkeitskurve
        ax.plot(
            range(len(player_data)), 
            player_data["Speed"], 
            label=name, 
            linewidth=2, 
            color=color
        )
    
    # Achsentitel und Legende
    ax.set_title("Geschwindigkeit über das gesamte Spiel", fontsize=14)
    ax.set_xlabel("Frame", fontsize=12)
    ax.set_ylabel("Geschwindigkeit (m/s)", fontsize=12)
    ax.legend()
    ax.grid(False)
    
    # Anpassungen für die gesamte Abbildung
    plt.tight_layout()
    return fig

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
    
    player_colors = {0: "red", 1: "blue"}  # Rot für Spieler 0, Blau für Spieler 1
    player_names = {0: "Adrian", 1: "Raphael"}  # Namen für die Spieler
    
    
    
    # Prüfen, ob der Schlag-Index gültig ist
    if shot_index < 0 or shot_index >= len(shots):
        st.error(f"Ungültiger Schlag-Index: {shot_index}.")
        return None
 
    # Daten für den aktuellen Schlag
    current_shot = shots.iloc[shot_index]
    frame = current_shot["Frame"]
    object_id = current_shot["Object.ID"]  # Der schlagende Spieler
    opponent_id = 1 - object_id  # Der Gegner (umgekehrt)
    
    # Bestimme Farbe und Name
    color1 = player_colors.get(object_id, "black")  # Standardfarbe ist Schwarz
    color2 = player_colors.get(opponent_id, "black")  # Standardfarbe ist Schwarz
    name1 = player_names.get(object_id, f"Spieler {object_id}")  # Standardname
    name2 = player_names.get(opponent_id, f"Spieler {opponent_id}")  # Standardname
    # Spieler- und Gegnerdaten für den aktuellen Frame
    player = game_data[(game_data["Frame"] == frame) & (game_data["Object.ID"] == object_id)]
    opponent = game_data[(game_data["Frame"] == frame) & (game_data["Object.ID"] == opponent_id)]
 
    if player.empty or opponent.empty:
        st.error("Keine gültigen Positionen für den aktuellen Schlag gefunden.")
        return None
 
    # Positionen des schlagenden Spielers und des Gegners
    A = (player["Transformed.X"].iloc[0], player["Transformed.Y"].iloc[0])  # Spieler
    player_2_pos = (opponent["Transformed.X"].iloc[0], opponent["Transformed.Y"].iloc[0])  # Gegner
     
    if A[0] >= -2 and A[0] <= 2:
    
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
            
    elif A[0] < -2:
        
        if object_id == 0:
            field_width = 8.23  # Anpassen an deine Daten
            B = (-field_width / 2, 11.89)
            C = ( 7.5, 11.89)
            X = 11.89
            Z = 1.5
        else:
            field_width = 8.23
            B = (-field_width / 2, -11.89)
            C = (7.5 , -11.89)
            X = -11.89
            Z = -1.5
        
    elif A[0] > 2:
        
        if object_id == 0:
            field_width = 8.23  # Anpassen an deine Daten
            B = (-7.5, 11.89)
            C = (field_width / 2, 11.89)
            X = 11.89
            Z = 1.5
        else:
            field_width = 8.23
            B = (-7.5 , -11.89)
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
    ax.plot([A[0], B[0]], [A[1], B[1]], 'b--')
    ax.plot([A[0], C[0]], [A[1], C[1]], 'b--')
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-')

    # Zeichne die Winkelhalbierende
    ax.plot([A[0], D[0]], [A[1], D[1]], 'r-', label="Winkelhalbierende")

    # Zeichne den Punkt auf der Winkelhalbierenden
    ax.scatter(D[0], D[1], color='green', label="Optimale Position", zorder=5)

    # Spielerpositionen
    ax.scatter(A[0], A[1], color= color1, label=f"Position von {name1}", zorder=5)
    ax.scatter(player_2_pos[0], player_2_pos[1], color=color2, label=f"Position von {name2}", zorder=5)

    # Färbe die Bereiche entlang der X-Achse (basierend auf D)
    green_area = patches.Rectangle((D[0] - 0.5, X - Z), 1, Z, color='green', alpha=0.3)
    yellow_area_left = patches.Rectangle((D[0] - 0.5, X - Z), -1.5, Z, color='yellow', alpha=0.3)  
    yellow_area_right = patches.Rectangle((D[0] + 0.5, X - Z), 1.5, Z, color='yellow', alpha=0.3)   
    red_area_left = patches.Rectangle((D[0] - 2, X - Z), -3.5, Z, color='red', alpha=0.3)
    red_area_right = patches.Rectangle((D[0] + 2, X - Z), 3.5, Z, color='red', alpha=0.3)
    
    ax.add_patch(green_area)
    ax.add_patch(yellow_area_left)
    ax.add_patch(yellow_area_right)
    ax.add_patch(red_area_left)
    ax.add_patch(red_area_right)

    # Achsenbegrenzung und Titel
    ax.set_xlim(-width, width)
    ax.set_ylim((-length / 2) -3, (length / 2) + 3)
    ax.set_title(f"Winkelhalbierende und Spielerpositionen bei Schlag {shot_index} in Game {game}") 
    ax.set_xlabel("X-Position (m)")
    ax.set_ylabel("Y-Position (m)")
    ax.legend()
    plt.axis('off')
    plt.grid(False)
    return fig
 
 
# Streamlit App
# Seiten-Auswahl
page = st.sidebar.selectbox("Wähle eine Seite:", ["Gesamtübersicht", "Game 1", "Game 2", "Game 3"])
 
if page == "Gesamtübersicht":
    st.title("Tennis Analyse")
 
    # Slider für Videozeit
    current_time = st.slider("Videozeit (in Sekunden):", min_value=0.0, max_value=315.0, step=0.1, value=0.0)
    current_frame = int(current_time * 30)
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
        <div style="font-weight: bold; font-size: 16px; margin-bottom: 5px; word-spacing: 200px;">Punktestand Satz Punkte</div>
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
    fig = combined_heatmap(csv_data, current_frame)
    st.pyplot(fig)
    
    st.markdown("### Geschwindigkeit der Spieler")
    fig_speed_0 = plot_speed_gesamt(csv_data, player_ids=[0, 1])
    st.pyplot(fig_speed_0)
    
 
    # Kennzahlen berechnen
    st.markdown("### Kennzahlen für die Spieler im gesamten Spiel")
    metrics_table_transposed = calculate_metrics_transposed(csv_data)
    st.table(metrics_table_transposed)
   
elif page == "Game 1":
    st.title("Analyse für das Game 1")
    
   
    # Schlag-Regler
    game_shots = csv_data[(csv_data["Game"] == "1") & (csv_data["Spieler schlägt"] == "Ja")]
    shot_count = len(game_shots)
    selected_shot = st.slider("Wähle einen Schlag:", min_value=0, max_value=shot_count -1 , step=1)
    
    #Berechne die Sekunde für den ausgewählten Schlag
    selected_frame = game_shots.iloc[selected_shot ]["Frame"]  # Index beginnt bei 0
    selected_second = selected_frame / 30

    # Visualisierung mit dynamischer Beschriftung
    st.write(f"Ausgewählter Schlag: Schlag bei Sekunde {selected_second:.2f}")
    
   
    
        
    st.video("static/match.mp4", start_time=int(selected_second)) 
    # Punktestand berechnen
    score_data = get_current_score(selected_second)
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
    
    # Winkelhalbierende für den ausgewählten Schlag visualisieren
    st.markdown("### Optimale Postion bei einem Schlag in Game 1")
    fig_wink_1 = visualize_winkelhalbierende_per_shot(csv_data, game="1", shot_index=selected_shot)
    if fig_wink_1:
        st.pyplot(fig_wink_1)
    
    data_game1 = csv_data[csv_data["Game"] == "1"]
    # Heatmap anzeigen
    st.markdown("### Heatmap der Spielerpositionen in Game 1")
    fig = combined_heatmap(data_game1, selected_frame)
    st.pyplot(fig)
    
  # Geschwindigkeit über Zeit für zwei Spieler nebeneinander
    st.markdown("### Geschwindigkeit der Spieler in Game 1")
    fig_speed_1 = plot_speed_per_game(csv_data, game="1", player_ids=[0, 1], frame=selected_frame)
    st.pyplot(fig_speed_1)
   
    
     # Kennzahlen berechnen
    st.markdown("### Kennzahlen für Spieler in Game 1")
    metrics_table_transposed = calculate_metrics_transposed_games(csv_data, "1")
    st.table(metrics_table_transposed)
    
elif page == "Game 2":
    st.title("Analyse für das Game 2")
 
    # Schlag-Regler
    game_shots = csv_data[(csv_data["Game"] == "2") & (csv_data["Spieler schlägt"] == "Ja")]
    shot_count = len(game_shots)
    selected_shot = st.slider("Wähle einen Schlag:", min_value=0, max_value=shot_count -1 , step=1)
    
    #Berechne die Sekunde für den ausgewählten Schlag
    selected_frame = game_shots.iloc[selected_shot ]["Frame"]  # Index beginnt bei 0
    selected_second = selected_frame / 30

    # Visualisierung mit dynamischer Beschriftung
    st.write(f"Ausgewählter Schlag: Schlag bei Sekunde {selected_second:.2f}")
    
   
    
        
    st.video("static/match.mp4", start_time=int(selected_second)) 
    # Punktestand berechnen
    score_data = get_current_score(selected_second)
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
    
    # Winkelhalbierende für den ausgewählten Schlag visualisieren
    st.markdown("### Optimale Postion bei einem Schlag in Game 2")
    fig_wink_1 = visualize_winkelhalbierende_per_shot(csv_data, game="2", shot_index=selected_shot)
    if fig_wink_1:
        st.pyplot(fig_wink_1)
    
    data_game1 = csv_data[csv_data["Game"] == "2"]
    # Heatmap anzeigen
    st.markdown("### Heatmap der Spielerpositionen in Game 2")
    fig = combined_heatmap(data_game1, selected_frame)
    st.pyplot(fig)
    
  # Geschwindigkeit über Zeit für zwei Spieler nebeneinander
    st.markdown("### Geschwindigkeit der Spieler in Game 2")
    fig_speed_2 = plot_speed_per_game(csv_data, game="2", player_ids=[0, 1], frame=selected_frame)
    st.pyplot(fig_speed_2)
    
     # Kennzahlen berechnen
    st.markdown("### Kennzahlen für Spieler in Game 2")
    metrics_table_transposed = calculate_metrics_transposed_games(csv_data, "2")
    st.table(metrics_table_transposed)
 
elif page == "Game 3":
    st.title("Analyse für das Game 3")
    
    # Schlag-Regler
    game_shots = csv_data[(csv_data["Game"] == "3") & (csv_data["Spieler schlägt"] == "Ja")]
    shot_count = len(game_shots)
    selected_shot = st.slider("Wähle einen Schlag:", min_value=0, max_value=shot_count -1  , step=1)
    
    # Berechne die Sekunde für den ausgewählten Schlag
    selected_frame = game_shots.iloc[selected_shot ]["Frame"]  # Index beginnt bei 0
    selected_second = selected_frame / 30
    
     # Visualisierung mit dynamischer Beschriftung
    st.write(f"Ausgewählter Schlag: Schlag bei Sekunde {selected_second:.2f}")
    
    
    st.video("static/match.mp4", start_time=int(selected_second))
    score_data = get_current_score(selected_second)
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
   
    
    # Winkelhalbierende für den ausgewählten Schlag visualisieren
    st.markdown("### Optimale Postion bei einem Schlag in Game 3")
    fig_wink_3 = visualize_winkelhalbierende_per_shot(csv_data, game="3", shot_index=selected_shot)
    if fig_wink_3:
        st.pyplot(fig_wink_3)
        
    
    data_game3 = csv_data[csv_data["Game"] == "3"]
    # Heatmap anzeigen
    st.markdown("### Heatmap der Spielerpositionen in Game 3")
    fig = combined_heatmap(data_game3, selected_frame)
    st.pyplot(fig)
    

    # Geschwindigkeit über Zeit für zwei Spieler nebeneinander
    st.markdown("### Geschwindigkeit der Spieler in Game 3")
    fig_speed_3 = plot_speed_per_game(csv_data, game="3", player_ids=[0, 1], frame=selected_frame)
    st.pyplot(fig_speed_3)
    
    st.markdown("### Kennzahlen für Spieler in Game 3")
    metrics_table_transposed = calculate_metrics_transposed_games(csv_data, "3")
    st.table(metrics_table_transposed)