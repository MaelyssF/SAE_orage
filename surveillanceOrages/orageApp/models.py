from django.db import models

# Create your models here.

class Auth_User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, null=False)
    email = models.EmailField(max_length=254, unique=True, null=False)

    def __str__(self):
        return self.username

class Profil_Notification(models.Model):
    pass