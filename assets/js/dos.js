var running = false;
var startTime = null;
var pollTimer = null;

function validIP(ip) {
    var pattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!pattern.test(ip)) return false;
    var parts = ip.split('.');
    for (var i = 0; i < parts.length; i++) {
        if (parseInt(parts[i]) > 255) return false;
    }
    return true;
}

function validPort(port) {
    return !isNaN(port) && port >= 1 && port <= 65535;
}

function addLog(type, label, msg) {
    var log = document.getElementById('attackLog');
    var empty = log.querySelector('.log-empty');
    if (empty) empty.remove();

    var time = new Date().toLocaleTimeString('en-GB');
    var p = document.createElement('p');
    p.className = 'log-line';
    p.innerHTML = '[' + time + '] <span class="log-' + type + '">' + label + '</span> — ' + msg;
    log.appendChild(p);
    log.scrollTop = log.scrollHeight;
}

function setStatus(state, msg) {
    var dot = document.querySelector('.status-dot-dos');
    var text = document.getElementById('statusText');
    dot.className = 'status-dot-dos ' + state;
    text.textContent = msg;
}

function saveDosToStorage(ip, port, packets, secs) {
    var time = new Date().toLocaleTimeString('en-GB');
    var logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
    var target = port ? ip + ':' + port : ip;
    logs.push({ type: 'dos', time: time, target: target, details: packets + ' packets sent in ' + secs + 's', packets: packets });
    localStorage.setItem('netwolf_logs', JSON.stringify(logs));
}

function startAttack() {
    var ip = document.getElementById('targetIP').value.trim();
    var port = parseInt(document.getElementById('targetPort').value);
    var duration = parseInt(document.getElementById('duration').value);
    var attackType = document.getElementById('attackType').value;
    var threadCount = parseInt(document.getElementById('threadCount').value) || 4;
    var error = document.getElementById('errorMsg');

    var needsPort = attackType !== 'HTTP_FLOOD';
    if (!validIP(ip) || (needsPort && !validPort(port)) || isNaN(duration) || duration < 1) {
        error.classList.remove('hidden');
        return;
    }

    error.classList.add('hidden');
    running = true;
    startTime = Date.now();

    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    document.getElementById('attackLog').innerHTML = '';
    document.getElementById('statStatus').textContent = 'RUNNING';
    document.getElementById('statStatus').className = 'stat-value stat-running';
    document.getElementById('statPackets').textContent = '0';
    document.getElementById('statPPS').textContent = '0';
    document.getElementById('statTime').textContent = '0s';

    setStatus('running', 'ATTACKING ' + ip + (needsPort ? ':' + port : '') + ' (' + attackType + ')');
    addLog('warn', 'INITIATED', attackType + ' for ' + duration + 's with ' + threadCount + ' threads');

    pollTimer = setInterval(function() {
        if (!running) { clearInterval(pollTimer); return; }
        var secs = ((Date.now() - startTime) / 1000).toFixed(1);
        document.getElementById('statTime').textContent = secs + 's';
    }, 500);

    var body = {
        ip: ip,
        attackType: attackType,
        threadCount: Math.min(4, Math.max(1, threadCount)),
        duration: duration
    };
    if (needsPort) body.port = port;

    postDos(body)
    .then(function(res) {
        clearInterval(pollTimer);
        running = false;

        var data = res.data;
        var secs = data.duration || ((Date.now() - startTime) / 1000).toFixed(1);

        if (res.ok && data.success) {
            var packets = data.packetsSent || 0;
            var pps = data.pps || 0;
            document.getElementById('statPackets').textContent = packets;
            document.getElementById('statTime').textContent = secs + 's';
            document.getElementById('statPPS').textContent = pps;
            document.getElementById('statStatus').textContent = 'DONE';
            document.getElementById('statStatus').className = 'stat-value stat-done';
            setStatus('done', 'ATTACK COMPLETE — ' + packets + ' PACKETS SENT');
            addLog('ok', 'COMPLETE', packets + ' packets in ' + secs + 's (' + pps + ' pps)');
            saveDosToStorage(ip, needsPort ? port : null, packets, secs);
        } else {
            document.getElementById('statStatus').textContent = 'ERROR';
            document.getElementById('statStatus').className = 'stat-value stat-done';
            setStatus('done', 'ERROR: ' + (data.message || 'Attack failed'));
            addLog('err', 'FAILED', data.message || 'Attack failed');
        }

        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
    })
    .catch(function() {
        clearInterval(pollTimer);
        running = false;
        setStatus('done', 'CONNECTION ERROR — IS FLASK RUNNING?');
        addLog('err', 'ERROR', 'Could not connect to backend');
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('statStatus').textContent = 'ERROR';
    });
}

function stopAttack() {
    running = false;
    clearInterval(pollTimer);
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('statStatus').textContent = 'STOPPED';
    document.getElementById('statStatus').className = 'stat-value stat-done';
    setStatus('done', 'ATTACK STOPPED');
    addLog('err', 'STOPPED', 'UI stopped — backend finishes current duration');
}
