from django.test import TestCase
from orageApp.models import Scenario_Simulation

class ScenarioSimulationModelTest(TestCase):
    def setUp(self):
        self.scenario_s = Scenario_Simulation.objects.create(nom_scenario="Scenario1", 
                                                             type_scenario="catastrophe", 
                                                             direction_initiale_deg=46.1, 
                                                             distance_initiale_km=13, 
                                                             nb_impacts=2, 
                                                             etendue_km=5.8, 
                                                             vitesse_kmh=74.2)

    def test_creation(self):
        self.assertEqual(self.scenario_s.graine_aleatoire, 42)
        self.assertEqual(self.scenario_s.bruit_parasite, 0)

    def test_string_representation(self):
        self.assertEqual(str(self.scenario_s), f"Scenario_Simulation n°{self.scenario_s.id_scenario} {self.scenario_s.nom_scenario}")

    def test_updating(self):
        self.scenario_s.intervalle_min = 25
        self.scenario_s.save()
        # Récupérer l'objet mis à jour
        updated_scenario_s = Scenario_Simulation.objects.get(nom_scenario="Scenario1")
        self.assertEqual(updated_scenario_s.intervalle_min, 25)

    def test_deletion(self):
        self.scenario_s.delete()
        self.assertEqual(Scenario_Simulation.objects.count(), 0)
