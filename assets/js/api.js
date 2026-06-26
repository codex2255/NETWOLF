var API_BASE = window.location.origin;

function apiFetch(path, options) {
    return fetch(API_BASE + path, options).then(function(res) {
        return res.json().then(function(data) {
            return { ok: res.ok, status: res.status, data: data };
        });
    });
}

function getHealth() {
    return apiFetch('/health');
}

function getNetworkInfo() {
    return apiFetch('/network/info');
}

function postScan(body) {
    return apiFetch('/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
}

function postDiscover(body) {
    return apiFetch('/discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
}

function postDos(body) {
    return apiFetch('/dos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
}

function getReports() {
    return apiFetch('/reports');
}

function getReport(id) {
    return apiFetch('/reports/' + encodeURIComponent(id));
}

function checkNavbarHealth() {
    var dot = document.querySelector('.status-dot');
    var text = document.querySelector('.status-text');
    if (!dot && !text) return;

    getHealth()
    .then(function(res) {
        if (res.ok) {
            if (dot) dot.style.backgroundColor = '#22ff66';
            if (text) { text.textContent = 'SYSTEM ONLINE'; text.style.color = '#22ff66'; }
        } else {
            if (dot) dot.style.backgroundColor = '#ff3333';
            if (text) { text.textContent = 'SYSTEM OFFLINE'; text.style.color = '#ff3333'; }
        }
    })
    .catch(function() {
        if (dot) dot.style.backgroundColor = '#ff3333';
        if (text) { text.textContent = 'SYSTEM OFFLINE'; text.style.color = '#ff3333'; }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('navbar')) {
        checkNavbarHealth();
    }
});
