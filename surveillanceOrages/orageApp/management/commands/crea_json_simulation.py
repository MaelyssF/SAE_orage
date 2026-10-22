"""Stockage des simulations : un fichier JSON par simulation, dans orageApp/simulations/.

Le serveur ne garde rien en mémoire entre deux requêtes : c'est le navigateur qui renvoie la
simulation qu'il affiche, et ce module la vérifie avant de l'écrire. On n'écrit jamais ce que le
client envoie tel quel : on reconstruit un dictionnaire propre à partir des seuls champs attendus.
"""

import json
from datetime import datetime

try:
    from .constantes import DOSSIER_SIMULATIONS, NB_IMPACTS_MAX, DUREE_MAX_S
except ImportError:
    from constantes import DOSSIER_SIMULATIONS, NB_IMPACTS_MAX, DUREE_MAX_S


def _nombre(valeur, nom: str, minimum: float, maximum: float) -> float:
    """Vérifie qu'une valeur est un nombre fini compris entre minimum et maximum"""
    # bool est un sous-type de int en Python : on le refuse explicitement
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        raise ValueError(f"« {nom} » doit être un nombre.")
    # écrite ainsi, la comparaison est fausse pour NaN et l'infini : ils sont refusés aussi
    if not minimum <= valeur <= maximum:
        raise ValueError(f"« {nom} » doit être compris entre {minimum} et {maximum}.")
    return float(valeur)


def _coordonnees(point, nom: str) -> dict:
    if not isinstance(point, dict):
        raise ValueError(f"« {nom} » doit contenir une latitude et une longitude.")
    return {
        "latitude": round(_nombre(point.get("latitude"), f"{nom}.latitude", -90, 90), 4),
        "longitude": round(_nombre(point.get("longitude"), f"{nom}.longitude", -180, 180), 4),
    }


def _impact(impact) -> dict:
    """Un impact : sa position et optionnellement son instant et intensité"""
    position = _coordonnees(impact, "impact")
    if "t_s" in impact and impact["t_s"] is not None:
        position["t_s"] = _nombre(impact.get("t_s"), "impact.t_s", 0, DUREE_MAX_S)
    if "intensite_ka" in impact and impact["intensite_ka"] is not None:
        position["intensite_ka"] = _nombre(impact.get("intensite_ka"), "impact.intensite_ka", -1000, 1000)
    if "id" in impact and isinstance(impact["id"], int):
        position["id"] = impact["id"]
    return position


def _debut(valeur) -> str:
    """Date et heure de début de la cellule"""
    if not isinstance(valeur, str):
        raise ValueError("« debut » doit être une date au format ISO 8601.")
    try:
        datetime.fromisoformat(valeur)
    except ValueError:
        raise ValueError("« debut » doit être une date au format ISO 8601.") from None
    return valeur


def valider_cellule(donnees) -> dict:
    """Contrôle une cellule statique reçue du navigateur et renvoie une version propre."""
    if not isinstance(donnees, dict):
        raise ValueError("Le corps de la requête doit être un objet JSON.")

    impacts = donnees.get("impacts")
    if not isinstance(impacts, list) or not 1 <= len(impacts) <= NB_IMPACTS_MAX:
        raise ValueError(f"« impacts » doit être une liste de 1 à {NB_IMPACTS_MAX} impacts.")

    return {
        "type": "cellule_statique",
        "debut": _debut(donnees.get("debut")),
        "centre": _coordonnees(donnees.get("centre"), "centre"),
        "rayon_km": _nombre(donnees.get("rayon_km"), "rayon_km", 0.1, 500),
        "intervalle_s": _nombre(donnees.get("intervalle_s", 1.0), "intervalle_s", 0.001, 3600),
        "impacts": [_impact(impact) for impact in impacts],
    }


def valider_scenario_mobile(donnees) -> dict:
    """Contrôle un scénario mobile avec étapes (frames) et renvoie une version propre."""
    frames_brutes = donnees.get("frames")
    if not isinstance(frames_brutes, list) or len(frames_brutes) == 0:
        raise ValueError("Un scénario mobile doit comporter au moins une étape (frame).")

    frames_validees = []
    tous_impacts = []

    for i, frame in enumerate(frames_brutes):
        frame_impacts = [_impact(imp) for imp in frame.get("impacts", [])]
        tous_impacts.extend(frame_impacts)

        f_val = {
            "frame_index": i,
            "temps_secondes": _nombre(frame.get("temps_secondes", 0), f"frame[{i}].temps_secondes", 0, DUREE_MAX_S),
            "impacts": frame_impacts,
        }
        if "centre_theorique" in frame and frame["centre_theorique"]:
            f_val["centre_theorique"] = _coordonnees(frame["centre_theorique"], f"frame[{i}].centre_theorique")
        if "distance_parcourue_km" in frame:
            f_val["distance_parcourue_km"] = _nombre(frame["distance_parcourue_km"], f"frame[{i}].distance_parcourue_km", 0, 10000)

        frames_validees.append(f_val)

    resultat = {
        "type": "scenario_mobile",
        "scenario": donnees.get("scenario", "moving_linear"),
        "parametres": donnees.get("parametres", {}),
        "frames": frames_validees,
        "impacts": tous_impacts,
    }

    if "point_depart" in donnees and donnees["point_depart"]:
        resultat["point_depart"] = _coordonnees(donnees["point_depart"], "point_depart")
    if "trajectoire" in donnees and isinstance(donnees["trajectoire"], dict):
        resultat["trajectoire"] = donnees["trajectoire"]

    return resultat


def valider_impacts_libres(donnees) -> dict:
    """Contrôle une liste libre d'impacts."""
    impacts = donnees.get("impacts")
    if not isinstance(impacts, list) or not 1 <= len(impacts) <= NB_IMPACTS_MAX:
        raise ValueError(f"« impacts » doit être une liste de 1 à {NB_IMPACTS_MAX} impacts.")

    return {
        "type": "impacts_libres",
        "impacts": [_impact(impact) for impact in impacts],
    }


def valider_simulation(donnees) -> dict:
    """Détecte le type de simulation et applique la validation appropriée."""
    if not isinstance(donnees, dict):
        raise ValueError("Le corps de la requête doit être un objet JSON.")

    sim_type = donnees.get("type")

    if sim_type == "scenario_mobile" or "frames" in donnees:
        return valider_scenario_mobile(donnees)
    elif sim_type == "cellule_statique" or ("centre" in donnees and "rayon_km" in donnees and "debut" in donnees):
        return valider_cellule(donnees)
    elif "impacts" in donnees:
        return valider_impacts_libres(donnees)
    else:
        raise ValueError("Format de simulation inconnu ou liste d'impacts absente.")


def enregistrer_simulation(donnees) -> str:
    """Écrit la simulation dans un nouveau fichier JSON et renvoie le nom de ce fichier.

    Le nom est simulation_AAAAMMJJ_HHMMSS.json ; si ce nom existe déjà (deux enregistrements
    dans la même seconde), un numéro est ajouté (_2, _3...). Un fichier existant n'est jamais écrasé.
    """
    simulation = valider_simulation(donnees)
    maintenant = datetime.now().astimezone()

    DOSSIER_SIMULATIONS.mkdir(exist_ok=True)
    base = "simulation_" + maintenant.strftime("%Y%m%d_%H%M%S")
    nom, numero = base, 1
    while True:
        chemin = DOSSIER_SIMULATIONS / f"{nom}.json"
        try:
            fichier = open(chemin, "x", encoding="utf-8")  # "x" : échoue si le fichier existe déjà
            break
        except FileExistsError:
            numero += 1
            nom = f"{base}_{numero}"

    date_lisible = maintenant.strftime("%d/%m/%Y à %H:%M:%S")

    contenu = {
        "id": nom,
        "type": simulation["type"],
        "cree_le": maintenant.isoformat(timespec="seconds"),
        "date_heure": date_lisible,
        "nb_impacts": len(simulation.get("impacts", [])),
    }

    if simulation["type"] == "cellule_statique":
        contenu["debut"] = simulation["debut"]
        contenu["parametres"] = {
            "centre": simulation["centre"],
            "rayon_km": simulation["rayon_km"],
            "nb_impacts": len(simulation["impacts"]),
            "intervalle_s": simulation["intervalle_s"],
            "duree_s": max((impact.get("t_s", 0) for impact in simulation["impacts"]), default=0),
        }
        contenu["impacts"] = simulation["impacts"]

    elif simulation["type"] == "scenario_mobile":
        if "point_depart" in simulation:
            contenu["point_depart"] = simulation["point_depart"]
        if "trajectoire" in simulation:
            contenu["trajectoire"] = simulation["trajectoire"]
        if "parametres" in simulation:
            contenu["parametres"] = simulation["parametres"]
        contenu["frames"] = simulation["frames"]
        contenu["impacts"] = simulation["impacts"]

    else:  # impacts_libres
        contenu["impacts"] = simulation["impacts"]

    with fichier:
        json.dump(contenu, fichier, ensure_ascii=False, indent=2)
    return chemin.name
