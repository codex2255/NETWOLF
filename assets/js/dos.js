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
    logs.push({ type: 'dos', time: time, target: ip + ':' + port, details: packets + ' packets sent in ' + secs + 's', packets: packets });
    localStorage.setItem('netwolf_logs', JSON.stringify(logs));
}

function startAttack() {
    var ip = document.getElementById('targetIP').value.trim();
    var port = parseInt(document.getElementById('targetPort').value);
    var packets = parseInt(document.getElementById('packetCount').value);
    var error = document.getElementById('errorMsg');

    if (!validIP(ip) || !validPort(port) || isNaN(packets) || packets < 1) {
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

    setStatus('running', 'ATTACKING ' + ip + ':' + port);
    addLog('warn', 'INITIATED', 'Sending ' + packets + ' packets to ' + ip + ':' + port);

    pollTimer = setInterval(function() {
        if (!running) { clearInterval(pollTimer); return; }
        var secs = ((Date.now() - startTime) / 1000).toFixed(1);
        document.getElementById('statTime').textContent = secs + 's';
        addLog('warn', 'RUNNING', 'Attack in progress... ' + secs + 's elapsed');
    }, 2000);

    fetch('http://127.0.0.1:5000/dos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip: ip, port: port, packetCount: packets })
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        clearInterval(pollTimer);
        running = false;

        var secs = ((Date.now() - startTime) / 1000).toFixed(1);

        if (data.success) {
            document.getElementById('statPackets').textContent = packets;
            document.getElementById('statTime').textContent = secs + 's';
            document.getElementById('statPPS').textContent = Math.floor(packets / (secs > 0 ? secs : 1));
            document.getElementById('statStatus').textContent = 'DONE';
            document.getElementById('statStatus').className = 'stat-value stat-done';
            setStatus('done', 'ATTACK COMPLETE — ' + packets + ' PACKETS SENT');
            addLog('ok', 'COMPLETE', packets + ' packets sent in ' + secs + 's');
            saveDosToStorage(ip, port, packets, secs);
        } else {
            document.getElementById('statStatus').textContent = 'ERROR';
            document.getElementById('statStatus').className = 'stat-value stat-done';
            setStatus('done', 'ERROR: ' + data.message);
            addLog('err', 'FAILED', data.message);
        }

        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
    })
    .catch(function(err) {
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
    addLog('err', 'STOPPED', 'UI stopped — backend finishes current batch');
}