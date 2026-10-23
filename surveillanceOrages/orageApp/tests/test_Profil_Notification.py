from django.test import TransactionTestCase
from orageApp.models import Profil_Notification
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from orageApp.tests import utils

class ProfilNotifModelTest(TransactionTestCase): # TransactionTestCase au lieu de TestCase car on teste les comportements de la base de données https://docs.djangoproject.com/en/6.1/topics/testing/tools/#django.test.TestCase
    def setUp(self):
        mold = utils.Mold()
        self.profil_notif, self.user = mold.create_profil_notif(), mold.create_user()

    def test_creation(self):
        self.assertEqual(self.profil_notif.notifications_actives, True)
        self.assertEqual(self.profil_notif.canal, "email")
        self.assertEqual(self.profil_notif.sensibilite, "moyenne")

    def test_string_representation(self):
        self.assertEqual(str(self.profil_notif), f"Profil_Notification d'utilisateur n°{self.profil_notif.user_id.id}")

    def test_updating(self):
        self.profil_notif.notifications_actives = False
        self.profil_notif.canal = "telegram"
        self.profil_notif.save()
        # Récupérer l'objet mis à jour
        updated_profil_notif = Profil_Notification.objects.get(user_id=self.user)

        self.assertEqual(updated_profil_notif.notifications_actives, False)
        self.assertEqual(updated_profil_notif.canal, "telegram")

    def test_deletion(self):
        self.profil_notif.delete()
        self.assertEqual(Profil_Notification.objects.count(), 0)

    def test_constraints(self):
        user2 = User.objects.create_user(username="test2", password="mdp_test2")
        creation_err_const_unique = lambda : Profil_Notification.objects.create(user_id=self.user)
        creation_err_check_statut = lambda : Profil_Notification.objects.create(user_id=user2, canal="potato", sensibilite="autre_potato")
        
        def creation_err_check_statut_modif():
            self.profil_notif = Profil_Notification.objects.get(user_id=self.user)
            self.profil_notif.canal = "pigeon voyageur"
            self.profil_notif.save()

        self.assertRaises(IntegrityError, creation_err_const_unique) # Vérifie qu'on lève une IntegrityError à cause de la contrainte unique qui n'est pas respectée
        self.assertRaises(IntegrityError, creation_err_check_statut) # Vérifie qu'on lève une IntegrityError à cause de la contrainte check statut qui n'est pas respectée
        self.assertRaises(IntegrityError, creation_err_check_statut_modif) # Vérifie qu'on lève une IntegrityError à cause de la contrainte check statut qui n'est pas respectée