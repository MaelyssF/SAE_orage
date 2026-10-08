CREATE TABLE
    AUTH_USER (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(150) NOT NULL UNIQUE,
        email VARCHAR(254) NOT NULL
    );

CREATE TABLE
    PROFIL_NOTIFICATION (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        notifications_actives BOOLEAN NOT NULL DEFAULT 1,
        canal VARCHAR(20) NOT NULL DEFAULT 'email', -- 'email', 'telegram', 'web'
        sensibilite VARCHAR(20) NOT NULL DEFAULT 'moyenne', -- 'faible', 'moyenne', 'elevee'
        FOREIGN KEY (user_id) REFERENCES AUTH_USER (id) ON DELETE CASCADE
    );

CREATE TABLE
    LIEU_SURVEILLE (
        id_lieu INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_lieu VARCHAR(100) NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        code_departement VARCHAR(5) NOT NULL, -- rattachement vigilance Météo-France
        rayon_proche_km REAL NOT NULL DEFAULT 20.0,
        rayon_large_km REAL NOT NULL DEFAULT 60.0,
        actif BOOLEAN NOT NULL DEFAULT 1
    );

CREATE TABLE
    SCENARIO_SIMULATION (
        id_scenario INTEGER PRIMARY KEY AUTOINCREMENT,
        nom VARCHAR(150),
        type_scenario VARCHAR(50) NOT NULL,
        graine_aleatoire INTEGER NOT NULL DEFAULT 42,
        direction_initiale_deg REAL NOT NULL,
        distance_initiale_km REAL NOT NULL,
        nb_impacts INTEGER NOT NULL,
        etendue_km REAL NOT NULL,
        bruit_parasite REAL NOT NULL DEFAULT 0.0,
        nb_releves INTEGER NOT NULL DEFAULT 6,
        intervalle_min INTEGER NOT NULL DEFAULT 10,
        vitesse_kmh REAL NOT NULL,
        distance_min_reglee_km REAL DEFAULT 0.0
    );

CREATE TABLE
    EPISODE (
        id_episode INTEGER PRIMARY KEY AUTOINCREMENT,
        lieu_id INTEGER NOT NULL,
        debut DATETIME NOT NULL,
        fin DATETIME, -- NULL tant que l'épisode est en cours
        FOREIGN KEY (lieu_id) REFERENCES LIEU_SURVEILLE (id_lieu) ON DELETE CASCADE
    );

CREATE TABLE
    RELEVE (
        id_releve INTEGER PRIMARY KEY AUTOINCREMENT,
        lieu_id INTEGER NOT NULL,
        episode_id INTEGER, -- NULL si aucun épisode actif
        scenario_id INTEGER, -- NULL si relevé réel (non simulé)
        horodatage_donnee DATETIME NOT NULL,
        horodatage_analyse DATETIME NOT NULL,
        statut VARCHAR(30) NOT NULL DEFAULT 'ok', -- 'ok', 'ancien', 'indisponible', 'erreur'
        image_source VARCHAR(255), -- capture ou URL source vérifiable
        indicateur_activite VARCHAR(30) NOT NULL DEFAULT 'Faible', -- 'Nulle', 'Faible', 'Modérée', 'Forte', 'Violente'
        niveau_activite INTEGER DEFAULT 1, -- échelle 1 à 5
        FOREIGN KEY (lieu_id) REFERENCES LIEU_SURVEILLE (id_lieu) ON DELETE CASCADE,
        FOREIGN KEY (episode_id) REFERENCES EPISODE (id_episode) ON DELETE SET NULL,
        FOREIGN KEY (scenario_id) REFERENCES SCENARIO_SIMULATION (id_scenario) ON DELETE SET NULL
    );

CREATE TABLE
    CELLULE (
        id_cellule INTEGER PRIMARY KEY AUTOINCREMENT,
        episode_id INTEGER NOT NULL,
        identifiant_externe VARCHAR(50),
        premiere_detection DATETIME NOT NULL,
        derniere_detection DATETIME NOT NULL,
        statut VARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'dissipee'
        FOREIGN KEY (episode_id) REFERENCES EPISODE (id_episode) ON DELETE CASCADE
    );

CREATE TABLE
    CELLULE_OBSERVATION (
        id_observation INTEGER PRIMARY KEY AUTOINCREMENT,
        cellule_id INTEGER NOT NULL,
        releve_id INTEGER NOT NULL,
        latitude_centre REAL NOT NULL,
        longitude_centre REAL NOT NULL,
        etendue_km REAL NOT NULL,
        nb_impacts INTEGER NOT NULL,
        niveau_activite INTEGER NOT NULL DEFAULT 1, -- échelle de 1 à 5
        direction_deplacement_deg REAL,
        vitesse_kmh REAL,
        distance_min_prevue_km REAL,
        delai_arrivee_min INTEGER, -- NULL si ne touche pas le lieu
        incertitude BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (cellule_id) REFERENCES CELLULE (id_cellule) ON DELETE CASCADE,
        FOREIGN KEY (releve_id) REFERENCES RELEVE (id_releve) ON DELETE CASCADE
    );

CREATE TABLE
    IMPACT (
        id_impact INTEGER PRIMARY KEY AUTOINCREMENT,
        releve_id INTEGER NOT NULL,
        cellule_id INTEGER, -- NULL si impact isolé
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        distance_km REAL NOT NULL, -- distance au lieu surveillé
        direction_cardinale VARCHAR(10) NOT NULL, -- 'NE', 'SW'...
        direction_deg REAL NOT NULL,
        intensite_ka REAL,
        categorie VARCHAR(10) DEFAULT 'CG-', -- 'CG-', 'CG+', 'IC'
        horodatage DATETIME NOT NULL,
        FOREIGN KEY (releve_id) REFERENCES RELEVE (id_releve) ON DELETE CASCADE,
        FOREIGN KEY (cellule_id) REFERENCES CELLULE (id_cellule) ON DELETE SET NULL
    );

CREATE TABLE
    VIGILANCE (
        id_vigilance INTEGER PRIMARY KEY AUTOINCREMENT,
        lieu_id INTEGER NOT NULL,
        niveau VARCHAR(20) NOT NULL, -- 'vert', 'jaune', 'orange', 'rouge'
        type_phenomene VARCHAR(50) NOT NULL DEFAULT 'Orages',
        debut_validite DATETIME NOT NULL,
        fin_validite DATETIME NOT NULL,
        mise_a_jour_source DATETIME NOT NULL,
        source VARCHAR(50) DEFAULT 'Météo-France',
        FOREIGN KEY (lieu_id) REFERENCES LIEU_SURVEILLE (id_lieu) ON DELETE CASCADE
    );

CREATE TABLE
    REGLE_ALERTE (
        id_regle INTEGER PRIMARY KEY AUTOINCREMENT,
        lieu_id INTEGER NOT NULL,
        type_alerte VARCHAR(50) NOT NULL, -- 'rapprochement', 'trajectoire', 'vigilance'
        niveau INTEGER NOT NULL DEFAULT 1, -- niveau de 1 à 5
        seuil_distance_km REAL,
        seuil_nb_impacts INTEGER,
        delai_anti_repetition_min INTEGER NOT NULL DEFAULT 30,
        utilise_vigilance BOOLEAN NOT NULL DEFAULT 0,
        actif BOOLEAN NOT NULL DEFAULT 1,
        FOREIGN KEY (lieu_id) REFERENCES LIEU_SURVEILLE (id_lieu) ON DELETE CASCADE
    );

CREATE TABLE
    ALERTE (
        id_alerte INTEGER PRIMARY KEY AUTOINCREMENT,
        episode_id INTEGER NOT NULL,
        regle_id INTEGER NOT NULL,
        cellule_id INTEGER,
        vigilance_id INTEGER,
        niveau INTEGER NOT NULL, -- de 1 à 5
        motif VARCHAR(255) NOT NULL,
        distance_km REAL,
        vigilance_contributive BOOLEAN NOT NULL DEFAULT 0,
        declenchee_le DATETIME NOT NULL,
        FOREIGN KEY (episode_id) REFERENCES EPISODE (id_episode) ON DELETE CASCADE,
        FOREIGN KEY (regle_id) REFERENCES REGLE_ALERTE (id_regle) ON DELETE CASCADE,
        FOREIGN KEY (cellule_id) REFERENCES CELLULE (id_cellule) ON DELETE SET NULL,
        FOREIGN KEY (vigilance_id) REFERENCES VIGILANCE (id_vigilance) ON DELETE SET NULL
    );

CREATE TABLE
    NOTIFICATION (
        id_notification INTEGER PRIMARY KEY AUTOINCREMENT,
        alerte_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        canal VARCHAR(20) NOT NULL DEFAULT 'email', -- 'email', 'telegram', etc.
        statut VARCHAR(20) NOT NULL DEFAULT 'en_attente', -- 'envoyee', 'echec', 'bloquee'
        envoyee_le DATETIME,
        FOREIGN KEY (alerte_id) REFERENCES ALERTE (id_alerte) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES AUTH_USER (id) ON DELETE CASCADE
    );