function countUp(id, target) {
    var el = document.getElementById(id);
    if (target == 0) { el.textContent = 0; return; }
    var count = 0;
    var step = Math.ceil(target / 50);
    var timer = setInterval(function() {
        count += step;
        if (count >= target) {
            count = target;
            clearInterval(timer);
        }
        el.textContent = count;
    }, 30);
}

function countOpenPorts(results) {
    var openPorts = 0;
    var vulnCount = 0;
    if (!results) return { openPorts: 0, vulnCount: 0 };
    for (var i = 0; i < results.length; i++) {
        if (results[i].status == 'open' || results[i].status == 'open|filtered') {
            openPorts++;
            var port = results[i].port;
            if (port == 21 || port == 23 || port == 445 || port == 3389 || port == 5900) {
                vulnCount++;
            }
        }
    }
    return { openPorts: openPorts, vulnCount: vulnCount };
}

function renderActivity(logs) {
    var container = document.getElementById('activityLog');
    container.innerHTML = '';

    if (logs.length == 0) {
        var p = document.createElement('p');
        p.style.color = '#999';
        p.style.fontSize = '11px';
        p.style.letterSpacing = '1px';
        p.textContent = 'No activity yet. Run a scan or DoS test to see logs here.';
        container.appendChild(p);
        return;
    }

    var recent = logs.slice().reverse().slice(0, 8);
    for (var j = 0; j < recent.length; j++) {
        var p = document.createElement('p');
        p.className = 'log-line';
        var typeClass = recent[j].type == 'scan' ? 'log-ok' : 'log-warn';
        var label = recent[j].type == 'scan' ? 'SCAN' : 'DoS';
        p.innerHTML = '[' + recent[j].time + '] <span class="' + typeClass + '">' + label + '</span> — ' + recent[j].details;
        container.appendChild(p);
    }
}

function loadDashboard() {
    var logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
    var scansRun = logs.filter(function(l) { return l.type == 'scan'; }).length;

    countUp('scansRun', scansRun);
    renderActivity(logs);

    getReports()
    .then(function(res) {
        if (res.ok && res.data.success && res.data.reports && res.data.reports.length > 0) {
            return getReport(res.data.reports[0].id);
        }
        return null;
    })
    .then(function(reportRes) {
        if (reportRes && reportRes.ok && reportRes.data.success) {
            var counts = countOpenPorts(reportRes.data.report.results);
            countUp('openPorts', counts.openPorts);
            countUp('vulnCount', counts.vulnCount);
            return;
        }
        var lastScan = JSON.parse(localStorage.getItem('netwolf_last_scan') || 'null');
        if (lastScan && lastScan.results) {
            var counts = countOpenPorts(lastScan.results);
            countUp('openPorts', counts.openPorts);
            countUp('vulnCount', counts.vulnCount);
        } else {
            countUp('openPorts', 0);
            countUp('vulnCount', 0);
        }
    })
    .catch(function() {
        var lastScan = JSON.parse(localStorage.getItem('netwolf_last_scan') || 'null');
        if (lastScan && lastScan.results) {
            var counts = countOpenPorts(lastScan.results);
            countUp('openPorts', counts.openPorts);
            countUp('vulnCount', counts.vulnCount);
        }
    });

    getNetworkInfo()
    .then(function(res) {
        var el = document.getElementById('networkInfo');
        if (res.ok && res.data.success && el) {
            el.innerHTML = 'NETWORK: <span style="color:#ff4444">' + res.data.localNetwork + '</span> | ROUTER: <span style="color:#ff4444">' + (res.data.routerIp || 'unknown') + '</span>';
        }
    })
    .catch(function() {
        var el = document.getElementById('networkInfo');
        if (el) el.textContent = 'Network info unavailable — is the backend running?';
    });
}

loadDashboard();
