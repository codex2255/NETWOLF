function loadSettings() {
    var s = localStorage.getItem('netwolf_settings');
    if (!s) return { defaultPort: 1024, timeout: 1000 };
    try {
        return JSON.parse(s);
    } catch (e) {
        return { defaultPort: 1024, timeout: 1000 };
    }
}

var services = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
    53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
    443: 'HTTPS', 445: 'SMB', 3306: 'MySQL', 3389: 'RDP',
    5900: 'VNC', 8080: 'HTTP-ALT', 8443: 'HTTPS-ALT'
};

function getService(port, apiService) {
    if (apiService) return String(apiService).toUpperCase();
    return services[port] || 'UNKNOWN';
}

function validIP(ip) {
    var pattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!pattern.test(ip)) return false;
    var parts = ip.split('.');
    for (var i = 0; i < parts.length; i++) {
        if (parseInt(parts[i]) > 255) return false;
    }
    return true;
}

function validPorts(start, end) {
    return !isNaN(start) && !isNaN(end) && start >= 1 && end <= 65535 && start <= end;
}

function addRow(port, service, status, protocol) {
    var body = document.getElementById('resultsBody');
    var empty = body.querySelector('.no-results');
    if (empty) empty.remove();

    var row = document.createElement('div');
    row.className = 'result-row';
    row.innerHTML = '<span>' + port + '</span><span>' + service + '</span><span class="status-' + status.replace('|', '-') + '">' + status.toUpperCase() + '</span><span>' + (protocol || 'TCP') + '</span>';
    body.appendChild(row);
}

function saveToStorage(ip, results, reportId) {
    var time = new Date().toLocaleTimeString('en-GB');
    var scanData = { ip: ip, results: results, time: time, reportId: reportId || null };
    localStorage.setItem('netwolf_last_scan', JSON.stringify(scanData));

    var logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
    var openCount = 0;
    for (var i = 0; i < results.length; i++) {
        if (results[i].status == 'open' || results[i].status == 'open|filtered') openCount++;
    }
    logs.push({ type: 'scan', time: time, target: ip, details: openCount + ' open ports found' });
    localStorage.setItem('netwolf_logs', JSON.stringify(logs));
}

function startScan() {
    var ip = document.getElementById('targetIP').value.trim();
    var start = parseInt(document.getElementById('portStart').value);
    var end = parseInt(document.getElementById('portEnd').value);
    var scanUdp = document.getElementById('scanUdp') ? document.getElementById('scanUdp').checked : false;
    var settings = loadSettings();
    var error = document.getElementById('errorMsg');
    var statusBar = document.getElementById('statusBar');
    var statusText = document.getElementById('statusText');
    var btn = document.getElementById('scanBtn');
    var body = document.getElementById('resultsBody');

    if (!validIP(ip) || !validPorts(start, end)) {
        error.classList.remove('hidden');
        return;
    }

    error.classList.add('hidden');
    body.innerHTML = '';
    statusBar.classList.remove('hidden');
    statusText.textContent = 'SCANNING ' + ip + ' — PORTS ' + start + ' TO ' + end + '...';
    btn.disabled = true;

    postScan({
        ip: ip,
        portStart: start,
        portEnd: end,
        scanUdp: scanUdp,
        timeout: parseInt(settings.timeout) || 1000
    })
    .then(function(res) {
        var data = res.data;
        if (!res.ok || !data.success) {
            statusText.textContent = 'ERROR: ' + (data.message || 'Scan failed');
            btn.disabled = false;
            return;
        }

        var results = data.results || [];
        results.sort(function(a, b) { return a.port - b.port; });

        if (results.length === 0) {
            body.innerHTML = '<p class="no-results">Scan complete — no open ports found in range.</p>';
        } else {
            for (var i = 0; i < results.length; i++) {
                addRow(
                    results[i].port,
                    getService(results[i].port, results[i].service),
                    results[i].status,
                    results[i].protocol
                );
            }
        }

        statusText.textContent = 'SCAN COMPLETE — ' + results.length + ' OPEN PORT(S) FOUND';
        saveToStorage(ip, results, data.reportId);
        btn.disabled = false;
    })
    .catch(function() {
        statusText.textContent = 'CONNECTION ERROR — IS FLASK RUNNING?';
        btn.disabled = false;
    });
}

function initScanner() {
    var settings = loadSettings();
    var portEnd = document.getElementById('portEnd');
    if (portEnd && !portEnd.value) {
        portEnd.value = settings.defaultPort || 1024;
    }
    var params = new URLSearchParams(window.location.search);
    var ipParam = params.get('ip');
    if (ipParam) {
        document.getElementById('targetIP').value = ipParam;
    }
}

document.addEventListener('DOMContentLoaded', initScanner);
