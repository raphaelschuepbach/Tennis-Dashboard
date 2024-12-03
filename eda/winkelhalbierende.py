import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def calculate_intersection_point(A, B, C):
    """
    Berechnet den Schnittpunkt D auf der Seite BC, wo die Winkelhalbierende vom Punkt A auf BC trifft.
    
    Parameter:
    A, B, C: Tupel, die die Koordinaten der Punkte A, B und C in einem Dreieck darstellen.
    
    Rückgabewert:
    Tupel (Dx, Dy): Koordinaten des Schnittpunkts auf BC.
    """
    # Berechne die Längen der Seiten AB und AC
    AB = math.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2)
    AC = math.sqrt((C[0] - A[0]) ** 2 + (C[1] - A[1]) ** 2)
    
    # Berechne die Koordinaten des Schnittpunkts D
    Dx = (B[0] * AC + C[0] * AB) / (AC + AB)
    Dy = (B[1] * AC + C[1] * AB) / (AC + AB)
    return (Dx, Dy)

def visualize_winkelhalbierende(object_id_1, object_id_2, position_X, position_Y):
    """
    Visualisiert die Winkelhalbierende und markiert Bereiche, in denen ein Spieler optimal stehen sollte.
    
    Parameter:
    object_id_1, object_id_2: Identifikatoren für die Objekte.
    position_X, position_Y: Funktionen oder Daten, die die X- und Y-Koordinaten der Objekte zurückgeben.
    
    Rückgabewert:
    Grafik mit Winkelhalbierende und farbigen Bereichen.
    """
    # Punkt A (Spieler 1)
    A = (position_X(object_id_1), position_Y(object_id_1))
    
    # Bestimme die Position von Spieler 2
    if -1.485 <= position_X(object_id_2) <= 1.485:
        B, C = (-5.485, -11.89), (5.485, -11.89)
    elif position_X(object_id_2) < -1.485:
        B, C = (-5.485, -11.89), (4.115, -6.4)
    elif position_X(object_id_2) > 1.485:
        B, C = (-4.115, -6.4), (5.485, -11.89)
    else:
        raise ValueError("Ungültige Position von Spieler 2")

    # Berechne den Punkt auf der Winkelhalbierenden
    D = calculate_intersection_point(A, B, C)

    # Erstellen der Grafik
    fig, ax = plt.subplots(figsize=(10, 7))

    # Zeichne das Dreieck
    ax.plot([A[0], B[0]], [A[1], B[1]], 'b--', label="Seite AB")
    ax.plot([A[0], C[0]], [A[1], C[1]], 'b--', label="Seite AC")
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-', label="Seite BC")

    # Zeichne die Winkelhalbierende
    ax.plot([A[0], D[0]], [A[1], D[1]], 'r-', label="Winkelhalbierende")

    # Zeichne den Punkt auf der Winkelhalbierenden
    ax.scatter(D[0], D[1], color='red', label="Schnittpunkt D", zorder=5)

    # Färbe die Bereiche
    # Grün: optimaler Bereich
    green_area = patches.Polygon([(B[0], B[1]), (C[0], C[1]), (0, -5)], closed=True, color='green', alpha=0.3)
    ax.add_patch(green_area)

    # Gelb: akzeptabler Bereich
    yellow_area = patches.Polygon([(B[0] - 1, B[1] + 1), (C[0] + 1, C[1] + 1), (0, -3)], closed=True, color='yellow', alpha=0.3)
    ax.add_patch(yellow_area)

    # Rot: nicht optimaler Bereich
    red_area = patches.Polygon([(B[0] - 2, B[1] + 2), (C[0] + 2, C[1] + 2), (0, -1)], closed=True, color='red', alpha=0.3)
    ax.add_patch(red_area)

    # Markiere die Punkte
    ax.scatter(A[0], A[1], color='blue', label="Punkt A (Spieler 1)", zorder=5)
    ax.scatter(B[0], B[1], color='purple', label="Punkt B")
    ax.scatter(C[0], C[1], color='purple', label="Punkt C")

    # Achsenbegrenzung und Titel
    ax.set_xlim(-10, 10)
    ax.set_ylim(-15, 5)
    ax.set_title("Winkelhalbierende mit optimalen Bereichen")
    ax.set_xlabel("X-Position (m)")
    ax.set_ylabel("Y-Position (m)")
    ax.legend()
    plt.grid()
    plt.show()

# Beispiel: Funktionen für Positionen
def position_X(obj_id):
    return -2 if obj_id == 1 else 0

def position_Y(obj_id):
    return 0 if obj_id == 1 else -12

# Visualisierung aufrufen
visualize_winkelhalbierende(1, 2, position_X, position_Y)