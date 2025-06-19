// map_prediction.js

const API_BASE = "https://parking-predictor.onrender.com";

const weekdays = [
    "ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"
];

const statusColors = {
    available: "green",
    limited: "orange",
    full: "red",
    unknown: "gray",
    no_data: "gray"
};

const statusLabels = {
  available: "פנוי",
  limited: "מעט",
  full: "מלא",
  unknown: "לא ידוע",
  no_data: "אין נתונים"
};

const daySelect = document.getElementById("daySelect");
const hourSelect = document.getElementById("hourSelect");

// populate weekday dropdown
function populateDays() {
    daySelect.innerHTML = weekdays.map(day => `<option value="${day}">${day}</option>`).join("");
}

populateDays();

// initialize map
const map = L.map("map").setView([32.08, 34.78], 13); // Centered on Tel Aviv
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

let markersLayer = L.layerGroup().addTo(map);

async function loadMapData() {
    const weekday = daySelect.value;
    const hour = hourSelect.value;
    const url = `${API_BASE}/availability?weekday=${encodeURIComponent(weekday)}&hour=${hour}`;

    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error("API error");
        const data = await res.json();
        console.log(data)

        markersLayer.clearLayers();

        data.forEach(lot => {
            const lat = lot.location.coordinates[1];
            const lng = lot.location.coordinates[0];
            console.log(lng)
            if (!lat || !lng) return;

            const color = statusColors[lot.status] || "gray";
            const hebrewStatus = statusLabels[lot.status] || lot.status;
            const circle = L.circleMarker([lat, lng], {
                radius: 8,
                fillColor: color,
                color: "#333",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(markersLayer);

            circle.bindPopup(`<b>${lot.name}</b><br>${lot.lot_id}<br>תחזית: ${hebrewStatus}`);
        });
    } catch (err) {
        alert("אירעה שגיאה בעת טעינת הנתונים.");
        console.error(err);
    }
}
