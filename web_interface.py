from flask import Flask, render_template_string, request, jsonify
import threading
import json
from utils.scanner import port_scan, service_detection
from utils.attack import udp_flood, tcp_flood

app = Flask(__name__)
scan_results_store = {}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NetWolf - Network Security Suite</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Courier New', monospace; background: #0a0e27; color: #00ff9d; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; padding: 20px; border-bottom: 2px solid #00ff9d; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .card { background: #0f1235; border: 1px solid #00ff9d; border-radius: 10px; padding: 20px; }
        .card h2 { margin-bottom: 15px; color: #ff3366; }
        input, select { width: 100%; padding: 10px; margin: 10px 0; background: #1a1f4e; border: 1px solid #00ff9d; color: #00ff9d; }
        button { background: #ff3366; color: white; padding: 10px 20px; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background: #cc0044; }
        .results { background: #0a0e27; padding: 15px; margin-top: 15px; border-left: 3px solid #00ff9d; }
        .open-port { color: #00ff9d; }
        .closed-port { color: #ff3366; }
        .log { background: #0f1235; padding: 10px; margin: 5px 0; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐺 NETWOLF v1.0</h1>
            <p>Ethical Network Testing Suite</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>🔍 Port Scanner</h2>
                <input type="text" id="scan_target" placeholder="Target IP">
                <input type="number" id="start_port" placeholder="Start Port" value="1">
                <input type="number" id="end_port" placeholder="End Port" value="1000">
                <button onclick="runScan()">Start Scan</button>
                <div id="scan_results" class="results"></div>
            </div>
            
            <div class="card">
                <h2>💥 DOS Attack Module</h2>
                <input type="text" id="attack_target" placeholder="Target IP">
                <input type="number" id="attack_port" placeholder="Port">
                <select id="attack_type">
                    <option value="udp">UDP Flood</option>
                    <option value="tcp">TCP Flood (SYN)</option>
                </select>
                <input type="number" id="duration" placeholder="Duration (seconds)" value="10">
                <button onclick="runAttack()" style="background: #ff3366;">⚠️ Execute Attack</button>
                <div id="attack_status" class="results"></div>
            </div>
        </div>
        
        <div class="card" style="margin-top: 20px;">
            <h2>📋 Service Detection</h2>
            <input type="text" id="service_target" placeholder="Target IP">
            <input type="text" id="service_ports" placeholder="Ports (comma: 80,443,22)">
            <button onclick="detectServices()">Detect Services</button>
            <div id="service_results" class="results"></div>
        </div>
    </div>
    
    <script>
        async function runScan() {
            const target = document.getElementById('scan_target').value;
            const start = document.getElementById('start_port').value;
            const end = document.getElementById('end_port').value;
            const resultsDiv = document.getElementById('scan_results');
            
            resultsDiv.innerHTML = '<div>[*] Scanning in progress...</div>';
            
            const response = await fetch('/api/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({target: target, start: parseInt(start), end: parseInt(end)})
            });
            
            const data = await response.json();
            if(data.results) {
                let html = '<strong>Open Ports:</strong><br>';
                data.results.forEach(r => {
                    html += `<div class="open-port">✓ Port ${r.port}: OPEN</div>`;
                });
                resultsDiv.innerHTML = html;
            }
        }
        
        async function runAttack() {
            const target = document.getElementById('attack_target').value;
            const port = document.getElementById('attack_port').value;
            const atype = document.getElementById('attack_type').value;
            const duration = document.getElementById('duration').value;
            const statusDiv = document.getElementById('attack_status');
            
            if(!confirm('WARNING: This will send attack traffic. Type "ETHICAL USE ONLY" to confirm')) {
                statusDiv.innerHTML = '<div>[-] Attack cancelled</div>';
                return;
            }
            
            statusDiv.innerHTML = '<div>[!] Attack in progress...</div>';
            
            const response = await fetch('/api/attack', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({target: target, port: parseInt(port), type: atype, duration: parseInt(duration)})
            });
            
            const data = await response.json();
            statusDiv.innerHTML = `<div>[+] ${data.message}</div>`;
        }
        
        async function detectServices() {
            const target = document.getElementById('service_target').value;
            const ports = document.getElementById('service_ports').value;
            const resultsDiv = document.getElementById('service_results');
            
            resultsDiv.innerHTML = '<div>[*] Detecting services...</div>';
            
            const response = await fetch('/api/services', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({target: target, ports: ports.split(',').map(p => parseInt(p.trim()))})
            });
            
            const data = await response.json();
            if(data.results) {
                let html = '<strong>Detected Services:</strong><br>';
                data.results.forEach(r => {
                    html += `<div class="log">Port ${r.port}: ${r.service}</div>`;
                });
                resultsDiv.innerHTML = html;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.json
    results = port_scan(data['target'], data['start'], data['end'])
    return jsonify({'results': results})

@app.route('/api/attack', methods=['POST'])
def api_attack():
    data = request.json
    
    def attack_thread():
        if data['type'] == 'udp':
            udp_flood(data['target'], data['port'], data['duration'], 10)
        elif data['type'] == 'tcp':
            tcp_flood(data['target'], data['port'], data['duration'], 10)
    
    thread = threading.Thread(target=attack_thread)
    thread.start()
    
    return jsonify({'message': f"Attack started on {data['target']} for {data['duration']} seconds"})

@app.route('/api/services', methods=['POST'])
def api_services():
    data = request.json
    results = service_detection(data['target'], data['ports'])
    return jsonify({'results': results})