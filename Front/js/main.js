
const weekdays = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"];
const weekdayMap = {
  "ראשון": "sunday",
  "שני": "monday",
  "שלישי": "tuesday",
  "רביעי": "wednesday",
  "חמישי": "thursday",
  "שישי": "friday",
  "שבת": "saturday"
};
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
const statusLabels = {
  available: "פנוי",
  full: "מלא",
  limited: "מעט",
  unknown: "לא ידוע",
  no_data: "אין נתונים"
};
const API_BASE = "https://parking-predictor.onrender.com";


const daySelect = document.getElementById("daySelect");
const holidayToggle = document.getElementById("holidayToggle");
const lotSelect = document.getElementById("lotSelect");

function populateDays() {
  const useHolidays = holidayToggle.checked;
  const options = useHolidays ? holidays : weekdays;
  daySelect.innerHTML = options.map(day => `<option value="${day}">${day}</option>`).join("");
}

holidayToggle.addEventListener("change", populateDays);
window.onload = () => {
  populateDays();
  fetchLots();
};

async function fetchLots() {
  try {
    const res = await fetch(`${API_BASE}/lots`);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const lots = await res.json();
    lotSelect.innerHTML = lots.map(lot =>
      `<option value="${lot.lot_id}">${lot.name}</option>`).join("");
  } catch (error) {
    console.error('Error fetching lots:', error);
    lotSelect.innerHTML = '<option>Error loading lots</option>';
  }
}

async function fetchAvailability() {
  const useHolidays = holidayToggle.checked;
  const selectedHebrewDay = daySelect.value;
  const weekday = useHolidays ? selectedHebrewDay : weekdayMap[selectedHebrewDay];
  const hour = document.getElementById("hourSelect").value;
  const lotId = lotSelect.value;
  const lotName = lotSelect.options[lotSelect.selectedIndex].text;

  const url = `${API_BASE}/prediction?lot_id=${lotId}&weekday=${encodeURIComponent(weekday)}&hour=${hour}`;
  const res = await fetch(url);
  const data = await res.json();
  console.log(data);

  const resultsEl = document.getElementById("results");
  resultsEl.innerHTML = `
  <div class="border-b py-2">
    <b>חניון ${lotName}, שעה ${data.hour}:00, ביום ${selectedHebrewDay} בדרך כלל - </b><br>
    ${(() => {
      const prediction = data.prediction || {};
      let totalUnknown = 0;
      const readableStatuses = [];

      for (const [status, prob] of Object.entries(prediction)) {
        if (status === "unknown" || status === "no_data") {
          totalUnknown += prob;
        } else if (prob > 0) {
          readableStatuses.push(`${statusLabels[status] || status}: ${Math.round(prob * 100)}%`);
        }
      }

      if (totalUnknown > 0) {
        readableStatuses.push(`אין מידע: ${Math.round(totalUnknown * 100)}%`);
      }

      return readableStatuses.join(" <br> ");
    })()}
    <br>
    מחירים ותפוסת זמן אמת בחניון 
    <a href="${data.url}" target="_blank" class="text-blue-600 hover:underline hover:text-blue-800 transition">כאן</a>
  </div>
`;

}
