from pathlib import Path
from PIL import Image
from orageApp.models import Releve, Impact 

# --- 1. CONFIGURATION DE LA CARTE (768x768 pixels) ---
# Emprise en pixels du cadre géographique de la France sur l'image Météociel
MAP_BOUNDS_PX = {
    "x_min": 55,    # Limite gauche de la carte
    "y_min": 45,    # Limite haute de la carte
    "x_max": 715,   # Limite droite de la carte
    "y_max": 715    # Limite basse de la carte
}

# Limites géographiques extrêmes couvertes par cette vue Météociel
GEO_LIMITS = {
    "lat_max": 51.5,  # Latitude Nord maximale
    "lat_min": 41.3,  # Latitude Sud minimale
    "lon_min": -5.0,  # Longitude Ouest minimale
    "lon_max": 9.6    # Longitude Est maximale
}

def pixel_vers_gps_pur(x, y):
    """
    Convertit des coordonnées pixels (x, y) en coordonnées GPS (Latitude, Longitude)
    par interpolation linéaire pure basée sur l'emprise globale de l'image 768x768.
    """
    x_min, y_min = MAP_BOUNDS_PX["x_min"], MAP_BOUNDS_PX["y_min"]
    x_max, y_max = MAP_BOUNDS_PX["x_max"], MAP_BOUNDS_PX["y_max"]
    
    lat_max, lat_min = GEO_LIMITS["lat_max"], GEO_LIMITS["lat_min"]
    lon_min, lon_max = GEO_LIMITS["lon_min"], GEO_LIMITS["lon_max"]

    # Calcul proportionnel (interpolation linéaire)
    latitude = lat_max + (y - y_min) / (y_max - y_min) * (lat_min - lat_max)
    longitude = lon_min + (x - x_min) / (x_max - x_min) * (lon_max - lon_min)

    return round(latitude, 5), round(longitude, 5)

def classifier_impact_2h(rgb):
    """
    Analyse la couleur RGB d'un pixel selon l'échelle des 2 dernières heures (0 à 105 min).
    Retourne l'âge estimé et le poids temporel associé pour l'analyse des orages.
    """
    r, g, b = rgb[:3]
    
    # Plages de couleurs indicatives de la palette Météociel foudre
    if r > 200 and g < 50 and b > 200:      # Magenta / Rose (0-15 min : très récent)
        return 0, 4
    elif r > 200 and g < 50 and b < 50:    # Rouge (15-30 min)
        return 15, 3
    elif r > 200 and g > 100 and b < 50:   # Orange (30-45 min)
        return 30, 2
    elif r > 200 and g > 200 and b < 50:   # Jaune (45-60 min)
        return 45, 1
    
    return None, 0

def traiter_image_meteociel(chemin_image):
    """
    Ouvre l'image 768x768, parcourt les pixels de la carte, 
    détecte les impacts de foudre et calcule leurs coordonnées GPS pures.
    """
    chemin = Path(chemin_image)
    if not chemin.exists():
        print(f"Erreur : L'image {chemin} est introuvable.")
        return []

    # Ouverture de l'image et conversion en RGB
    img = Image.open(chemin).convert("RGB")
    
    # Sécurité : Vérification stricte de la dimension 768x768
    largeur, hauteur = img.size
    if largeur != 768 or hauteur != 768:
        print(f"Avertissement : L'image fait {largeur}x{hauteur}, redimensionnement en 768x768.")
        img = img.resize((768, 768))
    
    pixels = img.load()
    impacts_detectes = []

    x_min = max(0, MAP_BOUNDS_PX["x_min"])
    y_min = max(0, MAP_BOUNDS_PX["y_min"])
    x_max = min(768, MAP_BOUNDS_PX["x_max"])
    y_max = min(768, MAP_BOUNDS_PX["y_max"])

    # Parcours exclusif de la zone de la carte sur l'image
    for y in range(y_min, y_max):
        for x in range(x_min, x_max):
            couleur = pixels[x, y]
            
            # Analyse de la couleur pour déterminer l'âge et le poids
            age_min, poids = classifier_impact_2h(couleur)
            
            if poids > 0:
                # Conversion pure Pixel -> GPS sans points de ville
                lat, lon = pixel_vers_gps_pur(x, y)
                
                impacts_detectes.append({
                    "pixel": (x, y),
                    "latitude": lat,
                    "longitude": lon,
                    "age_minutes": age_min,
                    "poids": poids
                })

    print(f"Traitement réussi : {len(impacts_detectes)} impacts extraits de {chemin.name}.")
    return impacts_detectes

if __name__ == "__main__":
    # Test du script sur une image de ton dossier
    image_test = Path("data/images/impacts_20261023T102756Z.png")
    resultats = traiter_image_meteociel(image_test)
    releve_actuel = Releve.objects.latest('date_heure')

    # Affichage des 5 premiers impacts détectés
    for imp in resultats[:5]:
        print(f"Pixel {imp['pixel']} ➔ GPS : {imp['latitude']}°N, {imp['longitude']}°E (Âge: {imp['age_minutes']} min, Poids: {imp['poids']})")
        Impact.objects.create(
        releve=releve_actuel,
        latitude=imp['latitude'],
        longitude=imp['longitude'],
        poids=imp['poids']  # Si tu stockes le poids temporel dans ton modèle
    )