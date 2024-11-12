import math

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

def winkelhalbierende(object_id_1, object_id_2, speed):
    """
    Bestimmt den Schnittpunkt der Winkelhalbierenden basierend auf der Position von object_id_2.
    
    Parameter:
    object_id_1, object_id_2: Identifikatoren für die Objekte (setzt voraus, dass die Funktionen position_X und position_Y existieren).
    speed: Float, der die Geschwindigkeit des Objekts darstellt.
    
    Rückgabewert:
    Tupel (Dx, Dy): Koordinaten des Schnittpunkts auf BC, oder None, wenn die Bedingungen nicht erfüllt sind.
    """
    if speed < 2:
        A = (position_X(object_id_1), position_Y(object_id_1))
        
        if -1.485 <= position_X(object_id_2) <= 1.485:
            B, C = (-5.485, -11.89), (5.485, -11.89)
            return calculate_intersection_point(A, B, C)
        
        elif position_X(object_id_2) < -1.485:
            B, C = (-5.485, -11.89), (4.115, -6.4)
            return calculate_intersection_point(A, B, C)
        
        elif position_X(object_id_2) > 1.485:
            B, C = (-4.115, -6.4), (5.485, -11.89)
            return calculate_intersection_point(A, B, C)
    
    return None

        
            
            
            