const mapElement = document.getElementById('map');
const selectSimulations = document.getElementById('select-simulations');


/** 
 * Charge la liste des simulations disponibles depuis l'API et les affiche dans le menu déroulant
*/
function chargerListeSimulations() {
    if (!selectSimulations) return;

    fetch('/orageApp/api/lister-simulations/')
        .then(response => response.json())
        .then(data => {
            selectSimulations.innerHTML = '';
            if (data.simulations.length === 0) {
                selectSimulations.innerHTML = '<option value="" disabled selected>Aucune simulation</option>';
                return;
            }
            data.simulations.forEach(sim => {
                const opt = document.createElement('option');
                opt.value = sim.fichier;
                opt.textContent = `${sim.date_heure} (${sim.nb_impacts} impacts)`;
                selectSimulations.appendChild(opt);
            });
        });
}
chargerListeSimulations(); // On charge la liste des simulations dès le chargement de la page


if (mapElement) {
    let scenarioActuel = null;
    let timerAnimation = null;

    // Initialisation de la carte Leaflet (centrée par défaut sur la France)
    const map = L.map('map').setView([46.60, 2.20], 6);
    let impactsActuels = [];

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16,
        attribution: 'Tiles &copy; Esri'
    }).addTo(map);

    // Affichage des coordonnées au clic sur la carte
    map.on('click', function (e) {
        const latitude = e.latlng.lat.toFixed(4);
        const longitude = e.latlng.lng.toFixed(4);
        L.popup()
            .setLatLng(e.latlng)
            .setContent(`<b>Position sélectionnée</b><br>Lat: ${latitude}<br>Lon: ${longitude}`)
            .openOn(map);
    });

    /** 
     * Réinitialise la carte en supprimant tous les points affichés
     */
    function resetMap() {
        if (impactsActuels.length === 0) {
            alert("Aucun impact sur la carte à effacer !");
            return;
        }

        // Variables d'état de la simulation
        let derniereCellule = null;     // Cellule actuellement affichée (à enregistrer)
        let simulationTerminee = false; // Vrai quand tous les impacts sont apparus
        let minuteurs = [];             // Stocke les setTimeout des impacts en attente
        let numeroGeneration = 0;       // Identifie la génération en cours pour ignorer les réponses périmées

        // Éléments du DOM
        const btnGenererCellule = document.getElementById('btn-generer-cellule');
        const btnEnregistrer = document.getElementById('btn-enregistrer');
        const btnEffacer = document.getElementById('btn-effacer');
        const messageSimulation = document.getElementById('message-simulation');

        function afficherMessage(texte) {
            if (messageSimulation) messageSimulation.textContent = texte;
        }

        // Annule les impacts qui n'ont pas encore eu le temps d'apparaître
        function annulerAnimation() {
            minuteurs.forEach(clearTimeout);
            minuteurs = [];
        }

        // Retire les impacts de la carte, arrête l'animation et réinitialise l'état
        function effacerImpacts() {
            numeroGeneration++; // Une réponse du serveur encore en route sera ignorée
            annulerAnimation();
            map.eachLayer(function (layer) {
                if (layer instanceof L.CircleMarker) {
                    map.removeLayer(layer);
                }
            });
            impactsActuels = [];
        }

        /**
         * Affiche la frame du scénario de simulation d'orage à l'index donné
         */
        function afficherFrame(index) {
            if (!scenarioActuel || !scenarioActuel.frames[index]) return;

            // On efface les points de la frame précédente
            map.eachLayer(function (layer) {
                if (layer instanceof L.CircleMarker || layer instanceof L.Circle) {
                    map.removeLayer(layer);
                }
            });

            const frame = scenarioActuel.frames[index];
            const traj = scenarioActuel.trajectoire;

            // On trace les 20 impacts de cette étape
            frame.impacts.forEach(imp => {
                L.circleMarker([imp.latitude, imp.longitude], {
                    radius: 3,
                    color: "#ff3333",
                    fillColor: "#ff0000",
                    fillOpacity: 0.95,
                    weight: 1
                }).addTo(map);
            });

            // Le cercle matérialisant la cellule orageuse
            L.circle([frame.centre_theorique.latitude, frame.centre_theorique.longitude], {
                radius: 4000, // 4 km
                color: "#388bfd",
                fillOpacity: 0.08,
                weight: 1,
                dashArray: "4, 4"
            }).addTo(map);

            // Mise à jour de la barre et des infos
            const slider = document.getElementById('slider-scenario');
            const infoText = document.getElementById('info-scenario');
            if (slider) slider.value = index;

            if (infoText) {
                const minutes = Math.floor(frame.temps_secondes / 60);
                infoText.innerHTML = `Étape : <b>${index + 1}/30</b> (+${minutes} min)<br>Distance : ${frame.distance_parcourue_km} km | Cap : ${traj.direction_cardinale} (${traj.direction_deg}°)`;
            }
            derniereCellule = null;
            simulationTerminee = false;
            if (btnEnregistrer) btnEnregistrer.disabled = true;
            if (btnGenererCellule) btnGenererCellule.disabled = false;
            afficherMessage('');
        }

        // Dessine un impact individuel sur la carte
        function afficherImpact(impact) {
            const tempsOffset = (typeof impact.t_s === 'number') ? impact.t_s : 0;
            L.circleMarker([impact.latitude, impact.longitude], {
                radius: 3,
                color: "#ff3333",
                fillColor: "#ff0000",
                fillOpacity: 0.95,
                weight: 1
            }).addTo(map).bindPopup(`<b>Impact de foudre</b><br>Lat: ${impact.latitude}<br>Lon: ${impact.longitude}<br>Tombé à T + ${tempsOffset} s`);
        }

        // Fait apparaître les impacts de la cellule un par un
        function jouerCellule(cellule) {
            const total = cellule.impacts.length;
            let apparus = 0;

            // Recentrage automatique de la carte vers le centre de la cellule
            if (cellule.centre && typeof cellule.centre.latitude === 'number' && typeof cellule.centre.longitude === 'number') {
                map.setView([cellule.centre.latitude, cellule.centre.longitude], 8);
            }

            afficherMessage(`Cellule en cours : 0 / ${total} impacts…`);

            cellule.impacts.forEach(function (impact, index) {
                // Utilise l'instant t_s fourni par le serveur (ou 1 seconde d'écart par défaut)
                const delaiS = (typeof impact.t_s === 'number') ? impact.t_s : index;

                const timer = setTimeout(function () {
                    afficherImpact(impact);
                    apparus++;

                    if (apparus < total) {
                        afficherMessage(`Cellule en cours : ${apparus} / ${total} impacts…`);
                    } else {
                        simulationTerminee = true;
                        if (btnEnregistrer) btnEnregistrer.disabled = false;
                        afficherMessage(`Simulation terminée : ${total} impacts générés (non enregistrée).`);
                    }
                }, delaiS * 1000);

                minuteurs.push(timer);
            });
        }

        // Bouton Générer une cellule
        if (btnGenererCellule) {
            btnGenererCellule.addEventListener('click', function () {
                btnGenererCellule.disabled = true;
                const numero = ++numeroGeneration;
                afficherMessage('Génération de la cellule par le serveur…');

                fetch(btnGenererCellule.dataset.apiUrl)
                    .then(res => {
                        if (!res.ok) throw new Error(`Erreur HTTP ${res.status}`);
                        return res.json();
                    })
                    .then(data => {
                        if (numero !== numeroGeneration) return; // Action annulée via "Effacer"

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

        // Bouton générer 1 impact
        const btnGenerer = document.getElementById('btn-generer');
        if (btnGenerer) {
            btnGenerer.addEventListener('click', function () {
                fetch('/orageApp/api/generer-impact/')
                    .then(response => response.json())
                    .then(data => {
                        L.circleMarker([data.latitude, data.longitude], {
                            radius: 3,
                            color: "#ff3333",
                            fillColor: "#ff0000",
                            fillOpacity: 0.95,
                            weight: 1
                        }).addTo(map).bindPopup(`<b>Impact de foudre</b><br>Lat: ${data.latitude}<br>Lon: ${data.longitude}`).openPopup();
                        impactsActuels.push({ latitude: data.latitude, longitude: data.longitude });
                    })
                    .catch(error => {
                        console.error('Erreur lors de la génération :', error);
                    });
            });
        }

        // Bouton générer 10 impacts
        const btnGenerer10 = document.getElementById('btn-generer-10');
        if (btnGenerer10) {
            btnGenerer10.addEventListener('click', function () {
                fetch('/orageApp/api/generer-10-impacts/')
                    .then(response => response.json())
                    .then(data => {
                        if (data.impacts && Array.isArray(data.impacts)) {
                            for (const impact of data.impacts) {
                                impactsActuels.push({ latitude: impact.latitude, longitude: impact.longitude });
                                L.circleMarker([impact.latitude, impact.longitude], {
                                    radius: 3,
                                    color: "#ff3333",
                                    fillColor: "#ff0000",
                                    fillOpacity: 0.95,
                                    weight: 1
                                }).addTo(map).bindPopup(`<b>Impact de foudre</b><br>Lat: ${impact.latitude}<br>Lon: ${impact.longitude}`);
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Erreur lors de la génération :', error);

                    });
            });
        }

        function afficherMessage(texte) {
            if (messageSimulation) messageSimulation.textContent = texte;
        }

        // Annule les impacts qui n'ont pas encore eu le temps d'apparaître
        function annulerAnimation() {
            minuteurs.forEach(clearTimeout);
            minuteurs = [];
        }

        // Retire les impacts de la carte, arrête l'animation et réinitialise l'état
        function effacerImpacts() {
            numeroGeneration++; // Une réponse du serveur encore en route sera ignorée
            annulerAnimation();
            map.eachLayer(function (layer) {
                if (layer instanceof L.CircleMarker) {
                    map.removeLayer(layer);
                }
            });
            derniereCellule = null;
            simulationTerminee = false;
            if (btnEnregistrer) btnEnregistrer.disabled = true;
            if (btnGenererCellule) btnGenererCellule.disabled = false;
            afficherMessage('');
        }

        // Dessine un impact individuel sur la carte
        function afficherImpact(impact) {
            const tempsOffset = (typeof impact.t_s === 'number') ? impact.t_s : 0;
            L.circleMarker([impact.latitude, impact.longitude], {
                radius: 3,
                color: "#ff3333",
                fillColor: "#ff0000",
                fillOpacity: 0.95,
                weight: 1
            }).addTo(map).bindPopup(`<b>Impact de foudre</b><br>Lat: ${impact.latitude}<br>Lon: ${impact.longitude}<br>Tombé à T + ${tempsOffset} s`);
        }

        // Fait apparaître les impacts de la cellule un par un
        function jouerCellule(cellule) {
            const total = cellule.impacts.length;
            let apparus = 0;

            // Recentrage automatique de la carte vers le centre de la cellule
            if (cellule.centre && typeof cellule.centre.latitude === 'number' && typeof cellule.centre.longitude === 'number') {
                map.setView([cellule.centre.latitude, cellule.centre.longitude], 8);
            }

            afficherMessage(`Cellule en cours : 0 / ${total} impacts…`);

            cellule.impacts.forEach(function (impact, index) {
                // Utilise l'instant t_s fourni par le serveur (ou 1 seconde d'écart par défaut)
                const delaiS = (typeof impact.t_s === 'number') ? impact.t_s : index;

                const timer = setTimeout(function () {
                    afficherImpact(impact);
                    apparus++;

                    if (apparus < total) {
                        afficherMessage(`Cellule en cours : ${apparus} / ${total} impacts…`);
                    } else {
                        simulationTerminee = true;
                        if (btnEnregistrer) btnEnregistrer.disabled = false;
                        afficherMessage(`Simulation terminée : ${total} impacts générés (non enregistrée).`);
                    }
                }, delaiS * 1000);

                minuteurs.push(timer);
            });
        }

        // Bouton Générer une cellule
        if (btnGenererCellule) {
            btnGenererCellule.addEventListener('click', function () {
                btnGenererCellule.disabled = true;
                const numero = ++numeroGeneration;
                afficherMessage('Génération de la cellule par le serveur…');

                fetch(btnGenererCellule.dataset.apiUrl)
                    .then(res => {
                        if (!res.ok) throw new Error(`Erreur HTTP ${res.status}`);
                        return res.json();
                    })
                    .then(data => {
                        if (numero !== numeroGeneration) return; // Action annulée via "Effacer"

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

        // Bouton effacer les impacts
        if (btnEffacer) {
            btnEffacer.addEventListener('click', function () {
                resetMap();
            });
        }

        // Bouton sauvegarder la simulation
        const btnSauvegarder = document.getElementById('btn-sauvegarder');
        if (btnSauvegarder) {
            btnSauvegarder.addEventListener('click', function () {
                if (impactsActuels.length === 0) {
                    alert("Aucun impact sur la carte à enregistrer !");
                    return;
                }

                fetch('/orageApp/api/sauvegarder-simulation/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ impacts: impactsActuels })
                })
                    .then(response => response.json())
                    .then(data => {
                        alert(`Simulation enregistrée avec succès !\nFichier : ${data.fichier}\nTotal : ${data.nb_impacts} impacts`);
                        chargerListeSimulations(); // Rafraîchit le menu déroulant
                    })
                    .catch(err => console.error("Erreur sauvegarde :", err));
            });
        }

        // Bouton charger (rejouer) une simulation
        const btnCharger = document.getElementById('btn-charger');
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
                        map.eachLayer(layer => {
                            if (layer instanceof L.CircleMarker) map.removeLayer(layer);
                        });

                        impactsActuels = data.impacts || [];

                        impactsActuels.forEach(imp => {
                            L.circleMarker([imp.latitude, imp.longitude], {
                                radius: 3,
                                color: "#ff3333",
                                fillColor: "#ff0000",
                                fillOpacity: 0.95,
                                weight: 1
                            }).addTo(map).bindPopup(`Impact restauré<br>Lat: ${imp.latitude}<br>Lon: ${imp.longitude}`);
                        });
                    })
                    .catch(err => console.error("Erreur chargement :", err));
            });
        }

        // Bouton Enregistrer
        if (btnEnregistrer) {
            btnEnregistrer.addEventListener('click', function () {
                if (!derniereCellule || !simulationTerminee) return;

                const jetonEl = document.querySelector('[name=csrfmiddlewaretoken]');
                const jeton = jetonEl ? jetonEl.value : '';
                btnEnregistrer.disabled = true;

                fetch(btnEnregistrer.dataset.apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': jeton },
                    body: JSON.stringify(derniereCellule)
                })
                    .then(res => res.json().then(donnees => ({ ok: res.ok, donnees })))
                    .then(({ ok, donnees }) => {
                        if (ok) {
                            afficherMessage(`Enregistrée : ${donnees.fichier}`);
                        } else {
                            btnEnregistrer.disabled = false;
                            afficherMessage(`Échec : ${donnees.erreur}`);
                        }
                    })
                    .catch(err => {
                        btnEnregistrer.disabled = false;
                        afficherMessage("Échec de l'enregistrement : serveur injoignable.");
                        console.error("Erreur enregistrement :", err);
                    });
            });
        }

    }
}
