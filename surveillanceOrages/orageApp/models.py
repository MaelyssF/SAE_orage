from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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
    # canal =
    # sensibilte =
    pass

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
    id_regle_alerte = models.AutoField(primary_key=True)
    type_alerte = models.CharField(max_length=50, db_column='type_alerte', default='orage')
    niveau = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)], db_column='niveau')
    seuil_distance = models.FloatField(default=0.0, db_column='seuil_distance')
    seuil_nb_impacts = models.IntegerField(default=0, db_column='seuil_nb_impacts')
    delai_anti_repetition = models.IntegerField(default=0, db_column='delai_anti_repetition')
    # utilise_vigilance = models.BooleanField(default=False, db_column='utilise_vigilance')
    actif = models.BooleanField(default=True, db_column='actif')
    lieu_surveille = models.ForeignKey(
        Lieu_Surveille, on_delete=models.CASCADE, db_column='lieu_surveille_id', related_name='regles_alerte',
    )

    class Meta:
        db_table = "REGLE_ALERTE"

class Alerte(models.Model):
    id_alerte = models.AutoField(primary_key=True)
    niveau = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)], db_column='niveau')
    motif = models.CharField(max_length=255, db_column='motif', default='Alerte de niveau 1')
    distance = models.FloatField(default=0.0, db_column='distance')
    declenchee_le = models.DateTimeField(auto_now_add=True, db_column='declenchee_le')

    episode = models.ForeignKey(
        Episode, on_delete=models.CASCADE, db_column='episode_id', related_name='alertes',
    )
    regle_alerte = models.ForeignKey(
        Regle_Alerte, on_delete=models.CASCADE, db_column='regle_alerte_id', related_name='alertes',
    )
    cellule = models.ForeignKey(
        Cellule, on_delete=models.CASCADE, db_column='cellule_id', related_name='alertes',
    )
    vigilance = models.ForeignKey(
        Vigilance, on_delete=models.CASCADE, db_column='vigilance_id', related_name='alertes',
    )

    class Meta:
        db_table = "ALERTE"

class Notification(models.Model):
    id_notification = models.AutoField(primary_key=True)
    canal = models.CharField(max_length=20, db_column='canal', default='email')
    statut = models.CharField(max_length=20, default='en_attente')
    envoyee_le = models.DateTimeField(auto_now_add=True, db_column='envoyee_le')

    alerte = models.ForeignKey(
        Alerte, on_delete=models.PROTECT, db_columns='alerte_id', related_name='notifications',
    )
    user = models.ForeignKey(
        Auth_User, on_delete=models.CASCADE, db_columns='user_id',
    )

    class Meta:
        db_table = "NOTIFICATION"