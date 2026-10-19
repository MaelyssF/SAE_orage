const map = L.map('map').setView([46.60, 2.20], 6);

L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16,
    attribution: 'Tiles &copy; Esri'
}).addTo(map);

map.on('click', function (e) {
    const latitude = e.latlng.lat.toFixed(4);
    const longitude = e.latlng.lng.toFixed(4);
    L.popup().setLatLng(e.latlng).setContent(`Latitude: ${latitude}, Longitude: ${longitude}`).openOn(map);
})

// Gestion des boutons pour générer et effacer les impacts

document.getElementById('btn-generer').addEventListener('click', function () {
    fetch('/api/generer-impact/')
        .then(response => response.json())
        .then(data => {
            console.log("Coordonnées reçues : ", data);
            L.circleMarker([data.latitude, data.longitude], {
                radius: 3,
                color: "#ff0000",
                fillColor: "#ff3333",
                fillOpacity: 0.9,
                weight: 1
            }).addTo(map).bindPopup(`Impact de foudre simulé. <br>Lat: ${data.latitude}<br>Lon: ${data.longitude}`).openPopup();
        }).catch(error => {
            console.error('Erreur lors de la génération :', error);
        });
});

document.getElementById('btn-generer-10').addEventListener('click', function () {
    fetch('/api/generer-10-impacts/')
        .then(response => response.json())
        .then(data => {
            console.log("Coordonnées reçues : ", data);
            for (const impact of data.impacts) {
                L.circleMarker([impact.latitude, impact.longitude], {
                    radius: 3,
                    color: "#ff0000",
                    fillColor: "#ff3333",
                    fillOpacity: 0.9,
                    weight: 1
                }).addTo(map).bindPopup(`Impact de foudre simulé. <br>Lat: ${impact.latitude}<br>Lon: ${impact.longitude}`);
            }
        }).catch(error => {
            console.error('Erreur lors de la génération :', error);
        });
});

document.getElementById('btn-effacer').addEventListener('click', function () {
    map.eachLayer(function (layer) {
        if (layer instanceof L.CircleMarker) {
            map.removeLayer(layer);
        }
    });
});