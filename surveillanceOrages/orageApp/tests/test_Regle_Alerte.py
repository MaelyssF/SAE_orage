from django.test import TransactionTestCase
from orageApp.models import Lieu_Surveille, Regle_Alerte
from django.db.utils import IntegrityError
from orageApp.tests import utils

class RegleAlerteModelTest(TransactionTestCase): # TransactionTestCase au lieu de TestCase car on teste les comportements de la base de données https://docs.djangoproject.com/en/6.1/topics/testing/tools/#django.test.TestCase
    def setUp(self):
        mold = utils.Mold()
        self.regle, self.lieu = mold.create_regle(), mold.create_lieu()

    def test_creation(self):
        self.assertEqual(self.regle.niveau_regle_alerte, 1)

    def test_string_representation(self):
        self.assertEqual(str(self.regle), f"Regle_Alerte n°{self.regle.id_regle_alerte}")

    def test_updating(self):
        self.regle.seuil_nb_impacts = 6
        self.regle.save()
        # Récupérer l'objet mis à jour
        updated_regle = Regle_Alerte.objects.get(id_regle_alerte=self.regle.id_regle_alerte)
        self.assertEqual(updated_regle.seuil_nb_impacts, 6)

    def test_deletion(self):
        self.regle.delete()
        self.assertEqual(Regle_Alerte.objects.count(), 0)

    def test_constraints(self):
        def creation_err_niv_regle():
            self.regle = Regle_Alerte.objects.get(id_regle_alerte=self.regle.id_regle_alerte)
            self.regle.niveau_regle_alerte = 8
            self.regle.save()

        def creation_err_type_alerte():
            self.regle = Regle_Alerte.objects.get(id_regle_alerte=self.regle.id_regle_alerte)
            self.regle.type_alerte = "au lait"
            self.regle.save()

        self.assertRaises(IntegrityError, creation_err_niv_regle) 
        self.assertRaises(IntegrityError, creation_err_type_alerte) 