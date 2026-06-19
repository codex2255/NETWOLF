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

function getStatus() {
    var rand = Math.random();
    if (rand < 0.3) return 'open';
    if (rand < 0.8) return 'closed';
    return 'filtered';
}

function getTime(status) {
    if (status === 'filtered') return 'timeout';
    return Math.floor(Math.random() * 20 + 2) + 'ms';
}

function addRow(port, service, status, time) {
    var body = document.getElementById('resultsBody');
    var empty = body.querySelector('.no-results');
    if (empty) empty.remove();

    var row = document.createElement('div');
    row.className = 'result-row';
    row.innerHTML = '<span>' + port + '</span><span>' + service + '</span><span class="status-' + status + '">' + status.toUpperCase() + '</span><span>' + time + '</span>';
    body.appendChild(row);
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

    var current = start;

    var timer = setInterval(function() {
        if (current > end) {
            clearInterval(timer);
            statusText.textContent = 'SCAN COMPLETE — ' + (end - start + 1) + ' PORTS SCANNED';
            btn.disabled = false;
            return;
        }
        var status = getStatus();
        var time = getTime(status);
        addRow(current, getService(current), status, time);
        current++;
    }, 80);
}