from django.test import TransactionTestCase
from orageApp.models import Episode, Lieu_Surveille, Scenario_Simulation, Releve
from django.db.utils import IntegrityError
from datetime import datetime as dt
import datetime
from orageApp.tests import utils

class ReleveModelTest(TransactionTestCase):
    def setUp(self):
        mold = utils.Mold()
        self.releve = mold.create_releve()

    def test_creation(self):
        self.assertEqual(self.releve.lieu_id.nom_lieu, "Maison")
        self.assertEqual(self.releve.horodatage_donnee, dt(2026, 10, 20, 8, 30, 45, tzinfo=datetime.timezone.utc))

    def test_string_representation(self):
        self.assertEqual(str(self.releve), f"Releve n°{self.releve.id_releve} de {self.releve.horodatage_donnee}")

    def test_updating(self):
        self.releve.image_source = "https://domain.com/image2.png"
        self.releve.save()
        # Récupérer l'objet mis à jour
        updated_releve = Releve.objects.get(id_releve=self.releve.id_releve)
        self.assertEqual(updated_releve.image_source, "https://domain.com/image2.png")

    def test_deletion(self):
        self.releve.delete()
        self.assertEqual(Releve.objects.count(), 0)

    def test_constraints(self):
        def creation_err_niv_act_a_6():
            self.releve = Releve.objects.get(id_releve=self.releve.id_releve)
            self.releve.niveau_activite = 6
            self.releve.save()
        
        def creation_err_statut():
            self.releve = Releve.objects.get(id_releve=self.releve.id_releve)
            self.releve.statut = "celibataire"
            self.releve.save()

        def creation_err_indic_act():
            self.releve = Releve.objects.get(id_releve=self.releve.id_releve)
            self.releve.indicateur_activite = "sportive"
            self.releve.save()

        def creation_err_horodatage():
            self.releve = Releve.objects.get(id_releve=self.releve.id_releve)
            self.releve.horodatage_analyse = dt(2026, 10, 20, 8, 20, 12, tzinfo=datetime.timezone.utc)
            self.releve.save()

        self.assertRaises(IntegrityError, creation_err_niv_act_a_6) 
        self.assertRaises(IntegrityError, creation_err_statut) 
        self.assertRaises(IntegrityError, creation_err_indic_act)
        self.assertRaises(IntegrityError, creation_err_horodatage) 