import json
from datetime import datetime
from pathlib import Path

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .management.commands.generer_impacts import *
from .management.commands.generer_scenario import *
from .management.commands.generer_cellule import *
from .management.commands.crea_json_simulation import *

DOSSIER_SIMULATIONS = Path(__file__).resolve().parent / "simulations"
DOSSIER_SIMULATIONS.mkdir(exist_ok=True)

# Pages


def home_view(request):
    """Vue pour la page d'accueil"""
    return render(request, "orageApp/home.html")


def carte_view(request):
    """Vue pour la carte"""
    return render(request, "orageApp/carte.html")


def simulateur_view(request):
    """Vue pour le simulateur"""
    return render(request, "orageApp/simulateur.html")


# API


def api_generer_impact(request):
    impact = generer_impact_france()
    return JsonResponse(impact)


def api_generer_10_impacts(request):
    impacts = generer_impacts()
    return JsonResponse({"impacts": impacts})


def api_generer_cellule(request):
    cellule = generer_cellule_statique()
    return JsonResponse(cellule)


@csrf_exempt
@require_POST
def api_enregistrer_simulation(request):
    """Reçoit la simulation affichée par le navigateur et l'enregistre dans un fichier JSON"""
    try:
        donnees = json.loads(request.body)
        fichier = enregistrer_simulation(donnees)
    except (ValueError, json.JSONDecodeError) as erreur:
        return JsonResponse({"status": "error", "erreur": str(erreur)}, status=400)
    return JsonResponse({"status": "ok", "fichier": fichier}, status=201)


def api_lister_simulations(request):
    """Renvoie la liste des simulations existantes triées de la plus récente à la plus ancienne"""
    simulations = []

    for fichier in sorted(DOSSIER_SIMULATIONS.glob("*.json"), reverse=True):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Récupération flexible de la date et du nombre d'impacts
                date_str = (
                    data.get("date_heure")
                    or data.get("cree_le")
                    or data.get("debut")
                    or fichier.stem
                )
                nb_impacts = data.get("nb_impacts")
                if nb_impacts is None and "parametres" in data:
                    nb_impacts = data["parametres"].get("nb_impacts")
                if nb_impacts is None and "frames" in data:
                    nb_impacts = sum(len(f.get("impacts", [])) for f in data["frames"])
                if nb_impacts is None:
                    nb_impacts = len(data.get("impacts", []))

                simulations.append(
                    {
                        "fichier": fichier.name,
                        "date_heure": str(date_str),
                        "nb_impacts": nb_impacts,
                        "type": data.get("type", "simulation"),
                    }
                )
        except Exception:
            continue

    return JsonResponse({"simulations": simulations})


def api_charger_simulation(request, nom_fichier):
    """Charge et renvoie les données d'une simulation spécifique"""
    chemin = DOSSIER_SIMULATIONS / nom_fichier

    if chemin.exists():
        with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)
            return JsonResponse(data)

    return JsonResponse(
        {"status": "error", "message": "Fichier introuvable !"}, status=404
    )


def api_generer_scenario(request):
    """Vue API pour générer un scénario d'impacts aléatoires en France"""
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if lat and lon:
        scenario = generer_scenario_moving_direct_from_coords(
            latitude=float(lat), longitude=float(lon)
        )
    else:
        scenario = generer_scenario_moving_direct_from_coords()

    return JsonResponse(scenario)
