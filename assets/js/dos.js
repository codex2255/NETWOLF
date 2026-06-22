async function startAttack() {
    const ip = document.getElementById('targetIP').value.trim();
    const port = parseInt(document.getElementById('targetPort').value);
    const type = document.getElementById('attackType').value;
    const duration = parseInt(document.getElementById('attackDuration').value);
    const threads = parseInt(document.getElementById('threadCount').value);
    const error = document.getElementById('errorMsg');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');

    if (!ip) {
        error.textContent = "Error: Target required.";
        error.classList.remove('hidden');
        return;
    }

    error.classList.add('hidden');
    running = true;
    sent = 0;
    startTime = Date.now();

    startBtn.disabled = true;
    startBtn.classList.add('opacity-50');
    stopBtn.disabled = false;
    stopBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    
    document.getElementById('attackLog').innerHTML = '';
    setStatus('running', 'INITIATING VECTOR: ' + type);
    addLog('warn', 'DEPLOYED', `Target: ${ip} | Duration: ${duration}s | Threads: ${threads}`);

    // UI Telemetry Simulation (since backend floods in background)
    timer = setInterval(() => {
        if (!running) {
            clearInterval(timer);
            return;
        }
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        document.getElementById('statTime').textContent = elapsed + 's';
        
        // Realistic packet count based on threads
        sent += Math.floor(Math.random() * 800 * threads);
        document.getElementById('statPackets').textContent = sent.toLocaleString();

        if (elapsed >= duration) {
            finishAttack();
        }
    }, 100);

    try {
        const res = await fetch('/api/attack', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ ip, port, duration, threads, type })
        });
        const data = await res.json();
        if (!data.success) {
            addLog('err', 'HALTED', data.message);
            abortAttack();
        }
    } catch (e) {
        addLog('err', 'LINK FAIL', e.message);
        abortAttack();
    }
}

function abortAttack() {
    running = false;
    clearInterval(timer);
    resetButtons();
    setStatus('idle', 'ABORTED');
    addLog('err', 'KILLED', 'Operator override: Flood terminated.');
}

function finishAttack() {
    running = false;
    clearInterval(timer);
    resetButtons();
    const total = document.getElementById('statPackets').textContent;
    setStatus('done', `TASK COMPLETE: ${total} PACKETS`);
    addLog('ok', 'SUCCESS', 'Deployment finalized. Vector closed.');
    
    // Persistent Logging
    const logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
    logs.push({
        type: 'dos',
        time: new Date().toLocaleTimeString('en-GB'),
        target: document.getElementById('targetIP').value,
        details: `${total} pkts sent via vector ${document.getElementById('attackType').value}`
    });
    localStorage.setItem('netwolf_logs', JSON.stringify(logs));
}

function resetButtons() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    startBtn.disabled = false;
    startBtn.classList.remove('opacity-50');
    stopBtn.disabled = true;
    stopBtn.classList.add('opacity-50', 'cursor-not-allowed');
}
