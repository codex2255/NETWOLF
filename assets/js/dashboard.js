/* ================================================
   NETWOLF — Dashboard Logic
   Handles dynamic stat counters and activity log
   Project: CS205 - Integrated Studio III
   Team: Josh (Backend) & Vishesh (Frontend)
   ================================================ */


// ================================================
// SECTION 1: STAT CARD COUNTER ANIMATION
// Numbers count up from 0 to target value on load
// ================================================

/**
 * Animates a number counting up from 0 to target
 * @param {string} elementId - The DOM element ID to update
 * @param {number} target    - The final number to count to
 * @param {number} duration  - Total animation time in ms
 */
function animateCounter(elementId, target, duration) {
    const element = document.getElementById(elementId);
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease-out effect — fast start, slow finish
        const eased = 1 - Math.pow(1 - progress, 3);
        element.textContent = Math.floor(eased * target);

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Animate all three stat cards on page load
animateCounter('scansRun', 24, 1500);
animateCounter('openPorts', 138, 1500);
animateCounter('vulnCount', 7, 1200);


// ================================================
// SECTION 2: ACTIVITY LOG
// Renders recent activity entries into the log div
// Each entry has a timestamp, status, and message
// ================================================

// Sample log data — will be replaced with real backend data
const activityLogs = [
    { time: '14:22:01', status: 'ok',   label: 'SUCCESS', message: 'Port scan completed → 192.168.1.1' },
    { time: '14:20:44', status: 'warn', label: 'WARNING', message: 'Port 8080 open on target host' },
    { time: '14:18:30', status: 'err',  label: 'ALERT',   message: 'Vulnerability detected → CVE-2021-44228' },
    { time: '14:15:12', status: 'ok',   label: 'SUCCESS', message: 'DoS stress test completed' },
    { time: '14:10:05', status: 'ok',   label: 'SUCCESS', message: 'Session initialized' },
];

/**
 * Renders log entries into the #activityLog container
 * Each entry is injected as an HTML string with correct status colour class
 */
function renderActivityLog() {
    const logContainer = document.getElementById('activityLog');

    // Map each log entry to an HTML line
    const logHTML = activityLogs.map(entry => {
        return `<p class="log-line">
            [${entry.time}] 
            <span class="log-${entry.status}">${entry.label}</span> 
            — ${entry.message}
        </p>`;
    }).join('');

    logContainer.innerHTML = logHTML;
}

// Render log on page load
renderActivityLog();