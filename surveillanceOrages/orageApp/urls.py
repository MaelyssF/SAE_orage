from django.urls import path
from orageApp.views import carteView

urlpatterns = [
    path('carte/', carteView, name='carte')
]
