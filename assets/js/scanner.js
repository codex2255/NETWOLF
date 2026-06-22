var services = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
    53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
    443: 'HTTPS', 445: 'SMB', 3306: 'MySQL', 3389: 'RDP',
    5900: 'VNC', 8080: 'HTTP-ALT', 8443: 'HTTPS-ALT'
};

function getService(port) {
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

function addRow(port, service, status) {
    var body = document.getElementById('resultsBody');
    var empty = body.querySelector('.no-results');
    if (empty) empty.remove();

    var row = document.createElement('div');
    row.className = 'result-row';
    row.innerHTML = '<span>' + port + '</span><span>' + service + '</span><span class="status-' + status + '">' + status.toUpperCase() + '</span><span>-</span>';
    body.appendChild(row);
}

function saveToStorage(ip, results) {
    var time = new Date().toLocaleTimeString('en-GB');
    var scanData = { ip: ip, results: results, time: time };
    localStorage.setItem('netwolf_last_scan', JSON.stringify(scanData));

    var logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
    var openCount = 0;
    for (var i = 0; i < results.length; i++) {
        if (results[i].status == 'open') openCount++;
    }
    logs.push({ type: 'scan', time: time, target: ip, details: openCount + ' open ports found' });
    localStorage.setItem('netwolf_logs', JSON.stringify(logs));
}

function startScan() {
    var ip = document.getElementById('targetIP').value.trim();
    var start = parseInt(document.getElementById('portStart').value);
    var end = parseInt(document.getElementById('portEnd').value);
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

    fetch('http://127.0.0.1:5000/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip: ip, portStart: start, portEnd: end })
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (!data.success) {
            statusText.textContent = 'ERROR: ' + data.message;
            btn.disabled = false;
            return;
        }

        var results = data.results;
        results.sort(function(a, b) { return a.port - b.port; });

        for (var i = 0; i < results.length; i++) {
            addRow(results[i].port, getService(results[i].port), results[i].status);
        }

        statusText.textContent = 'SCAN COMPLETE — ' + results.length + ' PORTS SCANNED';
        saveToStorage(ip, results);
        btn.disabled = false;
    })
    .catch(function(err) {
        statusText.textContent = 'CONNECTION ERROR — IS FLASK RUNNING?';
        btn.disabled = false;
    });
}