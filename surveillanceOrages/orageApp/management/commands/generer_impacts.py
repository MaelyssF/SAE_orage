import random
from math import cos, radians

from django.core.management.base import BaseCommand
from django.utils import timezone

# from .monApp.models import Impact

# Orléans
LATITUDE = 47.9025
LONGITUDE = 1.9086


NB_IMPACTS = 10
rayon_km = 5
km_par_degre = 111.0

# class Command(BaseCommand):
#     """
#     Crée 10 impacts de foudre autour du lieu surveillé
#     """
#     help = "Crée 10 impacts de foudre autour du lieu surveillé"
#     # MSE = sum((y - t)**2)
#     def handle(self, *args, **options):
#         for i in range(NB_IMPACTS):
#             dy_km = random.uniform(-rayon_km, rayon_km) # NORD - SUD
#             dx_km = random.uniform(-rayon_km, rayon_km) # EST
#             lat = LATITUDE + dy_km / km_par_degre
#             lon = LONGITUDE + dx_km / (km_par_degre * cos(radians(LATITUDE)))

#             Impact.objects.create(
#                 latitude=lat,
#                 releve_id=None,
#                 longitude=lon,
#                 cellule_id=None,
#                 latitude=lat,
#                 longitude=lon,
#                 distance_km=(dx_km**2 + dy_km**2)**0.5,
#                 direction_cardinale=random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
#                 direction_deg=random.uniform(0, 360), # Random pour l'instant
#                 intensite_ka=random.uniform(0, 100), # Random pour l'instant
#                 categorie=random.choice(['CG-', 'CG+', 'IC']), # Random pour l'instant
#                 horodatage=timezone.now(),
#             )

#         self.stdout.write(self.style.SUCCESS(
#             f"{NB_IMPACTS} impacts factices"
#         ))



def generer_impacts(lat_ref: float, lon_ref: float, rayon_km: float, nb_impacts: int = 10):
    """Fonction qui permet de générer un impact

    Args:
        lat_ref (float): Latitude de la référence
        lon_ref (float): Longitude de la référence
        rayon_km (float): Rayon en kilomètres
        nb_impacts (int, optional): Nombre d'impacts à générer. Par défaut à 10.
    """
    pass





def generer_un_impact(lat_ref: float = LATITUDE, lon_ref: float = LONGITUDE, rayon_km: float = 300.0) -> dict:
    """Fonction qui permet de générer un impact

    Args:
        lat_ref (float): Latitude de la référence
        lon_ref (float): Longitude de la référence
        rayon_km (float): Rayon en kilomètres
    """
    dy_km = random.uniform(-rayon_km, rayon_km)
    dx_km = random.uniform(-rayon_km, rayon_km)

    lat = lat_ref + dy_km / km_par_degre
    lon = lon_ref + dx_km / (km_par_degre * cos(radians(lat_ref)))

    return {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4)
    }


if __name__ == "__main__":
    impact = generer_un_impact(rayon_km=500.0)
    print("Impact généré :", impact)
