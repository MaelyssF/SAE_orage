const map = L.map('map').setView([46.60, 2.20], 6);

L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap France'
}).addTo(map);