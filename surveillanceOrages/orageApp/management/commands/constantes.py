from pathlib import Path

# Orléans
LATITUDE = 47.9025
LONGITUDE = 1.9086


NB_IMPACTS = 10
KM_PAR_DEGRE = 111.0


# Centre par défaut de la cellule : coin nord-est de la France (Lorraine)
CELLULE_LATITUDE = 48.9
CELLULE_LONGITUDE = 6.6

# Temps entre deux impacts successifs d'une cellule, en secondes (fixe pour l'instant)
INTERVALLE_IMPACTS_S = 1.0

DOSSIER_SIMULATIONS = Path(__file__).resolve().parent.parent.parent / "simulations"
NB_IMPACTS_MAX = 5000
DUREE_MAX_S = 24 * 3600  # un impact ne peut pas tomber plus de 24 h après le début de la cellule