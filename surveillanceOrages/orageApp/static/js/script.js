const mapElement = document.getElementById('map');

if (mapElement) {
    const map = L.map('map').setView([46.60, 2.20], 6);

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16,
        attribution: 'Tiles &copy; Esri'
    }).addTo(map);

    // Affichage des coordonnées au clic
    map.on('click', function (e) {
        const latitude = e.latlng.lat.toFixed(4);
        const longitude = e.latlng.lng.toFixed(4);
        L.popup()
            .setLatLng(e.latlng)
            .setContent(`<b>Position sélectionnée</b><br>Lat: ${latitude}<br>Lon: ${longitude}`)
            .openOn(map);
    });

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

    // Bouton effacer les impacts
    const btnEffacer = document.getElementById('btn-effacer');
    if (btnEffacer) {
        btnEffacer.addEventListener('click', function () {
            map.eachLayer(function (layer) {
                if (layer instanceof L.CircleMarker) {
                    map.removeLayer(layer);
                }
            });
        });
    }
}