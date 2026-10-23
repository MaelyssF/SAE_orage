from django.test import TransactionTestCase
from orageApp.models import Notification
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
import datetime
from orageApp.tests import utils

class NotifModelTest(TransactionTestCase): # TransactionTestCase au lieu de TestCase car on teste les comportements de la base de données https://docs.djangoproject.com/en/6.1/topics/testing/tools/#django.test.TestCase
    def setUp(self):
        mold = utils.Mold()
        self.notif = mold.create_notif()

    def test_creation(self):
        self.assertEqual(self.notif.canal, "email")

    def test_string_representation(self):
        self.assertEqual(str(self.notif), f"Notification n°{self.notif.id_notification}")

    def test_updating(self):
        self.notif.canal = "telegram"
        self.notif.save()
        # Récupérer l'objet mis à jour
        updated_notif = Notification.objects.get(id_notification=self.notif.id_notification)
        self.assertEqual(updated_notif.canal, "telegram")

    def test_deletion(self):
        self.notif.delete()
        self.assertEqual(Notification.objects.count(), 0)

    def test_constraints(self):
        def creation_err_statut():
            self.notif = Notification.objects.get(id_notification=self.notif.id_notification)
            self.notif.statut = "blesse"
            self.notif.save()

        def creation_err_canal():
            self.notif = Notification.objects.get(id_notification=self.notif.id_notification)
            self.notif.canal = "escargot immortel"
            self.notif.save()

        self.assertRaises(IntegrityError, creation_err_statut)
        self.assertRaises(IntegrityError, creation_err_canal)