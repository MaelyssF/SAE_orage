# tester_calibration.py

# 1. Définition de tes points de référence (pixels et GPS réels) sur une image 768x768
ARLES_PX = (508, 568)
ARLES_GPS = (43.6768, 4.6276)          # (Latitude, Longitude)

TOULON_PX = (562, 589)
TOULON_GPS = (43.125832, 5.930556)     # (Latitude, Longitude)

def pixel_vers_gps(x, y):
    """
    Convertit des coordonnées pixels (x, y) en GPS 
    en utilisant Arles et Toulon comme repères de calibration linéaire.
    """
    x_arles, y_arles = ARLES_PX
    lat_arles, lon_arles = ARLES_GPS
    
    x_toulon, y_toulon = TOULON_PX
    lat_toulon, lon_toulon = TOULON_GPS

    # Calcul du pas (variation de degré par pixel) entre les deux points
    lat_par_pixel = (lat_toulon - lat_arles) / (y_toulon - y_arles)
    lon_par_pixel = (lon_toulon - lon_arles) / (x_toulon - x_arles)

    # Application de la formule linéaire à partir d'Arles
    latitude = lat_arles + (y - y_arles) * lat_par_pixel
    longitude = lon_arles + (x - x_arles) * lon_par_pixel

    return round(latitude, 5), round(longitude, 5)

if __name__ == "__main__":
    print("--- Lancement des tests de calibration ---\n")
    
    # Test 1 : Vérification sur Arles
    lat_calc, lon_calc = pixel_vers_gps(ARLES_PX[0], ARLES_PX[1])
    print(f"Arles (Pixels {ARLES_PX}) :")
    print(f" -> GPS calculé : {lat_calc}° N, {lon_calc}° E")
    print(f" -> GPS attendu : {ARLES_GPS[0]}° N, {ARLES_GPS[1]}° E\n")

    # Test 2 : Vérification sur Toulon
    lat_calc, lon_calc = pixel_vers_gps(TOULON_PX[0], TOULON_PX[1])
    print(f"Toulon (Pixels {TOULON_PX}) :")
    print(f" -> GPS calculé : {lat_calc}° N, {lon_calc}° E")
    print(f" -> GPS attendu : {TOULON_GPS[0]}° N, {TOULON_GPS[1]}° E\n")

    # Test 3 : Test avec ton point orage (Toulon à 562, 589px ou un autre point)
    x_teste, y_teste = 562, 589
    lat_calculee, lon_calculee = pixel_vers_gps(x_teste, y_teste)
    print(f"Point orage testé (Pixels {x_teste}, {y_teste}) :")
    print(f"GPS calculé : {lat_calculee} N, {lon_calculee} E")