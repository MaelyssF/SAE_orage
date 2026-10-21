import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .management.commands.generer_impacts import *
from .management.commands.crea_json_simulation import enregistrer_simulation


def home_view(request):
    return render(request, "orageApp/home.html")


def carte_view(request):
    return render(request, "orageApp/carte.html")


def simulateur_view(request):
    return render(request, "orageApp/simulateur.html")


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