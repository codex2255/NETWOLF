async function startDiscovery() {
    var range = document.getElementById('networkRange').value.trim();
    var resultsBody = document.getElementById('resultsBody');
    var statusText = document.getElementById('statusText');
    var statusBar = document.getElementById('statusBar');
    var btn = document.getElementById('discoverBtn');

    if (!range) {
        document.getElementById('errorMsg').classList.remove('hidden');
        return;
    }

    document.getElementById('errorMsg').classList.add('hidden');
    resultsBody.innerHTML = '';
    statusBar.classList.remove('hidden');
    statusText.textContent = 'DISCOVERING DEVICES ON ' + range + '...';
    btn.disabled = true;

    try {
        const response = await fetch('/discovery', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ range: range })
        });
        const data = await response.json();

        if (data.success && data.results) {
            if (data.results.length === 0) {
                resultsBody.innerHTML = '<p class="no-results">No devices found on this range.</p>';
            } else {
                data.results.forEach(host => {
                    addDeviceCard(host);
                });
            }
            statusText.textContent = 'DISCOVERY COMPLETE — ' + data.results.length + ' DEVICES FOUND';
        } else {
            statusText.textContent = 'DISCOVERY FAILED: ' + (data.message || 'Unknown error');
        }
    } catch (err) {
        statusText.textContent = 'ERROR: ' + err.message;
    } finally {
        btn.disabled = false;
    }
}

async function autoDiscover() {
    var statusText = document.getElementById('statusText');
    var statusBar = document.getElementById('statusBar');
    var resultsBody = document.getElementById('resultsBody');

    resultsBody.innerHTML = '';
    statusBar.classList.remove('hidden');
    statusText.textContent = 'AUTO-DETECTING NETWORK...';

    try {
        const response = await fetch('/discovery/auto', { method: 'POST' });
        const data = await response.json();

        if (data.success && data.results) {
            document.getElementById('networkRange').value = data.network;
            data.results.forEach(host => {
                addDeviceCard(host);
            });
            statusText.textContent = 'DISCOVERY COMPLETE — ' + data.results.length + ' DEVICES FOUND';
        } else {
            statusText.textContent = 'AUTO-DETECTION FAILED';
        }
    } catch (err) {
        statusText.textContent = 'ERROR: ' + err.message;
    }
}

function addDeviceCard(host) {
    var resultsBody = document.getElementById('resultsBody');
    var noResults = resultsBody.querySelector('.no-results');
    if (noResults) noResults.remove();

    var card = document.createElement('div');
    card.className = 'device-card';
    card.innerHTML = `
        <div class="device-ip">${host.ip}</div>
        <div class="device-type">${host.device_type || 'Generic Device'}</div>
        <div class="device-os">${host.os || 'Unknown OS'}</div>
        <div class="device-mac" style="font-size: 0.8em; color: #888;">${host.mac || 'N/A'}</div>
    `;
    resultsBody.appendChild(card);
}
