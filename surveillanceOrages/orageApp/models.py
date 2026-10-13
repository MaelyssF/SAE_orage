from django.db import models

# Create your models here.

class Auth_User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, null=False)
    email = models.EmailField(max_length=254, unique=True, null=False)

    def __str__(self):
        return self.username

class Profil_Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE, related_name="user")
    notifications_actives = models.BooleanField()
    canal =
    sensibilte =

class Lieu_Surveille(models.Model):
    pass

class Scenario_Simulation(models.Model):
    pass

class Episode(models.Model):
    pass

class Releve(models.Model):
    pass

class Cellule(models.Model):
    pass

class Cellule_Observation(models.Model):
    pass

class Impact(models.Model):
    pass

class Vigilance(models.Model):
    pass

class Regle_Alerte(models.Model):
    pass

class Alerte(models.Model):
    pass

class Notification(models.Model):
    pass