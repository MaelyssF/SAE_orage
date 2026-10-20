import random
from math import sin, cos, radians

from django.core.management.base import BaseCommand
from django.utils import timezone

# from .monApp.models import Impact

# Orléans
LATITUDE = 47.9025
LONGITUDE = 1.9086


NB_IMPACTS = 10
rayon_km = 5
KM_PAR_DEGRE = 111.0

# class Command(BaseCommand):
#     """
#     Crée 10 impacts de foudre autour du lieu surveillé
#     """
#     help = "Crée 10 impacts de foudre autour du lieu surveillé"
#     # MSE = sum((y - t)**2)
#     def handle(self, *args, **options):
#         for i in range(NB_IMPACTS):
#             dy_km = random.uniform(-rayon_km, rayon_km) # NORD - SUD
#             dx_km = random.uniform(-rayon_km, rayon_km) # EST
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


# Génération d'un scénario synthétique d'orage se déplaçant directement vers la cible (Orléans)


def generer_scenario_moving_direct(
    lat_cible: float = LATITUDE,
    lon_cible: float = LONGITUDE,
    frames: int = 30,
    interval_seconds: int = 120,
    speed_kmh: float = 40.0,
    start_distance_km: float = 35.0,
    count: int = 20,
    spread_km: float = 4.0,
    seed: int = 43,
) -> dict:
    """
    Génère un scénario synthétique d'orage se déplaçant directement vers la cible

    Args:
        lat_cible (float): Latitude de la cible (par défaut à Orléans)
        lon_cible (float): Longitude de la cible (par défaut à Orléans)
        frames (int): Nombre de frames dans le scénario (par défaut à 30)
        interval_seconds (int): Intervalle de temps entre chaque frame en secondes (par défaut à 120s)
        speed_kmh (float): Vitesse de déplacement de l'orage en km/h (par défaut à 40.0)
        start_distance_km (float): Distance initiale de l'orage par rapport à la cible en km (par défaut à 35.0km)
        count (int): Nombre d'impacts générés par frame (par défaut à 20)
        spread_km (float): Dispersion des impacts autour du centre de l'orage en km (par défaut à 4.0km)
        seed (int): Graine pour la génération aléatoire (par défaut à 43)

    Returns:
        dict: Dictionnaire contenant les coordonnées (latitude et longitude) de l'impact généré
    """
    if seed:
        random.seed(seed)

    # Position initiale de l'orage à 45° (Nord-Est) par rapport à la cible
    angle_rad = radians(45)
    dx_init = start_distance_km * sin(angle_rad)  # Vers l'Est
    dy_init = start_distance_km * cos(angle_rad)  # Vers le Nord

    frames_data = []
    impact_id = 1

    for k in range(frames):
        temps_sec = k * interval_seconds

        # Distance parcourue depuis le début en km
        distance_parcourue = speed_kmh * (temps_sec / 3600.0)

        # Progression vers la cible
        ratio = max(
            0.0, (start_distance_km - distance_parcourue) / start_distance_km
        )

        # Coordonnées du centre de la cellule à cette frame
        dx_centre = dx_init * ratio
        dy_centre = dy_init * ratio

        lat_centre = lat_cible + dy_centre / KM_PAR_DEGRE
    
        lon_centre = lon_cible + dx_centre / (
            KM_PAR_DEGRE
            * cos(radians(lat_cible))
        )

        dist_actuelle_cible = round(start_distance_km - distance_parcourue, 2)

        # Génération des impacts autour du centre de la cellule
        impacts_frame = []
        for _ in range(count):
            dx_imp = random.uniform(-spread_km, spread_km)
            dy_imp = random.uniform(-spread_km, spread_km)

            lat_imp = lat_centre + dy_imp / KM_PAR_DEGRE
        
            lon_imp = lon_centre + dx_imp / (
                KM_PAR_DEGRE
                * cos(radians(lat_centre))
            )

            impacts_frame.append(
                {
                    "id": impact_id,
                    "latitude": round(lat_imp, 4),
                    "longitude": round(lon_imp, 4),
                    "intensite_ka": round(-abs(random.gauss(25.0, 10.0)), 1),
                }
            )
            impact_id += 1

        # Enregistrement des données de la frame
        frames_data.append(
            {
                "frame_index": k,
                "temps_secondes": temps_sec,
                "centre_theorique": {
                    "latitude": round(lat_centre, 4),
                    "longitude": round(lon_centre, 4),
                    "distance_cible_km": dist_actuelle_cible,
                },
                "impacts": impacts_frame,
            }
        )

    return {
        "scenario": "moving_direct",
        "lieu_cible": {"latitude": lat_cible, "longitude": lon_cible},
        "parametres": {
            "frames": frames,
            "interval_seconds": interval_seconds,
            "speed_kmh": speed_kmh,
            "start_distance_km": start_distance_km,
            "count_per_frame": count,
            "spread_km": spread_km,
        },
        "frames": frames_data,
        }


if __name__ == "__main__":
    # impacts = generer_impacts()
    # print("Impacts générés :", impacts)
    scenario = generer_scenario_moving_direct()
    print("Scénario généré avec", len(scenario["frames"]), "frames.")
    print("Frame 0 (départ) :", scenario["frames"][0]["centre_theorique"])
    print("Frame 1 :", scenario["frames"][1]["centre_theorique"])
    print("Frame 2 :", scenario["frames"][2]["centre_theorique"])
    print("Frame 4 :", scenario["frames"][4]["centre_theorique"])
    print("Frame 6 :", scenario["frames"][6]["centre_theorique"])
    print("Frame 8 :", scenario["frames"][8]["centre_theorique"])
    print("Frame 10 :", scenario["frames"][10]["centre_theorique"])
    print("Frame 12 :", scenario["frames"][12]["centre_theorique"])
    print("Frame 14 :", scenario["frames"][14]["centre_theorique"])
    print("Frame 16 :", scenario["frames"][16]["centre_theorique"])
    print("Frame 18 :", scenario["frames"][18]["centre_theorique"])
    print("Frame 20 :", scenario["frames"][20]["centre_theorique"])
    print("Frame 22 :", scenario["frames"][22]["centre_theorique"])
    print("Frame 24 :", scenario["frames"][24]["centre_theorique"])
    print("Frame 26 (arrivée sur cible) :", scenario["frames"][26]["centre_theorique"])
