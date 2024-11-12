import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as patches
import pandas as pd

def heatmap(data):
    # Tennisfeldabmessungen (in Metern)
    length = 23.77  # Länge des Tennisfelds
    width = 8.23    # Breite des Tennisfelds für Einzel
    double_width = 10.97  # Breite des Tennisfelds für Doppel
    service_line_dist = 6.40  # Abstand der Aufschlaglinie vom Netz
    net_position = 0  # Das Netz ist in der Mitte (Y = 0)

    # Erstellen der Grafik
    fig, ax = plt.subplots(figsize=(10, 5))

    # Tennisfeld (Grundlinien und Seitenlinien für Einzel)
    ax.add_patch(patches.Rectangle((-width / 2, -length / 2),
                                   width, length,
                                   fill=False, edgecolor="black", lw=2))

    # Seitenlinien für Doppel (außerhalb des Einzelfelds)
    ax.add_patch(patches.Rectangle((-double_width / 2, -length / 2),
                                   double_width, length,
                                   fill=False, edgecolor="black", lw=2))

    # Netz
    plt.plot([-double_width / 2, double_width / 2],
             [net_position, net_position], color='black', lw=2)

    # Aufschlaglinien
    plt.plot([-width / 2, width / 2],
             [service_line_dist, service_line_dist], color='black', lw=2)
    plt.plot([-width / 2, width / 2],
             [-service_line_dist, -service_line_dist], color='black', lw=2)

    # Mittellinie
    plt.plot([0, 0], [-service_line_dist, service_line_dist], color='red', lw=2)

    # Erzeugen der Heatmaps für die beiden Objekte
    for obj_id in data['object_id'].unique():
        subset = data[data['object_id'] == obj_id]
        sns.kdeplot(data=subset, x='Position X', y='Position Y', cmap="YlOrRd", shade=True, alpha=0.5, ax=ax)
    
    plt.title('Heatmap der Spielerpositionen für Objekt 1 und 2')
    plt.xlabel('X-Position (m)')
    plt.ylabel('Y-Position (m)')
    plt.show()
