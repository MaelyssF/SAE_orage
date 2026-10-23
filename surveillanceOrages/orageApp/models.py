from django.db import models
from django.db.models import Q, F
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

# Create your models here.

# class Auth_User(models.Model): # On ne crée pas cette table qui est créée nativement par Django
#     id = models.AutoField(primary_key=True)
#     username = models.CharField(max_length=150, unique=True, null=False)
#     email = models.EmailField(max_length=254, null=False)

#     def __str__(self):
#         return f"Utilisateur n°{self.id} {self.username}"

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
        return f"Profil_Notification d'utilisateur n°{self.user_id.id}"

    class Meta:
        db_table = "PROFIL_NOTIFICATION"
        # It is strongly advised that you use lowercase table names when you override the table name via db_table, particularly if you are using the MySQL backend
        # https://docs.djangoproject.com/en/6.1/ref/models/options/#db-table
        # Y penser si on a des problèmes
        constraints = [
            models.CheckConstraint(condition=Q(canal="email") | Q(canal="telegram") | Q(canal="web"), name="check_canal_profil_notif"),
            models.CheckConstraint(condition=Q(sensibilite="faible") | Q(sensibilite="moyenne") | Q(sensibilite="elevee"), name="check_sensibilite"),
        ]

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
        return f"Lieu_Surveille {self.nom_lieu}"

    class Meta:
        db_table = "LIEU_SURVEILLE"                                                                                                                                                                                                                    

class Scenario_Simulation(models.Model):
    id_scenario = models.AutoField(primary_key=True)
    nom_scenario = models.CharField(max_length=150)
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
        return f"Scenario_Simulation n°{self.id_scenario} {self.nom_scenario}"

    class Meta:
        db_table = "SCENARIO_SIMULATION"

class Episode(models.Model):
    id_episode = models.AutoField(primary_key=True)
    lieu_id = models.ForeignKey(Lieu_Surveille, on_delete=models.CASCADE, related_name="lieu_episode")
    debut = models.DateTimeField()
    fin = models.DateTimeField(null=True)

    def __str__(self):
        return f"Episode n°{self.id_episode}"

    class Meta:
        db_table = "EPISODE"
        constraints = [
            models.CheckConstraint(condition=models.Q(fin__gte=F("debut")), name="debut_inferieur_fin"),
        ]

class Releve(models.Model):
    STATUTS = models.TextChoices("STATUTS", "ok ancien indisponible")
    INDICATEURS_ACTIVITE = models.TextChoices("INDICATEURS_ACTIVITE", "nulle faible moderee forte violente")

    id_releve = models.AutoField(primary_key=True)
    lieu_id = models.ForeignKey(Lieu_Surveille, on_delete=models.CASCADE, related_name="lieu_releve")
    episode_id = models.ForeignKey(Episode, on_delete=models.SET_NULL, related_name="episode_releve", null=True)
    scenario_id = models.ForeignKey(Scenario_Simulation, on_delete=models.SET_NULL, related_name="scenario_releve", null=True)
    horodatage_donnee = models.DateTimeField()
    horodatage_analyse = models.DateTimeField()
    statut = models.CharField(max_length=30, default="ok", choices=STATUTS)
    image_source = models.CharField(max_length=255)
    indicateur_activite = models.CharField(max_length=30, default="faible", choices=INDICATEURS_ACTIVITE)
    niveau_activite = models.IntegerField(default=1)

    def __str__(self):
        return f"Releve n°{self.id_releve} de {self.horodatage_donnee}"

    class Meta:
        db_table = "RELEVE"
        constraints = [
            models.CheckConstraint(condition=models.Q(niveau_activite__gte=1) & models.Q(niveau_activite__lte=5), name="niveau_activite_1_a_5"),
            models.CheckConstraint(condition=Q(statut="ok") | Q(statut="ancien") | Q(statut="indisponible"), name="check_statut_releve"),
            models.CheckConstraint(condition=Q(indicateur_activite="nulle") | Q(indicateur_activite="faible") | Q(indicateur_activite="moderee") | Q(indicateur_activite="forte") | Q(indicateur_activite="violente"), name="check_indicateur_activite"),
            models.CheckConstraint(condition=models.Q(horodatage_analyse__gte=F("horodatage_donnee")), name="date_donnee_inf_analyse"),
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
        return f"Cellule n°{self.id_cellule}"

    class Meta:
        db_table = "CELLULE"
        constraints = [
            models.CheckConstraint(condition=Q(statut="activee") | Q(statut="dissipee"), name="check_statut_cellule"),
            models.CheckConstraint(condition=models.Q(derniere_detection__gte=F("premiere_detection")), name="1ere_detect_inf_2eme_detect"),
        ]

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

    def __str__(self):
        return f"Cellule_Observation n°{self.id_observation}"

    class Meta:
        db_table = "CELLULE_OBSERVATION"

class Impact(models.Model):
    CATS = models.TextChoices("CATS", "CG- CG+ IC")
    
    id_impact = models.AutoField(primary_key=True)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    distance_km = models.FloatField(null=False)
    direction_cardinale = models.CharField(max_length=10, null=False)
    direction_deg = models.FloatField(null=False)
    intensite_ka = models.FloatField('intensité en kiloampères')
    categorie = models.CharField('Cloud-to-Ground et Cloud-to-Intracloud' ,max_length=10, default='CG-', choices=CATS)
    horodatage = models.DateTimeField(null=False)
    releve_id = models.ForeignKey(
        Releve, on_delete=models.CASCADE, related_name='impacts',
    )
    cellule_id = models.ForeignKey(
        Cellule, on_delete=models.CASCADE, related_name='impacts',
    )

    def __str__(self):
        return f"Impact n°{self.id_impact}"
    
    class Meta:
        db_table = "IMPACT"
        constraints = [
            models.CheckConstraint(condition=Q(categorie="CG-") | Q(categorie="CG+") | Q(categorie="IC"), name="check_categorie"),
        ]

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
    debut_validite = models.DateTimeField(null=False, auto_now_add=True, db_column='debut_validite') # auto_now_add met automatiquement le champ à la date actuelle lors de la création
    fin_validite = models.DateTimeField(null=False, db_column='fin_validite')
    mise_a_jour_le = models.DateTimeField(auto_now=True, null=False, db_column='mise_a_jour_le') # auto_now met le champ à la date actuelle à chaque appel de model.save()
    source = models.CharField(max_length=50, db_column='source', default='Météo-France')
    lieu_id = models.ForeignKey(
        Lieu_Surveille, on_delete=models.CASCADE, db_column='lieu_id', related_name='vigilances',
    )

    def __str__(self):
        return f"Vigilance n°{self.id_vigilance} niveau {self.niveau_vigilance}"

    class Meta:
        db_table = "VIGILANCE"
        constraints = [
            models.CheckConstraint(condition=Q(niveau_vigilance__gte=0) & Q(niveau_vigilance__lte=3), name="check_niveau_vigilance"),
            models.CheckConstraint(condition=models.Q(fin_validite__gte=F("debut_validite")), name="debut_validite_inferieur_fin"),
        ]

class Regle_Alerte(models.Model):
    TYPES = models.TextChoices("TYPES", 'rapprochement trajectoire vigilance')
    
    id_regle_alerte = models.AutoField(primary_key=True)
    type_alerte = models.CharField(max_length=50, null=False, db_column='type_alerte', default='rapprochement', choices=TYPES)
    niveau_regle_alerte = models.IntegerField(default=1, null=False, validators=[MinValueValidator(1), MaxValueValidator(5)], db_column='niveau')
    seuil_distance = models.FloatField(default=0.0, db_column='seuil_distance')
    seuil_nb_impacts = models.IntegerField(default=0, db_column='seuil_nb_impacts')
    delai_anti_repetition = models.IntegerField(default=30, null=False, db_column='delai_anti_repetition')
    # utilise_vigilance = models.BooleanField(default=False, null=False, db_column='utilise_vigilance')
    actif = models.BooleanField(default=True, null=False, db_column='actif')
    lieu_surveille = models.ForeignKey(
        Lieu_Surveille, on_delete=models.CASCADE, db_column='lieu_surveille_id', related_name='regles_alerte',
    )

    def __str__(self):
        return f"Regle_Alerte n°{self.id_regle_alerte}"

    class Meta:
        db_table = "REGLE_ALERTE"
        constraints = [
            models.CheckConstraint(condition=Q(niveau_regle_alerte__gte=1) & Q(niveau_regle_alerte__lte=5), name="check_niveau_regle_alerte"),
            models.CheckConstraint(condition=Q(type_alerte="rapprochement") | Q(type_alerte="trajectoire") | Q(type_alerte="vigilance"), name="check_type_alerte"),
        ]

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

    def __str__(self):
        return f"Alerte n°{self.id_alerte}"

    class Meta:
        db_table = "ALERTE"
        constraints = [
            models.CheckConstraint(condition=Q(niveau_alerte__gte=1) & Q(niveau_alerte__lte=5), name="check_niveau_alerte"),
        ]           

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

    def __str__(self):
        return f"Notification n°{self.id_notification}"

    class Meta:
        db_table = "NOTIFICATION"
        constraints = [
            models.CheckConstraint(condition=Q(canal="email") | Q(canal="telegram") | Q(canal="web"), name="check_canal_notif"),
            models.CheckConstraint(condition=Q(statut="en_attente") | Q(statut="envoyee") | Q(statut="echec") | Q(statut="bloquee"), name="check_statut_notif"),
        ]