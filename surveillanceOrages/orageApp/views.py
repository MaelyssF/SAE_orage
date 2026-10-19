from django.shortcuts import render
from django.http import JsonResponse
from .management.commands.generer_impacts import generer_un_impact, generer_impact_france

def carteView(request):
    return render(request, 'orageApp/carte.html')


def api_generer_impact(request):
    impact = generer_un_impact()
    # impact = generer_impact_france()
    return JsonResponse(impact)