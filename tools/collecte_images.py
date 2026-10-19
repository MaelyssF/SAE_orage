import hashlib
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

import requests

URL = "https://www.meteociel.fr/obs/foudre/latest.gif"
OUT_DIR = Path("data/images")
INTERVAL_S = 300          # 5 min minimum
MAX_BACKOFF_S = 3600

HEADERS = {
    # User-Agent : nom du projet + contact
    "User-Agent": "ProjetUniv-SurveillanceOrages/0.1 (contact: prenom.nom@univ.fr)"
}

OUT_DIR.mkdir(exist_ok=True)
session = requests.Session()
session.headers.update(HEADERS)

last_hash = None

while True:
    try:
        r = requests.get(URL, headers=HEADERS, timeout=20)

        if r.status_code in (403, 429):
            print("Refus du site, arrêt.")
            break
        r.raise_for_status()

        digest = hashlib.sha256(r.content).hexdigest()
        if digest == last_hash:
            print("Image identique, rien enregistré.")
        else:
            last_hash = digest
            nom = datetime.now(ZoneInfo("Europe/Paris")).strftime("impacts_%Y%m%dT%H%M%SZ.png")
            (OUT_DIR / nom).write_bytes(r.content)
            print("Enregistrée :", nom)

    except requests.RequestException as e:
        print("Erreur :", e)

    time.sleep(INTERVAL_S)