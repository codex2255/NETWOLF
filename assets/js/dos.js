let attackRunning  = false;
let attackInterval = null;
let timerInterval  = null;
let packetsSent    = 0;
let startTime      = null;

function isValidIP(ip) {
    const pattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!pattern.test(ip)) return false;
    return ip.split('.').every(o => parseInt(o) >= 0 && parseInt(o) <= 255);
}

function isValidPort(port) {
    return !isNaN(port) && port >= 1 && port <= 65535;
}

function addLog(type, label, message) {
    const log   = document.getElementById('attackLog');
    const empty = log.querySelector('.log-empty');
    if (empty) empty.remove();

    const time = new Date().toLocaleTimeString('en-GB');
    const line = document.createElement('p');
    line.classList.add('log-line');
    line.innerHTML = `[${time}] <span class="log-${type}">${label}</span> — ${message}`;
    log.appendChild(line);
    log.scrollTop = log.scrollHeight;
}

function setStatus(state, message) {
    const dot  = document.querySelector('.status-dot-dos');
    const text = document.getElementById('statusText');
    dot.className    = `status-dot-dos ${state}`;
    text.textContent = message;
    text.style.color = state === 'running' ? '#ff2222' : state === 'done' ? '#22ff66' : '#555';
}

function setStatStatus(state, label) {
    const el     = document.getElementById('statStatus');
    el.className = `stat-value stat-${state}`;
    el.textContent = label;
}

function resetStats() {
    document.getElementById('statPackets').textContent = '0';
    document.getElementById('statPPS').textContent     = '0';
    document.getElementById('statTime').textContent    = '0s';
    setStatStatus('idle', 'IDLE');
}

function startAttack() {
    const ip      = document.getElementById('targetIP').value.trim();
    const port    = parseInt(document.getElementById('targetPort').value);
    const packets = parseInt(document.getElementById('packetCount').value);
    const type    = document.getElementById('attackType').value;
    const threads = parseInt(document.getElementById('threadCount').value) || 4;
    const errorMsg = document.getElementById('errorMsg');

    if (!isValidIP(ip) || !isValidPort(port) || isNaN(packets) || packets < 1) {
        errorMsg.classList.remove('hidden');
        return;
    }

    errorMsg.classList.add('hidden');
    attackRunning = true;
    packetsSent   = 0;
    startTime     = Date.now();

    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled  = false;

    setStatus('running', `ATTACKING ${ip}:${port} — ${type.replace('_', ' ')} — ${threads} THREADS`);
    setStatStatus('running', 'RUNNING');

    document.getElementById('attackLog').innerHTML = '';
    addLog('warn', 'INITIATED', `Attack started on ${ip}:${port} — ${packets} packets — ${type}`);

    const batchSize  = threads * 2;
    const intervalMs = 100;

    attackInterval = setInterval(() => {
        if (!attackRunning || packetsSent >= packets) {
            finishAttack(packets);
            return;
        }

        const remaining = packets - packetsSent;
        const batch     = Math.min(batchSize, remaining);
        packetsSent    += batch;

        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        const pps     = Math.floor(packetsSent / (elapsed > 0 ? elapsed : 1));

        document.getElementById('statPackets').textContent = packetsSent;
        document.getElementById('statPPS').textContent     = pps;
        document.getElementById('statTime').textContent    = `${elapsed}s`;

        if (packetsSent % 200 === 0 || packetsSent >= packets) {
            addLog('ok', 'SENT', `${packetsSent}/${packets} packets sent to ${ip}:${port}`);
        }

    }, intervalMs);
}

function stopAttack() {
    attackRunning = false;
    clearInterval(attackInterval);
    clearInterval(timerInterval);

    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled  = true;

    setStatus('done', 'ATTACK STOPPED BY USER');
    setStatStatus('done', 'STOPPED');
    addLog('err', 'STOPPED', `Attack manually stopped — ${packetsSent} packets sent`);
}

function finishAttack(total) {
    attackRunning = false;
    clearInterval(attackInterval);
    clearInterval(timerInterval);

    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled  = true;

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

    setStatus('done', `ATTACK COMPLETE — ${total} PACKETS SENT IN ${elapsed}s`);
    setStatStatus('done', 'DONE');
    addLog('ok', 'COMPLETE', `Attack finished — ${total} packets sent in ${elapsed}s`);
}