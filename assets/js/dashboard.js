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

function loadDashboard() {
    var logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
    var lastScan = JSON.parse(localStorage.getItem('netwolf_last_scan') || 'null');

    var scansRun = logs.filter(function(l) { return l.type == 'scan'; }).length;
    var openPorts = 0;
    var vulnCount = 0;

    if (lastScan && lastScan.results) {
        for (var i = 0; i < lastScan.results.length; i++) {
            if (lastScan.results[i].status == 'open') {
                openPorts++;
                var port = lastScan.results[i].port;
                if (port == 21 || port == 23 || port == 445 || port == 3389 || port == 5900) {
                    vulnCount++;
                }
            }
        }
    }

    countUp('scansRun', scansRun);
    countUp('openPorts', openPorts);
    countUp('vulnCount', vulnCount);

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

function checkStatus() {
    fetch('http://127.0.0.1:5000/health')
    .then(function(res) { return res.json(); })
    .then(function() {
        var dot = document.querySelector('.status-dot');
        var text = document.querySelector('.status-text');
        if (dot) dot.style.backgroundColor = '#22ff66';
        if (text) { text.textContent = 'SYSTEM ONLINE'; text.style.color = '#22ff66'; }
    })
    .catch(function() {
        var dot = document.querySelector('.status-dot');
        var text = document.querySelector('.status-text');
        if (dot) dot.style.backgroundColor = '#ff3333';
        if (text) { text.textContent = 'SYSTEM OFFLINE'; text.style.color = '#ff3333'; }
    });
}

loadDashboard();
checkStatus();