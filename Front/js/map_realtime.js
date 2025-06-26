const map = L.map("map").setView([32.08, 34.78], 13);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

let markersLayer = L.layerGroup().addTo(map);

const statusLabels = {
  available: "פנוי",
  limited: "מעט", 
  full: "מלא",
  unknown: "לא ידוע",
  no_data: "אין נתונים"
};

const statusColors = {
  available: "green",
  limited: "orange",
  full: "red",
  unknown: "gray",
  no_data: "lightgray"
};

// Change these URLs for local testing:
// const API_BASE = "http://127.0.0.1:8000";  // For local testing
const API_BASE = "https://parking-predictor.onrender.com";  // For production

async function loadRealtimeMap() {
  try {
    // Fetch both datasets
    const [realtimeRes, staticRes] = await Promise.all([
      fetch(`${API_BASE}/lots-realtime`),
      fetch(`${API_BASE}/lots`)
    ]);

    if (!realtimeRes.ok || !staticRes.ok) {
      throw new Error('Failed to fetch data');
    }

    const realtimeData = await realtimeRes.json();
    const staticData = await staticRes.json();

    // Update timestamp
   const updatedElem = document.getElementById("lastUpdated");
    if (updatedElem) {
      if (realtimeData.timestamp) {
        const scrapeTime = new Date(realtimeData.timestamp);
        const timeOnly = scrapeTime.toLocaleTimeString("he-IL", {
          hour: "2-digit",
          minute: "2-digit"
        });
        updatedElem.textContent = `עודכן לאחרונה: ${timeOnly}`;
      } else {
        updatedElem.textContent = `עודכן לאחרונה: לא ידוע`;
      }
    }

    // Clear existing markers
    markersLayer.clearLayers();

    let addedMarkers = 0;

    // Merge static (coordinates) + realtime (status) data
    staticData.forEach(staticLot => {
      // Find matching realtime data
      const realtimeLot = realtimeData.lots.find(rt => rt.id === staticLot.lot_id);
      
      if (realtimeLot) {
        // Get coordinates from static data
        const lat = staticLot.location?.coordinates?.[1];
        const lng = staticLot.location?.coordinates?.[0];
        
        if (!lat || !lng) {
          console.warn(`No coordinates for lot ${staticLot.lot_id}`);
          return;
        }

        // Get status from realtime data
        const status = realtimeLot.status || "no_data";
        const hebrewStatus = statusLabels[status] || statusLabels.no_data;
        const color = statusColors[status] || statusColors.no_data;

        // Create marker
        const circle = L.circleMarker([lat, lng], {
          radius: 8,
          fillColor: color,
          color: "#333",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.8
        }).addTo(markersLayer);

        // Create popup
        const lotLink = `<a href="https://ahuzot.co.il/Parking/ParkingDetails/?ID=${realtimeLot.id}" target="_blank" class="underline text-blue-600 hover:text-blue-800">${realtimeLot.name}</a>`;
        
        circle.bindPopup(`${lotLink}<br> ${realtimeLot.id}<br>סטטוס: ${hebrewStatus}`);
        
        addedMarkers++;
      } else {
        console.warn(`No realtime data for lot ${staticLot.lot_id}`);
      }
    });

    console.log(`Added ${addedMarkers} markers to map`);
    
    // Update counter if element exists
    const counterElem = document.getElementById("lotCount");
    if (counterElem) {
      counterElem.textContent = `${addedMarkers} חניונים`;
    }

  } catch (err) {
    console.error("Error loading realtime data:", err);
    alert("אירעה שגיאה בעת טעינת הנתונים.");
  }
}

// Load initial data
loadRealtimeMap();

// Auto-refresh every 30 seconds
setInterval(loadRealtimeMap, 30000);