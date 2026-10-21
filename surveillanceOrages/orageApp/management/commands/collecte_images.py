import hashlib
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

import requests

from orageApp.models import Releve

URL = "https://www.meteociel.fr/obs/foudre/latest.gif"
OUT_DIR = Path("data/images")
INTERVAL_S = 300        # 5 min minimum
MAX_BACKOFF_S = 3600    # Plafond de backoff à 1 heure en cas de panne prolongée

# HEADERS = {
#     # User-Agent : nom du projet + contact
#     "User-Agent": "ProjetUniv-SurveillanceOrages/0.1 (contact: asma.hachelef@etu.univ-orleans.fr)"
# }


OUT_DIR.mkdir(exist_ok=True)
session = requests.Session()
# session.headers.update(HEADERS)

last_hash = None
current_backoff = INTERVAL_S

print("Récupération données Météociel...")

while True:
    try:
        reponse = requests.get(URL, timeout=20)

        if reponse.status_code in (403, 429):
            print(f"[{datetime.now()}] Refus du site (HTTP {reponse.status_code}), arrêt de sécurité.")
            break
        reponse.raise_for_status()

        # Calcul du hash pour détecter les doublons
        digest = hashlib.sha256(reponse.content).hexdigest()
        if digest == last_hash:
            print("Image identique, rien enregistré.")
        else:
            last_hash = digest
            nom = datetime.now(ZoneInfo("Europe/Paris")).strftime("impacts_%Y%m%dT%H%M%SZ.png")
            fichier_chemin= (OUT_DIR / nom)
            fichier_chemin.write_bytes(reponse.content)
            print("Image enregistrée :", nom)

            # Enregistrement dans la base de données Django (RELEVE)
            nouveau_releve = Releve.objects.create(
                horodatage_donnee=datetime.now(ZoneInfo("Europe/Paris")),
                horodatage_analyse=datetime.now(ZoneInfo("Europe/Paris")),
                image_source=str(fichier_chemin),
                statut="ok"
                # lieu_id est laissé à NULL car c'est une image globale de la France
            )
            print(f"[{datetime.now()}] Relevé inséré en BDD (ID: {nouveau_releve.id_releve})")
        # Réinitialisation du backoff en cas de succès
        current_backoff = INTERVAL_S
        time.sleep(INTERVAL_S)

    except requests.RequestException as e:
        print(f"[{datetime.now()}] Erreur réseau ou HTTP : {e}")
        prochaine_attente = min(current_backoff * 2, MAX_BACKOFF_S)
        print(f"Nouvelle tentative dans {prochaine_attente} secondes...")
        time.sleep(prochaine_attente)
        current_backoff = prochaine_attente
    except Exception as e:
        print(f"[{datetime.now()}] Erreur inattendue : {e}")
        time.sleep(INTERVAL_S)