# Génération d'un scénario synthétique d'orage se déplaçant directement vers la cible (Orléans)
from .constantes import LATITUDE, LONGITUDE, KM_PAR_DEGRE
from django.core.management.base import BaseCommand
from django.utils import timezone
from math import sin, cos, radians
import random


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
        ratio = max(0.0, (start_distance_km - distance_parcourue) / start_distance_km)

        # Coordonnées du centre de la cellule à cette frame
        dx_centre = dx_init * ratio
        dy_centre = dy_init * ratio

        lat_centre = lat_cible + dy_centre / KM_PAR_DEGRE

        lon_centre = lon_cible + dx_centre / (KM_PAR_DEGRE * cos(radians(lat_cible)))

        dist_actuelle_cible = round(start_distance_km - distance_parcourue, 2)

        # Génération des impacts autour du centre de la cellule
        impacts_frame = []
        for _ in range(count):
            dx_imp = random.uniform(-spread_km, spread_km)
            dy_imp = random.uniform(-spread_km, spread_km)

            lat_imp = lat_centre + dy_imp / KM_PAR_DEGRE

            lon_imp = lon_centre + dx_imp / (KM_PAR_DEGRE * cos(radians(lat_centre)))

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
        "lieu_cible": {
            "latitude": lat_cible,
            "longitude": lon_cible
        },
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


def generer_scenario_moving_direct_from_coords(
    latitude: float = LATITUDE,
    longitude: float = LONGITUDE,
    direction_deg: float = None,
    frames: int = 30,
    interval_seconds: int = 120,
    speed_kmh: float = 40.0,
    count: int = 20,
    spread_km: float = 4.0,
    seed: int = None,
) -> dict:
    """
    Génère un scénario synthétique d'orage partant de coordonnées données (ou aléatoires)
    et se déplaçant dans une direction continue (donnée ou aléatoire)

    Args:
        latitude (float): Latitude du point de départ
        longitude (float): Longitude du point de départ
        direction_deg (float, optional): Cap de déplacement en degrés (0° = Nord, 90° = Est). Aléatoire si None
        frames (int): Nombre d'étapes (frames) dans le scénario
        interval_seconds (int): Intervalle de temps entre chaque étape en secondes
        speed_kmh (float): Vitesse de déplacement de l'orage en km/h
        count (int): Nombre d'impacts générés par frame
        spread_km (float): Dispersion des impacts autour du centre en km
        seed (int, optional): Graine aléatoire pour reproductibilité

    Returns:
        dict: Scénario complet prêt à être sérialisé en JSON
    """
    if seed is not None:
        random.seed(seed)

    # Si aucune direction n'est spécifiée, on en tire une aléatoirement entre 0° et 360°
    if direction_deg is None:
        direction_deg = random.uniform(0.0, 360.0)

    # Conversion du cap en radians pour la trigonométrie
    cap_rad = radians(direction_deg)

    # Vecteurs directeurs unitaires (dx = Est, dy = Nord)
    dx_unitaire = sin(cap_rad)
    dy_unitaire = cos(cap_rad)

    # Tableau des 16 directions cardinales pour affichage lisible
    cardinaux = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]

    index_cardinal = int((direction_deg / 22.5) + 0.5) % 16
    direction_cardinale = cardinaux[index_cardinal]

    frames_data = []
    impact_id = 1

    for k in range(frames):
        temps_sec = k * interval_seconds

        # Distance totale parcourue depuis le point de départ en km
        distance_parcourue = speed_kmh * (temps_sec / 3600.0)

        # Déplacement en km par rapport au point initial
        dx_centre_km = distance_parcourue * dx_unitaire
        dy_centre_km = distance_parcourue * dy_unitaire

        # Coordonnées GPS actuelles du centre de la cellule
        lat_centre = latitude + dy_centre_km / KM_PAR_DEGRE
        lon_centre = longitude + dx_centre_km / (
            KM_PAR_DEGRE * cos(radians(lat_centre))
        )

        # Génération des impacts dispersés autour du centre actuel
        impacts_frame = []
        for _ in range(count):
            dx_imp = random.uniform(-spread_km, spread_km)
            dy_imp = random.uniform(-spread_km, spread_km)

            lat_imp = lat_centre + dy_imp / KM_PAR_DEGRE
            lon_imp = lon_centre + dx_imp / (KM_PAR_DEGRE * cos(radians(lat_centre)))

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
                "distance_parcourue_km": round(distance_parcourue, 2),
                "centre_theorique": {
                    "latitude": round(lat_centre, 4),
                    "longitude": round(lon_centre, 4),
                },
                "impacts": impacts_frame,
            }
        )

    return {
        "scenario": "moving_linear",
        "point_depart": {
            "latitude": round(latitude, 4),
            "longitude": round(longitude, 4),
        },
        "trajectoire": {
            "direction_deg": round(direction_deg, 1),
            "direction_cardinale": direction_cardinale,
            "vitesse_kmh": speed_kmh,
        },
        "parametres": {
            "frames": frames,
            "interval_seconds": interval_seconds,
            "speed_kmh": speed_kmh,
            "count_per_frame": count,
            "spread_km": spread_km,
        },
        "frames": frames_data,
    }


if __name__ == "__main__":
    # impacts = generer_impacts()
    # print("Impacts générés :", impacts)
    # scenario = generer_scenario_moving_direct()
    # print("Scénario généré avec", len(scenario["frames"]), "frames.")
    # print("Frame 0 (départ) :", scenario["frames"][0]["centre_theorique"])
    # print("Frame 1 :", scenario["frames"][1]["centre_theorique"])
    # print("Frame 2 :", scenario["frames"][2]["centre_theorique"])
    # print("Frame 4 :", scenario["frames"][4]["centre_theorique"])
    # print("Frame 6 :", scenario["frames"][6]["centre_theorique"])
    # print("Frame 8 :", scenario["frames"][8]["centre_theorique"])
    # print("Frame 10 :", scenario["frames"][10]["centre_theorique"])
    # print("Frame 12 :", scenario["frames"][12]["centre_theorique"])
    # print("Frame 14 :", scenario["frames"][14]["centre_theorique"])
    # print("Frame 16 :", scenario["frames"][16]["centre_theorique"])
    # print("Frame 18 :", scenario["frames"][18]["centre_theorique"])
    # print("Frame 20 :", scenario["frames"][20]["centre_theorique"])
    # print("Frame 22 :", scenario["frames"][22]["centre_theorique"])
    # print("Frame 24 :", scenario["frames"][24]["centre_theorique"])
    # print("Frame 26 (arrivée sur cible) :", scenario["frames"][26]["centre_theorique"])
    scenario = generer_scenario_moving_direct_from_coords(
        latitude=45.7640, longitude=4.8357, speed_kmh=40.0, frames=15
    )
    print("Direction choisie :", scenario["trajectoire"]["direction_cardinale"])
print("Centre à la frame 5 :", scenario["frames"][5]["centre_theorique"])
