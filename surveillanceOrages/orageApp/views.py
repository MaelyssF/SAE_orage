from django.shortcuts import render
from django.http import JsonResponse
from .management.commands.generer_impacts import *


def home_view(request):
    return render(request, "orageApp/home.html")


def carte_view(request):
    return render(request, "orageApp/carte.html")


def simulateur_view(request):
    return render(request, "orageApp/simulateur.html")


def api_generer_impact(request):
    impact = generer_impact_france()
    return JsonResponse(impact)


def api_generer_10_impacts(request):
    impacts = generer_impacts()
    return JsonResponse({"impacts": impacts})
