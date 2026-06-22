function updateDashboardStats() {
    const logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
    const lastScan = JSON.parse(localStorage.getItem('netwolf_last_scan') || '{"results":[]}');
    
    const scansCount = logs.filter(l => l.type === 'scan').length;
    const openPortsCount = lastScan.results.filter(r => r.status === 'open').length;
    const dosCount = logs.filter(l => l.type === 'dos').length;

    countUp('scansRun', scansCount);
    countUp('openPorts', openPortsCount);
}

function countUp(id, target) {
    var el = document.getElementById(id);
    var count = 0;
    var step = Math.ceil(target / 50);

    var timer = setInterval(function() {
        count += step;
        if (count >= target) {
            count = target;
            clearInterval(timer);
        }
        el.textContent = count;
    }, 30);
}

countUp('scansRun', scansRun);
countUp('openPorts', openPorts);
countUp('vulnCount', vulnCount);

var logs = [
    { time: '14:22:01', type: 'ok', label: 'SUCCESS', msg: 'Port scan completed on 192.168.1.1' },
    { time: '14:20:44', type: 'warn', label: 'WARNING', msg: 'Port 8080 open on target host' },
    { time: '14:18:30', type: 'err', label: 'ALERT', msg: 'Vulnerability detected on port 443' },
    { time: '14:15:12', type: 'ok', label: 'SUCCESS', msg: 'DoS stress test completed' },
    { time: '14:10:05', type: 'ok', label: 'SUCCESS', msg: 'Session initialized' }
];

function showLogs() {
    const logs = JSON.parse(localStorage.getItem('netwolf_logs') || '[]');
    var container = document.getElementById('activityLog');
    
    if (logs.length === 0) {
        container.innerHTML = '<div class="opacity-20 italic py-4">No recent activity detected.</div>';
        return;
    }

    container.innerHTML = '';
    // Show last 10 logs
    const recentLogs = logs.slice(-10).reverse();
    
    recentLogs.forEach(log => {
        var div = document.createElement('div');
        div.className = 'flex gap-4 py-2 border-b border-white/5 last:border-0';
        const accent = log.type === 'scan' ? 'text-accent' : 'text-danger';
        div.innerHTML = `
            <span class="text-white/20 font-mono text-[10px]">${log.time}</span>
            <span class="${accent} font-bold uppercase tracking-tighter w-12 text-[10px]">${log.type}</span>
            <span class="text-white/60 truncate flex-1">${log.details}</span>
        `;
        container.appendChild(div);
    });
}

updateDashboardStats();
showLogs();
