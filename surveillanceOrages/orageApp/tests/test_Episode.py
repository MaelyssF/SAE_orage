from django.test import TransactionTestCase
from orageApp.models import Episode, Lieu_Surveille
from django.db.utils import IntegrityError
from datetime import datetime as dt
import datetime
from orageApp.tests import utils

class EpisodeModelTest(TransactionTestCase):
    def setUp(self):
        mold = utils.Mold()
        self.episode, self.lieu = mold.create_episode(), mold.create_lieu()

    def test_creation(self):
        self.assertEqual(self.episode.lieu_id.nom_lieu, "Maison")
        self.assertEqual(self.episode.debut, dt(2026, 10, 20, 6, 32, 29, tzinfo=datetime.timezone.utc))

    def test_string_representation(self):
        self.assertEqual(str(self.episode), f"Episode n°{self.episode.id_episode}")

    def test_updating(self):
        self.episode.debut = dt(2026, 10, 20, 7, 32, 29, tzinfo=datetime.timezone.utc)
        self.episode.save()
        # Récupérer l'objet mis à jour
        updated_episode = Episode.objects.get(id_episode=self.episode.id_episode)
        self.assertEqual(updated_episode.debut, dt(2026, 10, 20, 7, 32, 29, tzinfo=datetime.timezone.utc))

    def test_deletion(self):
        self.episode.delete()
        self.assertEqual(Episode.objects.count(), 0)

    def test_constraints(self):
        creation_err_debut_inf_fin = lambda : Episode.objects.create(lieu_id=self.lieu,  
                                                                     debut=dt(2026, 10, 20, 12, 7, 16, tzinfo=datetime.timezone.utc),
                                                                     fin=dt(2026, 10, 20, 6, 32, 29, tzinfo=datetime.timezone.utc))
        
        def creation_err_debut_inf_fin_modif():
            self.episode = Episode.objects.get(id_episode=self.episode.id_episode)
            self.episode.fin = dt(2026, 10, 17, 6, 32, 29, tzinfo=datetime.timezone.utc)
            self.episode.save()

        self.assertRaises(IntegrityError, creation_err_debut_inf_fin)
        self.assertRaises(IntegrityError, creation_err_debut_inf_fin_modif)