const map = L.map('map').setView([46.60, 2.20], 6);

L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap France'
}).addTo(map);

map.on('click', function(e) {
    const latitude = e.latlng.lat.toFixed(4);
    const longitude = e.latlng.lng.toFixed(4);
    L.popup().setLatLng(e.latlng).setContent(`Latitude: ${latitude}, Longitude: ${longitude}`).openOn(map);
})