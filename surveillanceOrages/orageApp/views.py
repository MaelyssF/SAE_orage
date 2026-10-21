import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .management.commands.generer_impacts import *
from .management.commands.crea_json_simulation import enregistrer_simulation
import json
from datetime import datetime
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt

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

@require_POST
def api_enregistrer_simulation(request):
    """Reçoit la cellule affichée par le navigateur et l'enregistre dans un fichier JSON"""
    try:
        fichier = enregistrer_simulation(json.loads(request.body))
    except ValueError as erreur:  # JSON illisible ou cellule invalide
        return JsonResponse({"erreur": str(erreur)}, status=400)
    return JsonResponse({"fichier": fichier}, status=201)



# Simulations


@csrf_exempt
def api_sauvegarder_simulation(request):
    """Vue API pour sauvegarder une simulation dans un fichier JSON"""
    if request.method == "POST":
        donnees = json.loads(request.body)
        impacts = donnees.get("impacts", [])

        if not impacts:
            return JsonResponse(
                {"status": "error", "message": "Aucun impact à sauvegarder !"},
                status=400,
            )

        maintenant = datetime.now()
        nom_fichier = maintenant.strftime("simulation_%d-%m-%Y_%H-%M-%S.json")
        date_lisible = maintenant.strftime("%d/%m/%Y à %H:%M:%S")

        contenu = {
            "date_heure": date_lisible,
            "nb_impacts": len(impacts),
            "impacts": impacts,
        }

        # Écriture du fichier JSON
        chemin_fichier = DOSSIER_SIMULATIONS / nom_fichier
        with open(chemin_fichier, "w", encoding="utf-8") as f:
            json.dump(contenu, f, indent=2, ensure_ascii=False)

        return JsonResponse(
            {
                "status": "ok",
                "fichier": nom_fichier,
                "date_heure": date_lisible,
                "nb_impacts": len(impacts),
            }
        )

    return JsonResponse(
        {"status": "error", "message": "Méthode non autorisée"}, status=405
    )


def api_lister_simulations(request):
    """Renvoie la liste des simulations existantes triées de la plus récente à la plus ancienne"""
    simulations = []

    for fichier in sorted(DOSSIER_SIMULATIONS.glob("*.json"), reverse=True):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                data = json.load(f)
                simulations.append(
                    {
                        "fichier": fichier.name,
                        "date_heure": data.get("date_heure", fichier.stem),
                        "nb_impacts": data.get(
                            "nb_impacts", len(data.get("impacts", []))
                        ),
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