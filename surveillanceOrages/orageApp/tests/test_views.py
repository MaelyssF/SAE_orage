from django.test import TestCase
from django.urls import reverse
from orageApp.models import *

class CarteViewTest(TestCase):

    # test url page d'accueil
    def test_status_code(self):
        response = self.client.get(reverse('carte'))
        self.assertEqual(response.status_code, 200)

    # test contenu de la page d'accueil
    def test_home_content(self):
        response = self.client.get(reverse('carte'))
        #self.assertContains(response, 'Hello Django !')

