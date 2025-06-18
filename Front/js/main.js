
const weekdays = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"];
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
  const res = await fetch("https://parking-predictor.onrender.com/lots");
  const lots = await res.json();
  lotSelect.innerHTML = lots.map(lot =>
    `<option value="${lot.lot_id}">${lot.name}</option>`).join("");
}

async function fetchAvailability() {
  const weekday = daySelect.value;
  const hour = document.getElementById("hourSelect").value;
  const lotId = lotSelect.value;

  const url = `https://parking-predictor.onrender.com/prediction?lot_id=${lotId}&weekday=${encodeURIComponent(weekday)}&hour=${hour}`;
  const res = await fetch(url);
  const data = await res.json();

  const resultsEl = document.getElementById("results");
  resultsEl.innerHTML = `
    <div class="border-b py-2">
      <strong>${data.name || ""}</strong> (${data.lot_id})<br>
      שעה ${data.hour}:00 ביום ${data.weekday}<br>
      מצב חזוי: ${Object.entries(data.prediction || {}).map(([status, prob]) => `${status}: ${Math.round(prob * 100)}%`).join(" | ")}
    </div>
  `;
}
