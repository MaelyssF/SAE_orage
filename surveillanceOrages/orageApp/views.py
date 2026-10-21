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
