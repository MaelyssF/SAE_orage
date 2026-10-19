from django.shortcuts import render
from django.http import JsonResponse
from .management.commands.generer_impacts import generer_un_impact

def carteView(request):
    return render(request, 'orageApp/carte.html')


def api_generer_impact(request):
    impact = generer_un_impact()
    return JsonResponse(impact)