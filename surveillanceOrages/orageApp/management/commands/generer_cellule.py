# Génération d'une cellule orageuse statique (un groupement d'impacts)

import random
from math import cos, radians
from datetime import datetime

try:
    from .constantes import *
    from .generer_impacts import generer_un_impact
except ImportError:
    from constantes import *
    from generer_impacts import generer_un_impact


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance approximative en km entre deux points proches (même formule que generer_un_impact, à l'envers)"""
    dy_km = (lat2 - lat1) * KM_PAR_DEGRE
    dx_km = (lon2 - lon1) * KM_PAR_DEGRE * cos(radians(lat1))
    return (dx_km**2 + dy_km**2) ** 0.5


def generer_cellule_statique(
    nb_impacts: int = 20,
    lat_centre: float = CELLULE_LATITUDE,
    lon_centre: float = CELLULE_LONGITUDE,
    rayon_km: float = 30.0,
    intervalle_s: float = INTERVALLE_IMPACTS_S,
) -> dict:
    """Génère une cellule orageuse immobile : nb_impacts impacts regroupés autour d'un centre

    Réutilise generer_un_impact (qui tire dans un carré de côté 2 x rayon_km) et ne garde que
    les impacts situés à moins de rayon_km du centre : la cellule est donc un disque, et non un carré.

    Les impacts ne tombent pas tous en même temps : le k-ième impact (k = 0, 1, 2...) tombe
    k x intervalle_s secondes après le début de la cellule (champ "t_s" de chaque impact).

    Args:
        nb_impacts (int): Nombre d'impacts de la cellule (par défaut à 20)
        lat_centre (float): Latitude du centre de la cellule (par défaut en Lorraine)
        lon_centre (float): Longitude du centre de la cellule (par défaut en Lorraine)
        rayon_km (float): Rayon de la cellule en kilomètres (par défaut à 30.0km)
        intervalle_s (float): Temps entre deux impacts successifs en secondes (par défaut à 1.0s)

    Returns:
        dict: Le début de la cellule, son centre, son rayon, l'intervalle entre impacts et la liste
        des impacts (chacun avec sa latitude, sa longitude et son instant de chute t_s en secondes)
    """
    impacts = []
    while len(impacts) < nb_impacts:
        impact = generer_un_impact(lat_centre, lon_centre, rayon_km)
        if distance_km(lat_centre, lon_centre, impact["latitude"], impact["longitude"]) <= rayon_km:
            impact["t_s"] = round(len(impacts) * intervalle_s, 3)
            impacts.append(impact)

    return {
        "debut": datetime.now().astimezone().isoformat(timespec="seconds"),
        "centre": {"latitude": lat_centre, "longitude": lon_centre},
        "rayon_km": rayon_km,
        "nb_impacts": nb_impacts,
        "intervalle_s": intervalle_s,
        "impacts": impacts,
    }
