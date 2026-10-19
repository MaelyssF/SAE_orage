from django.urls import path
from orageApp.views import home_view, carte_view, simulateur_view, api_generer_impact, api_generer_10_impacts

urlpatterns = [
    path('', home_view, name='home'),
    path('home/', home_view, name='home'),
    path('carte/', carte_view, name='carte'),
    path('simulateur/', simulateur_view, name='simulateur'),
    path('api/generer-impact/', api_generer_impact, name='api_generer_impact'),
    path('api/generer-10-impacts/', api_generer_10_impacts, name='api_generer_10_impacts'),
]
