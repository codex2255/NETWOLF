async function runDetection() {
    var ip = document.getElementById('targetIP').value.trim();
    var ports = document.getElementById('targetPorts').value.trim();
    var osResults = document.getElementById('osResults');
    var serviceResults = document.getElementById('serviceResults');
    var statusText = document.getElementById('statusText');
    var statusBar = document.getElementById('statusBar');
    var btn = document.getElementById('detectBtn');

    if (!ip) {
        alert("Please enter a target IP");
        return;
    }

    osResults.innerHTML = '<p class="status-text">Analyzing OS...</p>';
    serviceResults.innerHTML = '<p class="status-text">Detecting services...</p>';
    statusBar.classList.remove('hidden');
    statusText.textContent = 'ANALYZING ' + ip + '...';
    btn.disabled = true;

    try {
        // OS Fingerprint
        const osPromise = fetch('/os_detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip: ip })
        }).then(r => r.json());

        // Service Detection (if ports provided)
        let servicePromise = Promise.resolve({ success: true, results: [] });
        if (ports) {
            servicePromise = fetch('/service_detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ip: ip, ports: ports.split(',').map(p => parseInt(p.trim())) })
            }).then(r => r.json());
        }

        const [osData, serviceData] = await Promise.all([osPromise, servicePromise]);

        if (osData.success) {
            osResults.innerHTML = `
                <div style="margin-bottom: 10px;"><span style="color: #ff3366;">OS TYPE:</span> ${osData.os}</div>
                <div style="margin-bottom: 10px;"><span style="color: #ff3366;">TTL:</span> ${osData.ttl}</div>
                <div style="font-size: 0.8em; color: #888;">Analysis based on TCP/IP stack response.</div>
            `;
        } else {
            osResults.innerHTML = `<p class="error-msg">OS Detection Failed</p>`;
        }

        if (serviceData.success && serviceData.results.length > 0) {
            serviceResults.innerHTML = '';
            serviceData.results.forEach(s => {
                var div = document.createElement('div');
                div.style.marginBottom = '10px';
                div.style.borderBottom = '1px solid #333';
                div.style.paddingBottom = '5px';
                div.innerHTML = `
                    <div style="color: #00ff9d;">PORT ${s.port} (${s.service})</div>
                    <div style="font-size: 0.85em; font-family: monospace; color: #aaa;">${s.banner || 'No banner captured'}</div>
                `;
                serviceResults.appendChild(div);
            });
        } else if (ports) {
            serviceResults.innerHTML = `<p class="no-results">No services found on specified ports.</p>`;
        } else {
            serviceResults.innerHTML = `<p class="no-results">Enter ports above to run service detection.</p>`;
        }

        statusText.textContent = 'ANALYSIS COMPLETE';
    } catch (err) {
        statusText.textContent = 'ERROR: ' + err.message;
    } finally {
        btn.disabled = false;
    }
}
