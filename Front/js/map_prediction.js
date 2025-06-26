// map_prediction.js

const API_BASE = "https://parking-predictor.onrender.com";

const weekdays = [
  "ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"
];

const holidays = [
  "ערב פסח",
  "פסח א׳",
  "ערב חג שני",
  "פסח 7",
  "ערב יום השואה",
  "יום השואה",
  "ערב יום הזיכרון",
  "יום הזיכרון",
  "יום העצמאות",
  "ערב שבועות",
  "שבועות"
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
const loadButton = document.getElementById("loadButton");
const holidayToggle = document.getElementById("holidayToggle");
holidayToggle.addEventListener("change", populateDays);


function populateDays() {
  const useHolidays = holidayToggle.checked;
  const options = useHolidays ? holidays : weekdays;
  daySelect.innerHTML = options.map(day => `<option value="${day}">${day}</option>`).join("");
}

populateDays();

const map = L.map("map").setView([32.08, 34.78], 13);
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

    markersLayer.clearLayers();

    data.forEach(lot => {
      const lat = lot.location?.coordinates?.[1];
      const lng = lot.location?.coordinates?.[0];
      if (!lat || !lng) return;

      const color = statusColors[lot.status] || "gray";
      const hebrewStatus = statusLabels[lot.status] || lot.status;

      const lotLink = `<a href="https://ahuzot.co.il/Parking/ParkingDetails/?ID=${lot.lot_id}" target="_blank" class="underline text-blue-600 hover:text-blue-800">${lot.name}</a>`;

      const circle = L.circleMarker([lat, lng], {
        radius: 8,
        fillColor: color,
        color: "#333",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
      }).addTo(markersLayer);

      circle.bindPopup(`${lotLink}<br>${lot.lot_id}<br>תחזית: ${hebrewStatus}`);
    });

  } catch (err) {
    alert("אירעה שגיאה בעת טעינת הנתונים.");
    console.error(err);
  }
}  

const statusMap = {
        panui: "available",
        pail: "unknown",
        meat: "limited",
        male: "full",
        // ...all other results, including null :"no_data"
    };