from django.test import TransactionTestCase
from orageApp.models import Episode, Lieu_Surveille, Cellule
from django.db.utils import IntegrityError
from datetime import datetime as dt
import datetime
from orageApp.tests import utils

class CelluleModelTest(TransactionTestCase):
    def setUp(self):
        mold = utils.Mold()
        self.cellule = mold.create_cellule()

    def test_creation(self):
        self.assertEqual(self.cellule.statut, "activee")

    def test_string_representation(self):
        self.assertEqual(str(self.cellule), f"Cellule n°{self.cellule.id_cellule}")

    def test_updating(self):
        self.cellule.identifiant_externe = "identifiant_2"
        self.cellule.save()
        # Récupérer l'objet mis à jour
        updated_cellule = Cellule.objects.get(id_cellule=self.cellule.id_cellule)
        self.assertEqual(updated_cellule.identifiant_externe, "identifiant_2")

    def test_deletion(self):
        self.cellule.delete()
        self.assertEqual(Cellule.objects.count(), 0)

    def test_constraints(self):
        def creation_err_statut():
            self.cellule = Cellule.objects.get(id_cellule=self.cellule.id_cellule)
            self.cellule.statut = "marie"
            self.cellule.save()

        def creation_err_1ere_detect_sup_2eme_detect():
            self.cellule = Cellule.objects.get(id_cellule=self.cellule.id_cellule)
            self.cellule.premiere_detection = dt(2026, 10, 20, 18, 36, 20, tzinfo=datetime.timezone.utc)
            self.cellule.save()

        self.assertRaises(IntegrityError, creation_err_statut)
        self.assertRaises(IntegrityError, creation_err_1ere_detect_sup_2eme_detect)