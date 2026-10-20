from .constantes import LATITUDE, LONGITUDE, KM_PAR_DEGRE
import random
from math import cos, radians
# from .monApp.models import Impact


# class Command(BaseCommand):
#     """
#     Crée 10 impacts de foudre autour du lieu surveillé
#     """
#     help = "Crée 10 impacts de foudre autour du lieu surveillé"
#     # MSE = sum((y - t)**2)
#     def handle(self, *args, **options):
#         for i in range(NB_IMPACTS):
#             dy_km = random.uniform(-RAYON_KM, RAYON_KM) # NORD - SUD
#             dx_km = random.uniform(-RAYON_KM, RAYON_KM) # EST
#             lat = LATITUDE + dy_km / KM_PAR_DEGRE
#             lon = LONGITUDE + dx_km / (KM_PAR_DEGRE * cos(radians(LATITUDE)))

#             Impact.objects.create(
#                 latitude=lat,
#                 releve_id=None,
#                 longitude=lon,
#                 cellule_id=None,
#                 latitude=lat,
#                 longitude=lon,
#                 distance_km=(dx_km**2 + dy_km**2)**0.5,
#                 direction_cardinale=random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
#                 direction_deg=random.uniform(0, 360), # Random pour l'instant
#                 intensite_ka=random.uniform(0, 100), # Random pour l'instant
#                 categorie=random.choice(['CG-', 'CG+', 'IC']), # Random pour l'instant
#                 horodatage=timezone.now(),
#             )

#         self.stdout.write(self.style.SUCCESS(
#             f"{NB_IMPACTS} impacts factices"
#         ))


# Génération d'impacts de foudre aléatoires autour d'un point de référence


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
    """Fonction qui permet de générer un impact

    Args:
        lat_ref (float): Latitude de la référence
        lon_ref (float): Longitude de la référence
        rayon_km (float): Rayon en kilomètres, par défaut à 550 km (rayon de la France métropolitaine à partir d'Orléans)

    Returns:
        dict: Dictionnaire contenant les coordonnées (latitude et longitude) de l'impact généré
    """
    dy_km = random.uniform(-rayon_km, rayon_km)
    dx_km = random.uniform(-rayon_km, rayon_km)

    lat = lat_ref + dy_km / KM_PAR_DEGRE
    lon = lon_ref + dx_km / (KM_PAR_DEGRE * cos(radians(lat_ref)))

    return {"latitude": round(lat, 4), "longitude": round(lon, 4)}


def generer_impact_france() -> dict:
    """Fonction qui permet de générer un impact aléatoire en France

    Returns:
        dict: Dictionnaire contenant les coordonnées (latitude et longitude) de l'impact généré
    """
    lat_france = random.uniform(42.0, 51.0)
    lon_france = random.uniform(-5.0, 9.0)
    return {"latitude": round(lat_france, 4), "longitude": round(lon_france, 4)}


def generer_impacts(nb_impacts: int = 10) -> list:
    """Fonction qui permet de générer un impact

    Args:
        nb_impacts (int, optional): Nombre d'impacts à générer. Par défaut à 10.

    Returns:
            dict: Dictionnaire contenant les coordonnées (latitude et longitude) de l'impact généré
    """
    return [generer_impact_france() for _ in range(nb_impacts)]


if __name__ == "__main__":
    impacts = generer_impacts()
    print("Impacts générés :", impacts)
