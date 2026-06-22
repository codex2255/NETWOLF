var running = false;
var timer = null;
var elapsed = 0;
var sent = 0;
var startTime = null;

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

function startAttack() {
    var ip = document.getElementById('targetIP').value.trim();
    var port = parseInt(document.getElementById('targetPort').value);
    var packets = parseInt(document.getElementById('packetCount').value);
    var threads = parseInt(document.getElementById('threadCount').value) || 4;
    var error = document.getElementById('errorMsg');

    if (!validIP(ip) || !validPort(port) || isNaN(packets) || packets < 1) {
        error.classList.remove('hidden');
        return;
    }

    error.classList.add('hidden');
    running = true;
    sent = 0;
    startTime = Date.now();

    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    document.getElementById('attackLog').innerHTML = '';
    document.getElementById('statStatus').textContent = 'RUNNING';
    document.getElementById('statStatus').className = 'stat-value stat-running';

    setStatus('running', 'ATTACKING ' + ip + ':' + port);
    addLog('warn', 'INITIATED', 'Attack started on ' + ip + ':' + port + ' — ' + packets + ' packets');

    var batch = threads * 2;

    timer = setInterval(function() {
        if (!running || sent >= packets) {
            stopDone(packets);
            return;
        }

        var remaining = packets - sent;
        var add = Math.min(batch, remaining);
        sent += add;

        var secs = ((Date.now() - startTime) / 1000).toFixed(1);
        var pps = Math.floor(sent / (secs > 0 ? secs : 1));

        document.getElementById('statPackets').textContent = sent;
        document.getElementById('statPPS').textContent = pps;
        document.getElementById('statTime').textContent = secs + 's';

        if (sent % 200 === 0 || sent >= packets) {
            addLog('ok', 'SENT', sent + '/' + packets + ' packets sent');
        }
    }, 100);
}

function stopAttack() {
    running = false;
    clearInterval(timer);
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('statStatus').textContent = 'STOPPED';
    document.getElementById('statStatus').className = 'stat-value stat-done';
    setStatus('done', 'ATTACK STOPPED');
    addLog('err', 'STOPPED', 'Attack stopped — ' + sent + ' packets sent');
}

function stopDone(total) {
    running = false;
    clearInterval(timer);
    var secs = ((Date.now() - startTime) / 1000).toFixed(1);
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('statStatus').textContent = 'DONE';
    document.getElementById('statStatus').className = 'stat-value stat-done';
    setStatus('done', 'ATTACK COMPLETE — ' + total + ' PACKETS SENT');
    var t = new Date().toLocaleTimeString('en-GB');
var logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
logs.push({ type: 'dos', time: t, target: ip + ':' + port, details: packets + ' packets sent in ' + secs + 's', packets: packets });
localStorage.setItem('netwolf_logs', JSON.stringify(logs));
    addLog('ok', 'COMPLETE', total + ' packets sent in ' + secs + 's');
}