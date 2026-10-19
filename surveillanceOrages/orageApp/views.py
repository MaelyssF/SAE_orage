from django.shortcuts import render
from django.http import JsonResponse
from .management.commands.generer_impacts import *

def carteView(request):
    return render(request, 'orageApp/carte.html')


def api_generer_impact(request):
    impact = generer_impact_france()
    return JsonResponse(impact)

def api_generer_10_impacts(request):
    impacts = generer_impacts()
    return JsonResponse({"impacts": impacts})