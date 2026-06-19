var scansRun = 24;
var openPorts = 138;
var vulnCount = 7;

function countUp(id, target) {
    var el = document.getElementById(id);
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

countUp('scansRun', scansRun);
countUp('openPorts', openPorts);
countUp('vulnCount', vulnCount);

var logs = [
    { time: '14:22:01', type: 'ok', label: 'SUCCESS', msg: 'Port scan completed on 192.168.1.1' },
    { time: '14:20:44', type: 'warn', label: 'WARNING', msg: 'Port 8080 open on target host' },
    { time: '14:18:30', type: 'err', label: 'ALERT', msg: 'Vulnerability detected on port 443' },
    { time: '14:15:12', type: 'ok', label: 'SUCCESS', msg: 'DoS stress test completed' },
    { time: '14:10:05', type: 'ok', label: 'SUCCESS', msg: 'Session initialized' }
];

function showLogs() {
    var container = document.getElementById('activityLog');
    container.innerHTML = '';

    for (var i = 0; i < logs.length; i++) {
        var p = document.createElement('p');
        p.className = 'log-line';
        p.innerHTML = '[' + logs[i].time + '] <span class="log-' + logs[i].type + '">' + logs[i].label + '</span> — ' + logs[i].msg;
        container.appendChild(p);
    }
}

showLogs();