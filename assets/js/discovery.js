function addHostRow(host) {
    var body = document.getElementById('resultsBody');
    var empty = body.querySelector('.no-results');
    if (empty) empty.remove();

    var row = document.createElement('div');
    row.className = 'result-row discovery-row';
    row.style.cursor = 'pointer';
    row.title = 'Click to scan this host';
    row.innerHTML =
        '<span>' + host.ip + '</span>' +
        '<span>' + (host.hostname || '—') + '</span>' +
        '<span>' + (host.mac || '—') + '</span>' +
        '<span>' + (host.manufacturer || '—') + '</span>' +
        '<span>' + (host.os || '—') + '</span>' +
        '<span>' + (host.device_type || '—') + '</span>' +
        '<span class="status-' + (host.status === 'active' ? 'open' : 'closed') + '">' + (host.status || 'unknown').toUpperCase() + '</span>';

    row.addEventListener('click', function() {
        window.location.href = 'scanner.html?ip=' + encodeURIComponent(host.ip);
    });
    body.appendChild(row);
}

function startDiscovery() {
    var mode = document.getElementById('discoverMode').value;
    var network = document.getElementById('networkCidr').value.trim();
    var enhanced = document.getElementById('enhancedDiscovery').checked;
    var error = document.getElementById('errorMsg');
    var statusBar = document.getElementById('statusBar');
    var statusText = document.getElementById('statusText');
    var btn = document.getElementById('discoverBtn');
    var body = document.getElementById('resultsBody');

    error.classList.add('hidden');
    body.innerHTML = '';
    statusBar.classList.remove('hidden');
    statusText.textContent = 'DISCOVERING NETWORK (' + mode.toUpperCase() + ')...';
    btn.disabled = true;

    var payload = { mode: mode, enhanced: enhanced };
    if (network) payload.network = network;

    postDiscover(payload)
    .then(function(res) {
        var data = res.data;
        if (!res.ok || !data.success) {
            statusText.textContent = 'ERROR: ' + (data.message || 'Discovery failed');
            btn.disabled = false;
            return;
        }

        var hosts = data.hosts || [];
        var active = hosts.filter(function(h) { return h.status === 'active'; });

        if (active.length === 0) {
            body.innerHTML = '<p class="no-results">Discovery complete — no active hosts found.</p>';
        } else {
            active.sort(function(a, b) {
                var pa = a.ip.split('.').map(Number);
                var pb = b.ip.split('.').map(Number);
                for (var i = 0; i < 4; i++) {
                    if (pa[i] !== pb[i]) return pa[i] - pb[i];
                }
                return 0;
            });
            for (var i = 0; i < active.length; i++) {
                addHostRow(active[i]);
            }
        }

        statusText.textContent = 'DISCOVERY COMPLETE — ' + active.length + ' ACTIVE HOST(S)';
        btn.disabled = false;

        var time = new Date().toLocaleTimeString('en-GB');
        var logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
        logs.push({ type: 'scan', time: time, target: mode, details: active.length + ' hosts discovered' });
        localStorage.setItem('netwolf_logs', JSON.stringify(logs));
    })
    .catch(function() {
        statusText.textContent = 'CONNECTION ERROR — IS FLASK RUNNING?';
        btn.disabled = false;
    });
}

function loadNetworkInfo() {
    getNetworkInfo()
    .then(function(res) {
        if (res.ok && res.data.success) {
            var el = document.getElementById('networkHint');
            if (el) {
                el.textContent = 'Local network: ' + res.data.localNetwork + ' | Router: ' + (res.data.routerIp || 'unknown');
            }
            var cidr = document.getElementById('networkCidr');
            if (cidr && !cidr.value && res.data.localNetwork) {
                cidr.placeholder = res.data.localNetwork;
            }
        }
    })
    .catch(function() {});
}

document.addEventListener('DOMContentLoaded', loadNetworkInfo);
