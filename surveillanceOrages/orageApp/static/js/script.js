const mapElement = document.getElementById('map');

if (mapElement) {
    // Initialisation de la carte Leaflet (centrée par défaut sur la France)
    const map = L.map('map').setView([46.60, 2.20], 6);

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

    // Bouton Effacer
    if (btnEffacer) {
        btnEffacer.addEventListener('click', effacerImpacts);
    }
}