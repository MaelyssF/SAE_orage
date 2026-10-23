from django.urls import path
from orageApp.views import *

urlpatterns = [
    # Pages
    path('', home_view, name='home'),
    path('home/', home_view, name='home'),
    path('carte/', carte_view, name='carte'),
    path('simulateur/', simulateur_view, name='simulateur'),

    # API endpoints

    path('api/generer-impact/', api_generer_impact, name='api_generer_impact'),
    path('api/generer-impact-precis/', api_generer_impact_precis, name='api_generer_impact_precis'),
    path('api/generer-10-impacts/', api_generer_10_impacts, name='api_generer_10_impacts'),
    path('api/lister-simulations/', api_lister_simulations, name='api_lister_simulations'),
    path('api/charger-simulation/<str:nom_fichier>/', api_charger_simulation, name='api_charger_simulation'),
    path('api/generer-scenario/', api_generer_scenario, name='api_generer_scenario'),
    path('api/generer-cellule/', api_generer_cellule, name='api_generer_cellule'),
    path('api/enregistrer-simulation/', api_enregistrer_simulation, name='api_enregistrer_simulation'),
]