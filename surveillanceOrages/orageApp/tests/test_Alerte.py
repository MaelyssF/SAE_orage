from django.test import TransactionTestCase
from orageApp.models import Alerte
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
import datetime
from orageApp.tests import utils

class AlerteModelTest(TransactionTestCase): # TransactionTestCase au lieu de TestCase car on teste les comportements de la base de données https://docs.djangoproject.com/en/6.1/topics/testing/tools/#django.test.TestCase
    def setUp(self):
        mold = utils.Mold()
        self.alerte = mold.create_alerte()

    def test_creation(self):
        self.assertEqual(self.alerte.motif, "rapprochement orage")

    def test_string_representation(self):
        self.assertEqual(str(self.alerte), f"Alerte n°{self.alerte.id_alerte}")

    def test_updating(self):
        self.alerte.motif = "rapprochement tempête"
        self.alerte.save()
        # Récupérer l'objet mis à jour
        updated_alerte = Alerte.objects.get(id_alerte=self.alerte.id_alerte)
        self.assertEqual(updated_alerte.motif, "rapprochement tempête")

    def test_deletion(self):
        self.alerte.delete()
        self.assertEqual(Alerte.objects.count(), 0)

    def test_constraints(self):
        def creation_err_niv_alerte():
            self.alerte = Alerte.objects.get(id_alerte=self.alerte.id_alerte)
            self.alerte.niveau_alerte = 865
            self.alerte.save()

        self.assertRaises(IntegrityError, creation_err_niv_alerte) 
        