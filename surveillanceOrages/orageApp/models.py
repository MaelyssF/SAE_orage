from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

# Create your models here.

# class Auth_User(models.Model): # On ne crée pas cette table qui est créée nativement par Django
#     id = models.AutoField(primary_key=True)
#     username = models.CharField(max_length=150, unique=True, null=False)
#     email = models.EmailField(max_length=254, null=False)

#     def __str__(self):
#         return f"Utilisateur n°${self.id} ${self.username}"

#     class Meta:
#         db_table = "settings.AUTH_USER_MODEL"

class Profil_Notification(models.Model):
    CANAUX = models.TextChoices("CANAUX", "email telegram web")
    SENSIBILITE = models.TextChoices("SENSIBILITE", "faible moyenne elevee")

    id = models.AutoField(primary_key=True)
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_notification") # Équivalent à ForeignKey avec unique=True
    notifications_actives = models.BooleanField(default=True)
    canal = models.CharField(max_length=20, default="email", choices=CANAUX)
    sensibilite = models.CharField(max_length=20, default="moyenne", choices=SENSIBILITE)

    def __str__(self):
        return f"Profil_Notification d'utilisateur n°${self.user_id}"

    class Meta:
        db_table = "PROFIL_NOTIFICATION"
        # It is strongly advised that you use lowercase table names when you override the table name via db_table, particularly if you are using the MySQL backend
        # https://docs.djangoproject.com/en/6.1/ref/models/options/#db-table
        # Y penser si on a des problèmes

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
        db_table = "LIEU_SURVEILLE"                                                                                                                                                                                                                    

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
        db_table = "SCENARIO_SIMULATION"

class Episode(models.Model):
    id_episode = models.AutoField(primary_key=True)
    lieu_id = models.ForeignKey(Lieu_Surveille, on_delete=models.CASCADE, related_name="lieu_episode")
    debut = models.DateTimeField()
    fin = models.DateTimeField(null=True)

    def __str__(self):
        return f"Episode n°${self.id_episode}"

    class Meta:
        db_table = "EPISODE"

class Releve(models.Model):
    STATUTS = models.TextChoices("STATUTS", "ok ancien indisponible")
    INDICATEURS_ACTIVITE = models.TextChoices("INDICATEURS_ACTIVITE", "Nulle Faible Moderee Forte Violente")

    id_releve = models.AutoField(primary_key=True)
    lieu_id = models.ForeignKey(Lieu_Surveille, on_delete=models.CASCADE, related_name="lieu_releve", null=True, blank=True)
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
        db_table = "RELEVE"
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
        db_table = "CELLULE"

class Cellule_Observation(models.Model):
    id_observation = models.AutoField(primary_key=True)
    latitude_centre = models.FloatField(null=False)
    longitude_centre = models.FloatField(null=False)
    etendue_km = models.FloatField(null=False)
    nb_impacts = models.IntegerField(null=False)
    niveau_activite = models.IntegerField(null=False, default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    direction_deplacement_deg = models.FloatField()
    vitesse_kmh = models.FloatField()
    distance_min_prevue_km = models.FloatField()
    delai_arrivee_min = models.IntegerField()
    incertitude = models.BooleanField(default=False, null=False)
    cellule_id = models.ForeignKey(
        Cellule, on_delete=models.CASCADE, related_name='observations',
    )
    releve_id = models.ForeignKey(
        Releve, on_delete=models.CASCADE, related_name='observations',
    )

    class Meta:
        db_table = "CELLULE_OBSERVATION"

class Impact(models.Model):
    id_impact = models.AutoField(primary_key=True)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    distance_km = models.FloatField(null=False)
    direction_cardinale = models.CharField(max_length=10, null=False)
    direction_deg = models.FloatField(null=False)
    intensite_ka = models.FloatField('intensité en kiloampères')
    categorie = models.CharField('Cloud-to-Ground et Cloud-to-Intracloud' ,max_length=10, default='CG-')
    horodatage = models.DateTimeField(null=False)
    releve_id = models.ForeignKey(
        Releve, on_delete=models.CASCADE, related_name='impacts',
    )
    cellule_id = models.ForeignKey(
        Cellule, on_delete=models.CASCADE, related_name='impacts',
    )
    
    class Meta:
        db_table = "IMPACT"

class Vigilance(models.Model):
    ALERTE_CHOICES = {
        0 : "vert",
        1 : "jaune",
        2 : "orange",
        3 : "rouge",
    }
    id_vigilance = models.AutoField(primary_key=True)
    niveau_vigilance = models.IntegerField(default=1, null=False, choices=ALERTE_CHOICES.items(), validators=[MinValueValidator(0), MaxValueValidator(3)], db_column='niveau')
    type_phenomene = models.CharField(max_length=50, null=False, db_column='type_phenomene', default='Orages')
    debut_validite = models.DateTimeField(null=False, auto_now_add=True, db_column='debut_validite')
    fin_validite = models.DateTimeField(null=False, db_column='fin_validite')
    mise_a_jour_le = models.DateTimeField(auto_now=True, null=False, db_column='mise_a_jour_le')
    source = models.CharField(max_length=50, db_column='source', default='Météo-France')
    lieu_id = models.ForeignKey(
        Lieu_Surveille, on_delete=models.CASCADE, db_column='lieu_id', related_name='vigilances',
    )

    class Meta:
        db_table = "VIGILANCE"

class Regle_Alerte(models.Model):
    id_regle_alerte = models.AutoField(primary_key=True)
    type_alerte = models.CharField(max_length=50, null=False, db_column='type_alerte', default='orage')
    niveau_regle_alerte = models.IntegerField(default=1, null=False, validators=[MinValueValidator(1), MaxValueValidator(5)], db_column='niveau')
    seuil_distance = models.FloatField(default=0.0, db_column='seuil_distance')
    seuil_nb_impacts = models.IntegerField(default=0, db_column='seuil_nb_impacts')
    delai_anti_repetition = models.IntegerField(default=30, null=False, db_column='delai_anti_repetition')
    # utilise_vigilance = models.BooleanField(default=False, null=False, db_column='utilise_vigilance')
    actif = models.BooleanField(default=True, null=False, db_column='actif')
    lieu_surveille = models.ForeignKey(
        Lieu_Surveille, on_delete=models.CASCADE, db_column='lieu_surveille_id', related_name='regles_alerte',
    )

    class Meta:
        db_table = "REGLE_ALERTE"

class Alerte(models.Model):
    id_alerte = models.AutoField(primary_key=True)
    niveau_alerte = models.IntegerField(default=1, null=False, validators=[MinValueValidator(1), MaxValueValidator(5)], db_column='niveau')
    motif = models.CharField(max_length=255, null=False, db_column='motif', default='Alerte de niveau 1')
    distance = models.FloatField(default=0.0, db_column='distance')
    vigilance_contributive = models.BooleanField(default=False, null=False, db_column='vigilance_contributive')
    declenchee_le = models.DateTimeField(auto_now_add=True, null=False, db_column='declenchee_le')

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
    canal = models.CharField(null=False, max_length=20, db_column='canal', default='email')
    statut = models.CharField(null=False, max_length=20, default='en_attente')
    envoyee_le = models.DateTimeField(auto_now_add=True, db_column='envoyee_le')

    alerte = models.ForeignKey(
        Alerte, on_delete=models.CASCADE, db_column='alerte_id', related_name='notifications',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='user_id',
    )

    class Meta:
        db_table = "NOTIFICATION"