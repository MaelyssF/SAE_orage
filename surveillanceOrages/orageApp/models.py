from django.db import models

# Create your models here.

class Auth_User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, null=False)
    email = models.EmailField(max_length=254, null=False)

    def __str__(self):
        return f"Utilisateur n°${self.id} ${self.username}"

    class Meta:
        db_table = "auth_user"

class Profil_Notification(models.Model):
    CANAUX = models.TextChoices("CANAUX", "email telegram web")
    SENSIBILITE = models.TextChoices("SENSIBILITE", "faible moyenne elevee")

    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Auth_User, on_delete=models.CASCADE, related_name="user_notification", unique=True)
    notifications_actives = models.BooleanField(default=True)
    canal = models.CharField(max_length=20, default="email", choices=CANAUX)
    sensibilite = models.CharField(max_length=20, default="moyenne", choices=SENSIBILITE)

    def __str__(self):
        return f"Profil_Notification d'utilisateur n°${self.user_id}"

    class Meta:
        db_table = "profil_notification"

class Lieu_Surveille(models.Model):
    id_lieu = models.AutoField(primary_key=True)
    nom_lieu = models.CharField(max_length=100, null=False) # null = False est par défaut
    latitude = models.FloatField()
    longitude = models.FloatField()
    code_departement = models.CharField(max_length=5)
    rayon_proche_km = models.FloatField(default=20)
    rayon_large_km = models.FloatField(default=60)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"Lieu_Surveille ${self.nom_lieu}"

    class Meta:
        db_table = "lieu_surveille"                                                                                                                                                                                                                    

class Scenario_Simulation(models.Model):
    id_scenario = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=150)
    type_scenario = models.CharField(max_length=50)
    graine_aleatoire = models.IntegerField(default=42)
    direction_initiale_deg = models.FloatField()
    distance_initiale_km = models.FloatField()
    nb_impacts = models.IntegerField()
    etendue_km = models.FloatField()
    bruit_parasite = models.FloatField(default=0)
    nb_releves = models.IntegerField(default=6)
    intervalle_min = models.IntegerField(default=10)
    vitesse_kmh = models.FloatField()
    distance_min_reglee_km = models.FloatField(default=0)

    def __str__(self):
        return f"Scenario_Simulation n°${self.id_scenario} ${self.nom}"

    class Meta:
        db_table = "scenario_simulation"

class Episode(models.Model):
    id_episode = models.AutoField(primary_key=True)
    lieu_id = models.ForeignKey(Lieu_Surveille, on_delete=models.CASCADE, related_name="lieu_episode")
    debut = models.DateTimeField()
    fin = models.DateTimeField(null=True)

    def __str__(self):
        return f"Episode n°${self.id_episode}"

    class Meta:
        db_table = "episode"

class Releve(models.Model):
    STATUTS = models.TextChoices("STATUTS", "ok ancien indisponible")
    INDICATEURS_ACTIVITE = models.TextChoices("INDICATEURS_ACTIVITE", "Nulle Faible Moderee Forte Violente")

    id_releve = models.AutoField(primary_key=True)
    lieu_id = models.ForeignKey(Lieu_Surveille, on_delete=models.CASCADE, related_name="lieu_releve")
    episode_id = models.ForeignKey(Episode, on_delete=models.SET_NULL, related_name="episode_releve", null=True)
    scenario_id = models.ForeignKey(Scenario_Simulation, on_delete=models.SET_NULL, related_name="scenario_releve", null=True)
    horodatage_donnee = models.DateTimeField()
    horodatage_analyse = models.DateTimeField()
    statut = models.CharField(max_length=30, default="ok", choices=STATUTS)
    image_source = models.CharField(max_length=255)
    indicateur_activite = models.CharField(max_length=30, default="Faible", choices=INDICATEURS_ACTIVITE)
    niveau_activite = models.IntegerField(default=1)

    def __str__(self):
        return f"Releve n°${self.id_releve} de ${self.horodatage_donnee}"

    class Meta:
        db_table = "releve"
        constraints = [
            models.CheckConstraint(condition=models.Q(niveau_activite__gte=1) & models.Q(niveau_activite__lte=5), name="niveau_activite_1_a_5"),
        ]

class Cellule(models.Model):
    STATUTS = models.TextChoices("STATUTS", "activee dissipee")

    id_cellule = models.AutoField(primary_key=True)
    episode_id = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="episode_cellule")
    identifiant_externe = models.CharField(max_length=50)
    premiere_detection = models.DateTimeField()
    derniere_detection = models.DateTimeField()
    statut = models.CharField(max_length=20, default="activee", choices=STATUTS)

    def __str__(self):
        return f"Cellule n°${self.id_cellule}"

    class Meta:
        db_table = "cellule"

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