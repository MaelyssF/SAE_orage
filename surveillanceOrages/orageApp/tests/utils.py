from orageApp.models import *
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone

class Mold:
    def __init__(self):
        pass
        
    def create_user(self):
        if not hasattr(self, "user"):
            self.user = User.objects.create_user(username="test", password="mdp_test") # https://stackoverflow.com/questions/63054997/difference-between-user-objects-create-user-vs-user-objects-create-vs-user
        return self.user

    def create_profil_notif(self):
        if not hasattr(self, "profil_notif"):
            self.create_user()
            self.profil_notif = Profil_Notification.objects.create(user_id=self.user)
        return self.profil_notif

    def create_lieu(self):
        if not hasattr(self, "lieu"):
            self.lieu = Lieu_Surveille.objects.create(nom_lieu="Maison", 
                                                      latitude=47.843058, 
                                                      longitude=1.926602, 
                                                      code_departement=45067)
        return self.lieu  

    def create_episode(self):
        if not hasattr(self, "episode"):
            self.create_lieu()
            self.episode = Episode.objects.create(lieu_id=self.lieu, 
                                                  debut=datetime(2026, 10, 20, 6, 32, 29, tzinfo=timezone.utc), 
                                                  fin=datetime(2026, 10, 20, 12, 7, 16, tzinfo=timezone.utc))
        return self.episode 

    def create_scenario_s(self):
        if not hasattr(self, "scenario_s"):
            self.scenario_s = Scenario_Simulation.objects.create(nom_scenario="Scenario1", 
                                                                 type_scenario="catastrophe", 
                                                                 direction_initiale_deg=46.1, 
                                                                 distance_initiale_km=13, 
                                                                 nb_impacts=2, 
                                                                 etendue_km=5.8, 
                                                                 vitesse_kmh=74.2)
        return self.scenario_s

    def create_releve(self):
        if not hasattr(self, "releve"):
            self.create_episode()
            self.create_scenario_s()
            self.releve = Releve.objects.create(lieu_id=self.lieu, 
                                                episode_id=self.episode, 
                                                scenario_id=self.scenario_s,
                                                horodatage_donnee=datetime(2026, 10, 20, 8, 30, 45, tzinfo=timezone.utc),
                                                horodatage_analyse=datetime(2026, 10, 20, 8, 32, 29, tzinfo=timezone.utc),
                                                image_source="https://domain.com/image.png")
        return self.releve

    def create_cellule(self):
        if not hasattr(self, "cellule"):
            self.create_episode()
            self.cellule = Cellule.objects.create(episode_id=self.episode,
                                                  identifiant_externe="identifiant_1",
                                                  premiere_detection=datetime(2026, 10, 20, 15, 7, 4, tzinfo=timezone.utc),
                                                  derniere_detection=datetime(2026, 10, 20, 17, 55, 28, tzinfo=timezone.utc),)
        return self.cellule

    def create_impact(self):
        if not hasattr(self, "impact"):
            self.create_releve()
            self.create_cellule()
            self.impact = Impact.objects.create(latitude=47.873134,
                                            longitude=1.966902,
                                            distance_km=12.3,
                                            direction_cardinale="NNO",
                                            direction_deg=17.6,
                                            intensite_ka=33.5,
                                            horodatage=datetime(2026, 10, 20, 16, 26, 57, tzinfo=timezone.utc),
                                            releve_id=self.releve,
                                            cellule_id=self.cellule)
        return self.impact

    def create_vigilance(self):
        if not hasattr(self, "vigilance"):
            self.create_lieu()
            self.vigilance = Vigilance.objects.create(fin_validite=datetime.now(tz=timezone.utc) + timedelta(hours=2),
                                                    lieu_id=self.lieu)
        return self.vigilance

    def create_regle(self):
        if not hasattr(self, "regle"):
            self.create_lieu()
            self.regle = Regle_Alerte.objects.create(lieu_surveille=self.lieu)
        return self.regle

    def create_cellule_observation(self):
        if not hasattr(self, "cellule_observation"):
            self.create_cellule()
            self.create_releve()
            self.cellule_observation = Cellule_Observation.objects.create(latitude_centre=47.846058,
                                                                          longitude_centre=1.926902,
                                                                          etendue_km=5.2,
                                                                          nb_impacts=5,
                                                                          direction_deplacement_deg=26.1,
                                                                          vitesse_kmh=45.3,
                                                                          distance_min_prevue_km=2.0,
                                                                          delai_arrivee_min=32,
                                                                          cellule_id=self.cellule,
                                                                          releve_id=self.releve)
        return self.cellule_observation

    def create_alerte(self):
        if not hasattr(self, "alerte"):
            self.create_regle()
            self.create_cellule()
            self.create_vigilance()
            self.alerte = Alerte.objects.create(motif="rapprochement orage",
                                            episode=self.episode,
                                            regle_alerte=self.regle,
                                            cellule=self.cellule,
                                            vigilance=self.vigilance)
        return self.alerte

    def create_notif(self):
        if not hasattr(self, "notif"):
            self.create_user()
            self.create_alerte()
            self.notif = Notification.objects.create(alerte=self.alerte,
                                                    user=self.user)
        return self.notif
