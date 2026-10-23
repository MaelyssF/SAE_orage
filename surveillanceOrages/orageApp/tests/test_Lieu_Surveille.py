from django.test import TestCase
from orageApp.models import Lieu_Surveille

class LieuModelTest(TestCase):
    def setUp(self):
        self.lieu = Lieu_Surveille.objects.create(nom_lieu="Maison", 
                                                  latitude=47.843058, 
                                                  longitude=1.926602, 
                                                  code_departement=45067)

    def test_creation(self):
        self.assertEqual(self.lieu.rayon_proche_km, 20)
        self.assertEqual(self.lieu.rayon_large_km, 60)
        self.assertEqual(self.lieu.actif, True)

    def test_string_representation(self):
        self.assertEqual(str(self.lieu), f"Lieu_Surveille Maison")

    def test_updating(self):
        self.lieu.rayon_large_km = 80
        self.lieu.save()
        # Récupérer l'objet mis à jour
        updated_lieu = Lieu_Surveille.objects.get(nom_lieu="Maison")
        self.assertEqual(updated_lieu.rayon_large_km, 80)

    def test_deletion(self):
        self.lieu.delete()
        self.assertEqual(Lieu_Surveille.objects.count(), 0)
