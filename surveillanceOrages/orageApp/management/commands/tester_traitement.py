from pathlib import Path
import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nom_de_ton_projet.settings')
django.setup()

from mon_app.models import Releve
# Importe ta fonction de traitement depuis ton fichier de traitement d'images
# (par exemple : from traitement_images import traiter_image_meteociel)

def lancer_test_local():
    chemin_image = Path("data/images/image_ab6d59.jpg")
    
    if not chemin_image.exists():
        print(f"❌ Le fichier {chemin_image} est introuvable.")
        return

    print(f"🔍 Analyse de l'image de test : {chemin_image.name}")
    
    # Optionnel : Créer un faux relevé en base pour associer le test si ton code en a besoin
    releve_test = Releve.objects.create(
        image_source=str(chemin_image),
        statut="test"
    )
    
    # Appel de ton traitement d'image
    # impacts = traiter_image_meteociel(releve_test)
    print(f"✅ Test terminé avec succès pour le relevé ID : {releve_test.id_releve}")

if __name__ == "__main__":
    lancer_test_local()