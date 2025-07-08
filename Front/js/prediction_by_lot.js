// parking_lot.js - ParkInsight Parking Lot Prediction Page

// Constants
const weekdays = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"];
const holidays = [
  "ערב פסח", "פסח א׳", "ערב חג שני", "פסח 7", "ערב יום השואה",
  "יום השואה", "ערב יום הזיכרון", "יום הזיכרון", "יום העצמאות",
  "ערב שבועות", "שבועות"
];
const API_BASE = "https://parking-predictor.onrender.com";

// Populate days function
function populateDays() {
  const daySelect = document.getElementById('daySelect');
  const holidayToggle = document.getElementById('holidayToggle');
  const useHolidays = holidayToggle.checked;
  const options = useHolidays ? holidays : weekdays;
  daySelect.innerHTML = options.map(day => `<option value="${day}">${day}</option>`).join("");
}

// Load parking lots function
async function fetchLots() {
  try {
    const lotSelect = document.getElementById('lotSelect');
    const res = await fetch(`${API_BASE}/lots`);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const lots = await res.json();
    lotSelect.innerHTML = lots.map(lot =>
      `<option value="${lot.lot_id}">${lot.name}</option>`).join("");
  } catch (error) {
    console.error('Error fetching lots:', error);
    document.getElementById('lotSelect').innerHTML = '<option>Error loading lots</option>';
  }
}

// Real API integration for availability prediction
async function fetchAvailability() {
  const resultsSection = document.getElementById('results');
  const resultTitle = document.getElementById('resultTitle');
  const freePercent = document.getElementById('freePercent');
  const fullPercent = document.getElementById('fullPercent');
  const lowPercent = document.getElementById('lowPercent');

   // Get the button for loading states
  // const submitButton = document.querySelector('.btn-primary');
  // const originalButtonContent = submitButton.innerHTML;
  
  try {
     // Show loading state on button
    // submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> טוען תחזית...';
    // submitButton.disabled = true;
    // Show loading state in results
    resultTitle.textContent = 'טוען תחזית...';
    freePercent.textContent = '...';
    fullPercent.textContent = '...';
    lowPercent.textContent = '...';
    resultsSection.classList.remove('hidden');
    
    // Get form values
    const weekday = document.getElementById('daySelect').value;
    const hour = document.getElementById('hourSelect').value;
    const lotId = document.getElementById('lotSelect').value;
    const lotName = document.getElementById('lotSelect').options[document.getElementById('lotSelect').selectedIndex].text;
    
    // Make real API call
    const url = `${API_BASE}/prediction?lot_id=${lotId}&weekday=${encodeURIComponent(weekday)}&hour=${hour}`;
    const res = await fetch(url);
    const data = await res.json();
    
    // Update title with real context
    resultTitle.textContent = `חניון ${lotName}, שעה ${data.hour}:00, ביום ${weekday} בדרך כלל`;
    
    // Extract real prediction data
    const prediction = data.prediction || {};
    
    // Update with real percentages
    freePercent.textContent = Math.round((prediction.available || 0) * 100) + '%';
    fullPercent.textContent = Math.round((prediction.full || 0) * 100) + '%';
    lowPercent.textContent = Math.round((prediction.limited || 0) * 100) + '%';
    
    // Update link with real URL
    const linkElement = resultsSection.querySelector('a');
    if (linkElement && data.url) {
      linkElement.href = data.url;
    }

    // // SUCCESS FEEDBACK: Show success state on button
    // submitButton.innerHTML = '<i class="fas fa-check"></i> נטען בהצלחה!';
    // submitButton.style.background = 'var(--success)';
    
    // AUTO-SCROLL: Scroll to results after short delay
    setTimeout(() => {
      resultsSection.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }, 500);
    
    // Reset button after 2 seconds
    // setTimeout(() => {
    //   submitButton.innerHTML = originalButtonContent;
    //   submitButton.style.background = '';
    //   submitButton.disabled = false;
    // }, 2000);
    
  } catch (error) {
    console.error("Error fetching availability:", error);
    resultTitle.textContent = "שגיאה בטעינת התחזית";
    freePercent.textContent = "--";
    fullPercent.textContent = "--";
    lowPercent.textContent = "--";
  }
}

// Enhanced interactions and animations
document.addEventListener('DOMContentLoaded', function() {
  // Initialize data
  populateDays();
  fetchLots();
  
  // Holiday toggle listener
  document.getElementById('holidayToggle').addEventListener('change', populateDays);
  
  // Attach click event to button (instead of onclick in HTML)
  const submitButton = document.querySelector('button[onclick="fetchAvailability()"]');
  if (submitButton) {
    // Remove the onclick attribute
    submitButton.removeAttribute('onclick');
    // Add event listener
    submitButton.addEventListener('click', fetchAvailability);
  }
  
  // Staggered animations
  const elements = document.querySelectorAll('.fade-in');
  elements.forEach((el, index) => {
    el.style.animationDelay = `${index * 0.1}s`;
  });
  
  // Enhanced form interactions
  document.querySelectorAll('.form-control').forEach(control => {
    control.addEventListener('focus', function() {
      this.parentElement.style.transform = 'translateY(-2px)';
      this.parentElement.style.transition = 'transform 0.2s ease';
    });
    
    control.addEventListener('blur', function() {
      this.parentElement.style.transform = 'translateY(0)';
    });
  });
});