"""Stockage des simulations : un fichier JSON par simulation, dans orageApp/simulations/.

Le serveur ne garde rien en mémoire entre deux requêtes : c'est le navigateur qui renvoie la
cellule qu'il affiche, et ce module la vérifie avant de l'écrire. On n'écrit jamais ce que le
client envoie tel quel : on reconstruit un dictionnaire propre à partir des seuls champs attendus.
"""

import json
from datetime import datetime
from pathlib import Path

DOSSIER_SIMULATIONS = Path("orageApp/simulations")
NB_IMPACTS_MAX = 1000
DUREE_MAX_S = 24 * 3600  # un impact ne peut pas tomber plus de 24 h après le début de la cellule


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
        "latitude": _nombre(point.get("latitude"), f"{nom}.latitude", -90, 90),
        "longitude": _nombre(point.get("longitude"), f"{nom}.longitude", -180, 180),
    }


def _impact(impact) -> dict:
    """Un impact : sa position et l'instant de sa chute (en secondes depuis le début de la cellule)"""
    position = _coordonnees(impact, "impact")
    position["t_s"] = _nombre(impact.get("t_s"), "impact.t_s", 0, DUREE_MAX_S)
    return position


def _debut(valeur) -> str:
    """Date et heure de début de la cellule, au format ISO 8601 (ex. 2026-10-20T12:22:05+02:00)"""
    if not isinstance(valeur, str):
        raise ValueError("« debut » doit être une date au format ISO 8601.")
    try:
        datetime.fromisoformat(valeur)
    except ValueError:
        raise ValueError("« debut » doit être une date au format ISO 8601.") from None
    return valeur


def valider_cellule(donnees) -> dict:
    """Contrôle une cellule reçue du navigateur et renvoie une version propre.

    Lève ValueError, avec un message lisible, si quelque chose cloche.
    """
    if not isinstance(donnees, dict):
        raise ValueError("Le corps de la requête doit être un objet JSON.")

    impacts = donnees.get("impacts")
    if not isinstance(impacts, list) or not 1 <= len(impacts) <= NB_IMPACTS_MAX:
        raise ValueError(f"« impacts » doit être une liste de 1 à {NB_IMPACTS_MAX} impacts.")

    return {
        "debut": _debut(donnees.get("debut")),
        "centre": _coordonnees(donnees.get("centre"), "centre"),
        "rayon_km": _nombre(donnees.get("rayon_km"), "rayon_km", 0.1, 500),
        "intervalle_s": _nombre(donnees.get("intervalle_s"), "intervalle_s", 0.001, 3600),
        "impacts": [_impact(impact) for impact in impacts],
    }


def enregistrer_simulation(donnees) -> str:
    """Écrit la cellule dans un nouveau fichier JSON et renvoie le nom de ce fichier.

    Le nom est simulation_AAAAMMJJ_HHMMSS.json ; si ce nom existe déjà (deux enregistrements
    dans la même seconde), un numéro est ajouté (_2, _3...). Un fichier existant n'est jamais écrasé.
    """
    cellule = valider_cellule(donnees)
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

    contenu = {
        "id": nom,
        "type": "cellule_statique",
        "debut": cellule["debut"],  # l'horodatage d'un impact = debut + t_s
        "cree_le": maintenant.isoformat(timespec="seconds"),  # moment de l'enregistrement
        "parametres": {
            "centre": cellule["centre"],
            "rayon_km": cellule["rayon_km"],
            "nb_impacts": len(cellule["impacts"]),
            "intervalle_s": cellule["intervalle_s"],
            "duree_s": max(impact["t_s"] for impact in cellule["impacts"]),
        },
        "impacts": cellule["impacts"],
    }
    with fichier:
        json.dump(contenu, fichier, ensure_ascii=False, indent=2)
    return chemin.name