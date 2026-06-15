const PORT_SERVICES = {
    21:   'FTP',
    22:   'SSH',
    23:   'Telnet',
    25:   'SMTP',
    53:   'DNS',
    80:   'HTTP',
    110:  'POP3',
    143:  'IMAP',
    443:  'HTTPS',
    445:  'SMB',
    3306: 'MySQL',
    3389: 'RDP',
    5900: 'VNC',
    8080: 'HTTP-ALT',
    8443: 'HTTPS-ALT',
};


function getServiceName(port) {
    return PORT_SERVICES[port] || 'UNKNOWN';
}


/**
 * Validates IPv4 address format
 * @param {string} ip
 * @returns {boolean}
 */
function isValidIP(ip) {
    const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!ipPattern.test(ip)) return false;

    // Each octet must be 0-255
    const octets = ip.split('.');
    return octets.every(o => parseInt(o) >= 0 && parseInt(o) <= 255);
}

/**
 * Validates that port range is within 1-65535
 * and start is less than or equal to end
 * @param {number} start
 * @param {number} end
 * @returns {boolean}
 */
function isValidPortRange(start, end) {
    return (
        start >= 1 && end <= 65535 &&
        start <= end &&
        !isNaN(start) && !isNaN(end)
    );
}


// ================================================
// SECTION 3: SCAN SIMULATION
// Simulates port scan results with random statuses
// In production this will call Josh's Python backend
// ================================================

const STATUSES = ['open', 'closed', 'filtered'];
const STATUS_WEIGHTS = [0.3, 0.5, 0.2]; // 30% open, 50% closed, 20% filtered

/**
 * Returns a weighted random scan status
 * @returns {string} 'open' | 'closed' | 'filtered'
 */
function getRandomStatus() {
    const rand = Math.random();
    let cumulative = 0;
    for (let i = 0; i < STATUSES.length; i++) {
        cumulative += STATUS_WEIGHTS[i];
        if (rand < cumulative) return STATUSES[i];
    }
    return 'closed';
}

/**
 * Simulates a port scan result for a single port
 * @param {number} port
 * @returns {object} scan result object
 */
function simulateScanPort(port) {
    const status = getRandomStatus();
    const responseTime = status === 'closed'
        ? `${Math.floor(Math.random() * 10 + 2)}ms`
        : status === 'filtered'
        ? 'timeout'
        : `${Math.floor(Math.random() * 20 + 5)}ms`;

    return {
        port,
        service: getServiceName(port),
        status,
        responseTime,
    };
}


// ================================================
// SECTION 4: RESULTS RENDERING
// Injects scan results into the DOM results table
// ================================================

/**
 * Renders a single result row into the results body
 * @param {object} result - scan result object
 */
function renderResultRow(result) {
    const body = document.getElementById('resultsBody');

    // Remove empty state message on first result
    const noResults = body.querySelector('.no-results');
    if (noResults) noResults.remove();

    const row = document.createElement('div');
    row.classList.add('result-row');
    row.innerHTML = `
        <span>${result.port}</span>
        <span>${result.service}</span>
        <span class="status-${result.status}">${result.status.toUpperCase()}</span>
        <span>${result.responseTime}</span>
    `;
    body.appendChild(row);
}


function startScan() {
    const ip        = document.getElementById('targetIP').value.trim();
    const portStart = parseInt(document.getElementById('portStart').value);
    const portEnd   = parseInt(document.getElementById('portEnd').value);
    const errorMsg  = document.getElementById('errorMsg');
    const statusBar = document.getElementById('statusBar');
    const statusText = document.getElementById('statusText');
    const scanBtn   = document.getElementById('scanBtn');
    const resultsBody = document.getElementById('resultsBody');

    if (!isValidIP(ip) || !isValidPortRange(portStart, portEnd)) {
        errorMsg.classList.remove('hidden');
        return;
    }

    errorMsg.classList.add('hidden');
    resultsBody.innerHTML = '';
    statusBar.classList.remove('hidden');
    statusText.textContent = `SCANNING ${ip} — PORTS ${portStart} TO ${portEnd}...`;
    scanBtn.disabled = true;

    fetch('http://127.0.0.1:5000/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip, portStart, portEnd })
    })
    .then(res => res.json())
    .then(data => {
        statusText.textContent = `SCAN COMPLETE`;
        scanBtn.disabled = false;

        if (data.results && data.results.length > 0) {
            data.results.forEach(result => renderResultRow(result));
        } else {
            resultsBody.innerHTML = '<p class="no-results">No open ports found.</p>';
        }
    })
    .catch(err => {
        statusText.textContent = 'ERROR — Could not connect to backend.';
        scanBtn.disabled = false;
    });
}