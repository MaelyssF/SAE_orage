import random
from math import cos, radians

try:
    from .constantes import LATITUDE, LONGITUDE, KM_PAR_DEGRE
except ImportError:
    from constantes import LATITUDE, LONGITUDE, KM_PAR_DEGRE


def generer_impact_precis(latitude: float, longitude: float) -> dict:
    """Génère un impact exactement aux coordonnées indiquées

    Returns:
        dict: Dictionnaire contenant les coordonnées (latitude et longitude) de l'impact généré
    """
    return {
        "latitude": latitude,
        "longitude": longitude,
    }


def generer_un_impact(
    lat_ref: float = LATITUDE, lon_ref: float = LONGITUDE, rayon_km: float = 550.0
) -> dict:
    """Fonction qui permet de générer un impact dans un rayon donné

    Args:
        lat_ref (float): Latitude de la référence
        lon_ref (float): Longitude de la référence
        rayon_km (float): Rayon en kilomètres, par défaut à 550 km (rayon métropolitain)

    Returns:
        dict: Dictionnaire contenant les coordonnées de l'impact
    """
    dy_km = random.uniform(-rayon_km, rayon_km)
    dx_km = random.uniform(-rayon_km, rayon_km)

    lat = lat_ref + dy_km / KM_PAR_DEGRE
    lon = lon_ref + dx_km / (KM_PAR_DEGRE * cos(radians(lat_ref)))

    return {"latitude": round(lat, 4), "longitude": round(lon, 4)}


def generer_impact_france() -> dict:
    """Fonction qui permet de générer un impact aléatoire en France métropolitaine

    Returns:
        dict: Dictionnaire contenant les coordonnées de l'impact généré
    """
    lat_france = random.uniform(42.0, 51.0)
    lon_france = random.uniform(-5.0, 9.0)
    return {"latitude": round(lat_france, 4), "longitude": round(lon_france, 4)}


def generer_impacts(nb_impacts: int = 10) -> list:
    """Génère une liste d'impacts aléatoires en France.

    Args:
        nb_impacts (int, optional): Nombre d'impacts à générer. Par défaut à 10.

    Returns:
        list: Liste de dictionnaires contenant les coordonnées des impacts
    """
    return [generer_impact_france() for _ in range(nb_impacts)]


if __name__ == "__main__":
    impacts = generer_impacts()
    print("Impacts générés :", impacts)
