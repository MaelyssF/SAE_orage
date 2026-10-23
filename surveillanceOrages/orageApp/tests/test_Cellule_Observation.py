from django.test import TransactionTestCase
from orageApp.models import Episode, Lieu_Surveille, Scenario_Simulation, Releve, Cellule, Cellule_Observation
from datetime import datetime as dt
import datetime
from orageApp.tests import utils

class CelluleObservationModelTest(TransactionTestCase):
    def setUp(self):
        mold = utils.Mold()
        self.cellule_observation = mold.create_cellule_observation()

    def test_creation(self):
        self.assertEqual(self.cellule_observation.nb_impacts, 5)

    def test_string_representation(self):
        self.assertEqual(str(self.cellule_observation), f"Cellule_Observation n°{self.cellule_observation.id_observation}")

    def test_updating(self):
        self.cellule_observation.distance_min_prevue_km = 10.0
        self.cellule_observation.save()
        # Récupérer l'objet mis à jour
        updated_cellule_observation = Cellule_Observation.objects.get(id_observation=self.cellule_observation.id_observation)
        self.assertEqual(updated_cellule_observation.distance_min_prevue_km, 10.0)

    def test_deletion(self):
        self.cellule_observation.delete()
        self.assertEqual(Cellule_Observation.objects.count(), 0)
