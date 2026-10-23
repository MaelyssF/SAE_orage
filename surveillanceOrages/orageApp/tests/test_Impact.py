from django.test import TransactionTestCase
from orageApp.models import Impact
from django.db.utils import IntegrityError
from datetime import datetime as dt
import datetime
from orageApp.tests import utils

class ImpactObservationModelTest(TransactionTestCase):
    def setUp(self):
        mold = utils.Mold()
        self.impact = mold.create_impact()

    def test_creation(self):
        self.assertEqual(self.impact.intensite_ka, 33.5)

    def test_string_representation(self):
        self.assertEqual(str(self.impact), f"Impact n°{self.impact.id_impact}")

    def test_updating(self):
        self.impact.direction_cardinale = "NOO"
        self.impact.save()
        # Récupérer l'objet mis à jour
        updated_impact = Impact.objects.get(id_impact=self.impact.id_impact)
        self.assertEqual(updated_impact.direction_cardinale, "NOO")

    def test_deletion(self):
        self.impact.delete()
        self.assertEqual(Impact.objects.count(), 0)

    def test_constraints(self):
        def creation_err_cat_modif():
            self.impact = Impact.objects.get(id_impact=self.impact.id_impact)
            self.impact.categorie = "travailleur salarié"
            self.impact.save()
        
        self.assertRaises(IntegrityError, creation_err_cat_modif) 
