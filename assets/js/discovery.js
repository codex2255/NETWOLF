async function startDiscovery() {
    var range = document.getElementById('networkRange').value.trim();
    var method = document.getElementById('discoveryMethod').value;
    var resultsBody = document.getElementById('resultsBody');
    var statusText = document.getElementById('statusText');
    var statusBar = document.getElementById('statusBar');
    var btn = document.getElementById('discoverBtn');

    if (!range && method !== 'smart' && method !== 'interfaces' && method !== 'gateway') {
        alert("Please enter a target range or select an automatic method.");
        return;
    }

    resultsBody.innerHTML = '<div class="col-span-full py-12 flex flex-col items-center gap-4 opacity-50"><div class="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin"></div><div class="font-mono text-xs uppercase tracking-widest">Executing Topology Scan...</div></div>';
    statusBar.classList.remove('hidden');
    statusText.textContent = `RUNNING ${method.toUpperCase()} DISCOVERY...`;
    btn.disabled = true;

    try {
        const response = await fetch('/discovery', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ range: range, method: method })
        });
        const data = await response.json();

        if (data.success && data.results) {
            resultsBody.innerHTML = '';
            if (data.results.length === 0) {
                resultsBody.innerHTML = '<p class="text-dim text-sm font-mono col-span-full py-12 text-center border border-dashed border-white/10 rounded-xl">No active nodes identified in this segment.</p>';
            } else {
                data.results.forEach(host => {
                    addDeviceCard(host);
                });
            }
            statusText.textContent = 'DISCOVERY COMPLETE — ' + data.results.length + ' NODES MAPPED';
        } else {
            statusText.textContent = 'ERROR: ' + (data.message || 'Transmission failure');
        }
    } catch (err) {
        statusText.textContent = 'CRITICAL ERROR: ' + err.message;
    } finally {
        btn.disabled = false;
    }
}

async function autoDetectNetwork() {
    try {
        const res = await fetch('/discovery/auto', { method: 'POST' });
        const data = await res.json();
        if (data.network) {
            document.getElementById('networkRange').value = data.network;
        }
    } catch (e) {}
}

function addDeviceCard(host) {
    var resultsBody = document.getElementById('resultsBody');
    var card = document.createElement('div');
    card.className = 'pro-card animate-fade border-white/5 hover:border-accent/40 transition-all cursor-pointer group hover:bg-accent/[0.02]';
    
    let typeIcon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6" y2="6"/><line x1="6" y1="18" x2="6" y2="18"/></svg>';
    if (host.device_type?.toLowerCase().includes('router')) typeIcon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>';
    
    card.innerHTML = `
        <div class="flex justify-between items-start mb-6">
            <div class="p-2.5 bg-accent-dim rounded-xl text-accent group-hover:shadow-[0_0_15px_rgba(0,255,163,0.3)] transition-all">
                ${typeIcon}
            </div>
            <div class="flex flex-col items-end">
                <span class="text-[9px] font-mono text-dim uppercase tracking-widest mb-1">Status</span>
                <span class="flex items-center gap-1.5 text-[10px] font-bold text-accent uppercase">
                    <span class="w-1.5 h-1.5 bg-accent rounded-full animate-pulse"></span>
                    Online
                </span>
            </div>
        </div>
        <div class="text-xl font-bold font-mono text-white mb-1 tracking-tight">${host.ip}</div>
        <div class="text-[11px] font-medium text-dim mb-6 flex items-center gap-2">
            <span class="w-1 h-1 bg-white/20 rounded-full"></span>
            ${host.os || 'OS Fingerprint Unknown'}
        </div>
        <div class="space-y-2 pt-4 border-t border-white/5">
            <div class="flex justify-between text-[10px] font-mono"><span class="text-dim uppercase">MAC Physical</span> <span class="text-white/60">${host.mac || 'REDACTED'}</span></div>
            <div class="flex justify-between text-[10px] font-mono"><span class="text-dim uppercase">Manufacturer</span> <span class="text-white/60 truncate max-w-[120px]">${host.manufacturer || 'Generic'}</span></div>
        </div>
    `;
    resultsBody.appendChild(card);
}

document.addEventListener('DOMContentLoaded', autoDetectNetwork);
