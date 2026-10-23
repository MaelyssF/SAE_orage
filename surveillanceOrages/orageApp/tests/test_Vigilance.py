from django.test import TransactionTestCase
from orageApp.models import Lieu_Surveille, Vigilance
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from datetime import datetime, timedelta, timezone

class VigilanceModelTest(TransactionTestCase): # TransactionTestCase au lieu de TestCase car on teste les comportements de la base de données https://docs.djangoproject.com/en/6.1/topics/testing/tools/#django.test.TestCase
    def setUp(self):
        self.lieu = Lieu_Surveille.objects.create(nom_lieu="Maison", 
                                                  latitude=47.843058, 
                                                  longitude=1.926602, 
                                                  code_departement=45067)
        self.vigilance = Vigilance.objects.create(fin_validite=datetime.now(tz=timezone.utc) + timedelta(hours=2),
                                                  lieu_id=self.lieu)

    def test_creation(self):
        self.assertEqual(self.vigilance.niveau_vigilance, 1)

    def test_string_representation(self):
        self.assertEqual(str(self.vigilance), f"Vigilance n°{self.vigilance.id_vigilance} niveau {self.vigilance.niveau_vigilance}")

    def test_updating(self):
        self.vigilance.source = "Météociel"
        self.vigilance.save()
        # Récupérer l'objet mis à jour
        updated_vigilance = Vigilance.objects.get(id_vigilance=self.vigilance.id_vigilance)
        self.assertEqual(updated_vigilance.source, "Météociel")

    def test_deletion(self):
        self.vigilance.delete()
        self.assertEqual(Vigilance.objects.count(), 0)

    def test_constraints(self):
        def creation_err_niv_vigilance():
            self.vigilance = Vigilance.objects.get(id_vigilance=self.vigilance.id_vigilance)
            self.vigilance.niveau_vigilance = 8
            self.vigilance.save()

        def creation_err_debut_inf_fin():
            self.vigilance = Vigilance.objects.get(id_vigilance=self.vigilance.id_vigilance)
            self.vigilance.fin_validite = datetime(2025, 10, 20, 12, 7, 16, tzinfo=timezone.utc)
            self.vigilance.save()

        self.assertRaises(IntegrityError, creation_err_debut_inf_fin) 
        self.assertRaises(IntegrityError, creation_err_niv_vigilance) 