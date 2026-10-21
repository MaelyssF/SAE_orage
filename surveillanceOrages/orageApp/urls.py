from django.urls import path
from orageApp.views import home_view, carte_view, simulateur_view, api_generer_cellule, api_enregistrer_simulation

urlpatterns = [
    path('', home_view, name='home'),
    path('home/', home_view, name='home'),
    path('carte/', carte_view, name='carte'),
    path('simulateur/', simulateur_view, name='simulateur'),
    path('generer-cellule/', api_generer_cellule, name='api_generer_cellule'),
    path('enregistrer-simulation/', api_enregistrer_simulation, name='api_enregistrer_simulation'),
]