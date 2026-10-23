const mapElement = document.getElementById('map');
const selectSimulations = document.getElementById('select-simulations');
const messageSimulation = document.getElementById('message-simulation');

// Boutons et contrôles
const btnGenererCellule = document.getElementById('btn-generer-cellule');
const btnEnregistrer = document.getElementById('btn-enregistrer');
const btnGenererScenario = document.getElementById('btn-generer-scenario');
const sliderScenario = document.getElementById('slider-scenario');
const btnPlayPause = document.getElementById('btn-play-pause');
const infoScenario = document.getElementById('info-scenario');
const btnGenerer = document.getElementById('btn-generer');
const btnGenerer10 = document.getElementById('btn-generer-10');
const btnEffacer = document.getElementById('btn-effacer');
const btnCharger = document.getElementById('btn-charger');

// Variables d'état global
let map = null;
let impactsActuels = [];        // Impacts affichés actuellement sur la carte
let derniereCellule = null;     // Données de la cellule statique en cours
let simulationTerminee = false; // Vrai quand tous les impacts de la cellule sont apparus
let minuteurs = [];             // Stocke les setTimeout des impacts en attente
let numeroGeneration = 0;       // Identifiant de génération pour ignorer les requêtes périmées
let scenarioActuel = null;      // Données du scénario mobile en cours
let timerAnimation = null;      // Minuteur pour le défilement automatique du scénario

const couleursImpactsParAge = [
    "#f705fa", // 0 min : rose
    "#ff0000", // 15 min : rouge
    "#ff8000", // 30 min : orange
    "#ffff00", // 45 min : jaune
    "#00ff00", // 60 min : vert
    "#00ffff", // 75 min : cyan
    "#0080ff", // 90 min : bleu
    "#0000ff"  // 105 min : bleu marine
];
const dureeVieImpactSecondes = 2 * 60 * 60;
const intervalleCouleurSecondes = 15 * 60;

// =============================================================================
// FONCTIONS UTILITAIRES
// =============================================================================

function afficherMessage(texte) {
    if (messageSimulation) {
        messageSimulation.textContent = texte;
    }
}

// Annule les impacts d'une cellule qui n'ont pas encore eu le temps d'apparaître
function annulerAnimation() {
    minuteurs.forEach(clearTimeout);
    minuteurs = [];
}

// Arrête l'animation du scénario mobile
function arreterLecture() {
    if (timerAnimation) {
        clearInterval(timerAnimation);
        timerAnimation = null;
    }
    if (btnPlayPause) {
        btnPlayPause.innerHTML = '<i class="bi bi-play-fill"></i> Lecture';
    }
}

// Lance la lecture automatique du scénario mobile
function lancerLecture() {
    arreterLecture();
    if (!scenarioActuel) return;

    if (btnPlayPause) {
        btnPlayPause.innerHTML = '<i class="bi bi-pause-fill"></i> Pause';
    }

    timerAnimation = setInterval(() => {
        if (!sliderScenario) return;
        let currentIndex = parseInt(sliderScenario.value);
        if (currentIndex < scenarioActuel.frames.length - 1) {
            afficherFrame(currentIndex + 1);
        } else {
            arreterLecture(); // Fin du scénario atteinte
        }
    }, 450); // 450 ms par étape
}

// Réinitialise la carte et arrête toutes les animations en cours
function effacerImpacts() {
    numeroGeneration++; // Ignore les réponses serveur en transit
    annulerAnimation();
    arreterLecture();

    if (map) {
        map.eachLayer(function (layer) {
            if (layer instanceof L.CircleMarker || layer instanceof L.Circle) {
                map.removeLayer(layer);
            }
        });
    }

    impactsActuels = [];
    derniereCellule = null;
    simulationTerminee = false;
    scenarioActuel = null;

    if (btnEnregistrer) btnEnregistrer.disabled = true;
    if (btnGenererCellule) btnGenererCellule.disabled = false;
    if (sliderScenario) {
        sliderScenario.disabled = true;
        sliderScenario.value = 0;
    }
    if (infoScenario) {
        infoScenario.textContent = "En attente du lancement d'un orage...";
    }
    afficherMessage('');
}

// Dessine un impact individuel sur la carte
function afficherImpact(impact) {
    if (!map) return;
    const tempsOffset = (typeof impact.t_s === 'number') ? impact.t_s : 0;
    
    L.circleMarker([impact.latitude, impact.longitude], {
        radius: 3,
        color: "#ff3333",
        fillColor: "#ff0000",
        fillOpacity: 0.95,
        weight: 1
    }).addTo(map).bindPopup(
        `<b>Impact de foudre</b><br>Lat: ${impact.latitude}<br>Lon: ${impact.longitude}<br>Tombé à T + ${tempsOffset} s`
    );
}

function obtenirTempsFrame(frame, index) {
    if (Number.isFinite(frame.temps_secondes)) {
        return frame.temps_secondes;
    }

    const intervalle = scenarioActuel.parametres?.interval_seconds;
    return index * (Number.isFinite(intervalle) ? intervalle : 0);
}

function obtenirCouleurImpact(ageSecondes) {
    if (ageSecondes < 0 || ageSecondes >= dureeVieImpactSecondes) {
        return null;
    }

    const indexCouleur = Math.floor(ageSecondes / intervalleCouleurSecondes);
    return couleursImpactsParAge[indexCouleur];
}

// Affiche progressivement les impacts d'une cellule statique
function jouerCellule(cellule) {
    if (!map) return;
    const total = cellule.impacts.length;
    let apparus = 0;

    // Recentrage automatique vers le centre de la cellule
    if (cellule.centre && typeof cellule.centre.latitude === 'number' && typeof cellule.centre.longitude === 'number') {
        map.setView([cellule.centre.latitude, cellule.centre.longitude], 8);
    }

    afficherMessage(`Cellule en cours : 0 / ${total} impacts…`);

    cellule.impacts.forEach(function (impact, index) {
        const delaiS = (typeof impact.t_s === 'number') ? impact.t_s : index;

        const timer = setTimeout(function () {
            afficherImpact(impact);
            impactsActuels.push({ latitude: impact.latitude, longitude: impact.longitude });
            apparus++;

            if (apparus < total) {
                afficherMessage(`Cellule en cours : ${apparus} / ${total} impacts…`);
            } else {
                simulationTerminee = true;
                if (btnEnregistrer) btnEnregistrer.disabled = false;
                if (btnGenererCellule) btnGenererCellule.disabled = false;
                afficherMessage(`Simulation terminée : ${total} impacts générés.`);
            }
        }, delaiS * 1000);

        minuteurs.push(timer);
    });
}

// Affiche une étape (frame) d'un scénario mobile
function afficherFrame(index) {
    if (!map || !scenarioActuel || !scenarioActuel.frames[index]) return;

    // Efface les impacts de la frame précédente
    map.eachLayer(function (layer) {
        if (layer instanceof L.CircleMarker || layer instanceof L.Circle) {
            map.removeLayer(layer);
        }
    });

    const frame = scenarioActuel.frames[index];
    const traj = scenarioActuel.trajectoire || {};

    // Affiche les impacts récents et leurs traces en fonction de leur ancienneté
    const tempsCourant = obtenirTempsFrame(frame, index);
    scenarioActuel.frames.slice(0, index + 1).forEach((frameImpact, indexFrameImpact) => {
        const ageFrame = tempsCourant - obtenirTempsFrame(frameImpact, indexFrameImpact);
        const couleur = obtenirCouleurImpact(ageFrame);
        if (!couleur) return;

        frameImpact.impacts.forEach(imp => {
            L.circleMarker([imp.latitude, imp.longitude], {
                radius: 3,
                color: couleur,
                fillColor: couleur,
                fillOpacity: 0.95,
                weight: 1
            }).addTo(map);
        });
    });

    // Trace le cercle matérialisant la cellule orageuse
    if (frame.centre_theorique) {
        L.circle([frame.centre_theorique.latitude, frame.centre_theorique.longitude], {
            radius: 30000, // 4 km
            color: "#388bfd",
            fillOpacity: 0.08,
            weight: 1,
            dashArray: "4, 4"
        }).addTo(map);
    }

    // Mise à jour du slider et du texte
    if (sliderScenario) sliderScenario.value = index;

    if (infoScenario) {
        const minutes = Math.floor(frame.temps_secondes / 60);
        const dist = frame.distance_parcourue_km !== undefined ? `${frame.distance_parcourue_km} km` : '';
        const cap = traj.direction_cardinale ? `${traj.direction_cardinale} (${traj.direction_deg}°)` : '';
        infoScenario.innerHTML = `Étape : <b>${index + 1}/${scenarioActuel.frames.length}</b> (+${minutes} min)<br>Distance : ${dist} | Cap : ${cap}`;
    }
}

// Charge la liste des simulations disponibles pour le menu déroulant
function chargerListeSimulations() {
    if (!selectSimulations) return;

    fetch('/orageApp/api/lister-simulations/')
        .then(response => response.json())
        .then(data => {
            selectSimulations.innerHTML = '';
            if (!data.simulations || data.simulations.length === 0) {
                selectSimulations.innerHTML = '<option value="" disabled selected>Aucune simulation</option>';
                return;
            }
            data.simulations.forEach(sim => {
                const opt = document.createElement('option');
                opt.value = sim.fichier;
                opt.textContent = `${sim.date_heure} (${sim.nb_impacts} impacts)`;
                selectSimulations.appendChild(opt);
            });
        })
        .catch(err => console.error("Erreur chargement liste simulations :", err));
}

// =============================================================================
// INITIALISATION ET ÉVÉNEMENTS
// =============================================================================

if (mapElement) {
    // Initialisation de la carte Leaflet
    map = L.map('map').setView([46.60, 2.20], 6);

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16,
        attribution: 'Tiles &copy; Esri'
    }).addTo(map);

    // Clic sur la carte : afficher les coordonnées
    map.on('click', function (e) {
        const latitude = e.latlng.lat.toFixed(4);
        const longitude = e.latlng.lng.toFixed(4);
        L.popup()
            .setLatLng(e.latlng)
            .setContent(`<b>Position sélectionnée</b><br>Lat: ${latitude}<br>Lon: ${longitude}`)
            .openOn(map);
    });

    // Charger les simulations enregistrées dans la liste déroulante
    chargerListeSimulations();

    // -------------------------------------------------------------------------
    // Génération de cellule statique
    // -------------------------------------------------------------------------
    if (btnGenererCellule) {
        btnGenererCellule.addEventListener('click', function () {
            effacerImpacts();
            btnGenererCellule.disabled = true;
            const numero = ++numeroGeneration;
            afficherMessage('Génération de la cellule par le serveur…');

            const url = btnGenererCellule.dataset.apiUrl || '/orageApp/api/generer-cellule/';

            fetch(url)
                .then(res => {
                    if (!res.ok) throw new Error(`Erreur HTTP ${res.status}`);
                    return res.json();
                })
                .then(data => {
                    if (numero !== numeroGeneration) return;

                    if (data.impacts && Array.isArray(data.impacts) && data.impacts.length > 0) {
                        derniereCellule = data;
                        jouerCellule(data);
                    } else {
                        btnGenererCellule.disabled = false;
                        afficherMessage('Aucun impact reçu.');
                    }
                })
                .catch(err => {
                    if (numero !== numeroGeneration) return;
                    btnGenererCellule.disabled = false;
                    afficherMessage(`Échec de la génération : ${err.message}`);
                    console.error('Erreur API :', err);
                });
        });
    }

    // -------------------------------------------------------------------------
    // Enregistrement de la simulation
    // -------------------------------------------------------------------------
    if (btnEnregistrer) {
        btnEnregistrer.addEventListener('click', function () {
            let payload = null;

            if (scenarioActuel) {
                payload = {
                    type: "scenario_mobile",
                    point_depart: scenarioActuel.point_depart,
                    trajectoire: scenarioActuel.trajectoire,
                    parametres: scenarioActuel.parametres,
                    frames: scenarioActuel.frames
                };
            } else if (derniereCellule && simulationTerminee) {
                payload = {
                    type: "cellule_statique",
                    debut: derniereCellule.debut,
                    centre: derniereCellule.centre,
                    rayon_km: derniereCellule.rayon_km,
                    intervalle_s: derniereCellule.intervalle_s,
                    impacts: derniereCellule.impacts
                };
            } else if (impactsActuels.length > 0) {
                payload = {
                    type: "impacts_libres",
                    impacts: impactsActuels
                };
            }

            if (!payload) {
                afficherMessage("Aucune simulation active à enregistrer !");
                return;
            }

            const jetonEl = document.querySelector('[name=csrfmiddlewaretoken]');
            const jeton = jetonEl ? jetonEl.value : '';
            btnEnregistrer.disabled = true;

            const url = btnEnregistrer.dataset.apiUrl || '/orageApp/api/enregistrer-simulation/';

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': jeton
                },
                body: JSON.stringify(payload)
            })
                .then(res => res.json().then(donnees => ({ ok: res.ok, donnees })))
                .then(({ ok, donnees }) => {
                    btnEnregistrer.disabled = false;
                    if (ok) {
                        afficherMessage(`Simulation enregistrée : ${donnees.fichier}`);
                        chargerListeSimulations();
                    } else {
                        afficherMessage(`Échec : ${donnees.erreur || 'erreur serveur'}`);
                    }
                })
                .catch(err => {
                    btnEnregistrer.disabled = false;
                    afficherMessage("Échec de l'enregistrement : serveur injoignable.");
                    console.error("Erreur enregistrement :", err);
                });
        });
    }

    // -------------------------------------------------------------------------
    // Scénario orage mobile
    // -------------------------------------------------------------------------
    if (btnGenererScenario) {
        btnGenererScenario.addEventListener('click', function () {
            effacerImpacts();
            afficherMessage("Calcul du scénario d'orage mobile…");

            fetch('/orageApp/api/generer-scenario/')
                .then(response => response.json())
                .then(data => {
                    scenarioActuel = data;

                    if (sliderScenario) {
                        sliderScenario.disabled = false;
                        sliderScenario.max = data.frames.length - 1;
                        sliderScenario.value = 0;
                    }

                    if (btnEnregistrer) btnEnregistrer.disabled = false;

                    afficherMessage(`Scénario mobile prêt : ${data.frames.length} étapes.`);
                    afficherFrame(0);
                    lancerLecture();
                })
                .catch(err => {
                    afficherMessage("Erreur lors de la génération du scénario.");
                    console.error("Erreur scénario :", err);
                });
        });
    }

    if (sliderScenario) {
        sliderScenario.addEventListener('input', function () {
            arreterLecture();
            afficherFrame(parseInt(this.value));
        });
    }

    if (btnPlayPause) {
        btnPlayPause.addEventListener('click', function () {
            if (timerAnimation) {
                arreterLecture();
            } else {
                lancerLecture();
            }
        });
    }

    // -------------------------------------------------------------------------
    // Génération ponctuelle d'impacts
    // -------------------------------------------------------------------------
    if (btnGenerer) {
        btnGenerer.addEventListener('click', function () {
            fetch('/orageApp/api/generer-impact/')
                .then(response => response.json())
                .then(data => {
                    afficherImpact(data);
                    impactsActuels.push({ latitude: data.latitude, longitude: data.longitude });
                    if (btnEnregistrer) btnEnregistrer.disabled = false;
                })
                .catch(error => console.error('Erreur génération 1 impact :', error));
        });
    }

    if (btnGenerer10) {
        btnGenerer10.addEventListener('click', function () {
            fetch('/orageApp/api/generer-10-impacts/')
                .then(response => response.json())
                .then(data => {
                    if (data.impacts && Array.isArray(data.impacts)) {
                        data.impacts.forEach(impact => {
                            afficherImpact(impact);
                            impactsActuels.push({ latitude: impact.latitude, longitude: impact.longitude });
                        });
                        if (btnEnregistrer) btnEnregistrer.disabled = false;
                    }
                })
                .catch(error => console.error('Erreur génération 10 impacts :', error));
        });
    }

    // -------------------------------------------------------------------------
    // Nettoyage de la carte
    // -------------------------------------------------------------------------
    if (btnEffacer) {
        btnEffacer.addEventListener('click', function () {
            effacerImpacts();
        });
    }

    // -------------------------------------------------------------------------
    // Rejeu d'une simulation enregistrée
    // -------------------------------------------------------------------------
    if (btnCharger) {
        btnCharger.addEventListener('click', function () {
            const fichierChoisi = selectSimulations ? selectSimulations.value : null;
            if (!fichierChoisi) {
                alert("Veuillez choisir une simulation dans la liste.");
                return;
            }

            fetch('/orageApp/api/charger-simulation/' + fichierChoisi + '/')
                .then(response => response.json())
                .then(data => {
                    effacerImpacts();

                    if (data.frames && Array.isArray(data.frames) && data.frames.length > 0) {
                        // Rejeu d'un scénario mobile avec étapes
                        scenarioActuel = data;
                        if (sliderScenario) {
                            sliderScenario.disabled = false;
                            sliderScenario.max = data.frames.length - 1;
                            sliderScenario.value = 0;
                        }
                        afficherFrame(0);
                        if (btnEnregistrer) btnEnregistrer.disabled = false;
                        afficherMessage(`Scénario mobile rejoué : ${data.frames.length} étapes (${data.nb_impacts || 0} impacts).`);
                    } else {
                        // Rejeu d'une cellule statique ou d'impacts libres
                        impactsActuels = data.impacts || [];
                        impactsActuels.forEach(imp => {
                            afficherImpact(imp);
                        });

                        if (data.parametres && data.parametres.centre) {
                            map.setView([data.parametres.centre.latitude, data.parametres.centre.longitude], 8);
                        }

                        if (btnEnregistrer) btnEnregistrer.disabled = false;
                        afficherMessage(`Simulation restaurée : ${impactsActuels.length} impacts.`);
                    }
                })
                .catch(err => console.error("Erreur chargement simulation :", err));
        });
    }
}
