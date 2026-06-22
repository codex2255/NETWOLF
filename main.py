import socket
import threading
import time
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import ipaddress

from utils.attack import udp_flood, tcp_flood, icmp_flood, http_flood, smurf_attack, network_wide_udp_flood, broadcast_udp_flood, dns_amplification_attack
from utils.scanner import port_scan, service_detection, os_fingerprint
from utils.discovery import network_discovery, ping_sweep, arp_scan, get_router_ip, discover_gateway_and_scan, smart_discovery, get_all_network_interfaces

# --- HELPER LOGIC ---

def is_target_allowed(target):
    try:
        if not target: return False
        t_addr = ipaddress.ip_address(target)
        if t_addr.is_loopback: return True
        hostname = socket.gethostname()
        l_ip = socket.gethostbyname(hostname)
        if l_ip == '127.0.0.1':
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 1))
                l_ip = s.getsockname()[0]
            except: pass
            finally: s.close()
        l_net = ipaddress.ip_network(f"{'.'.join(l_ip.split('.')[:3])}.0/24", strict=False)
        return t_addr in l_net
    except: return False

def is_range_allowed(range_str):
    try:
        if not range_str: return False
        t_net = ipaddress.ip_network(range_str, strict=False)
        hostname = socket.gethostname()
        l_ip = socket.gethostbyname(hostname)
        if l_ip == '127.0.0.1':
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 1))
                l_ip = s.getsockname()[0]
            except: pass
            finally: s.close()
        l_net = ipaddress.ip_network(f"{'.'.join(l_ip.split('.')[:3])}.0/24", strict=False)
        return l_net.overlaps(t_net)
    except: return False

class NetWolf:
    def __init__(self):
        self.scan_results = []
        self.attack_log = []
        self.discovered_hosts = []
        self.running = True

    def run_cli(self):
        while self.running:
            print("\n[ NETWOLF CLI ]")
            print("1. Discovery | 2. Port Scan | 3. Service Detect | 4. OS Detect | 5. DoS | 8. Web GUI | 9. Exit")
            choice = input("> ")
            if choice == '1': self.network_discovery_menu()
            elif choice == '2': self.port_scanner_menu()
            elif choice == '3': self.service_detection_menu()
            elif choice == '4': self.os_fingerprint_menu()
            elif choice == '5': self.attack_menu()
            elif choice == '8': start_web_server()
            elif choice == '9': self.running = False

    def network_discovery_menu(self):
        print("1. Auto | 2. Manual | 3. Ping | 4. ARP | 5. Router | 6. Interfaces | 7. Smart")
        c = input("> ")
        net = self.get_network_range() if c == '1' else input("Range: ")
        if c == '1': results = network_discovery(net, enhanced=True)
        elif c == '2': results = network_discovery(net, enhanced=True)
        elif c == '3': results = ping_sweep(net)
        elif c == '4': results = arp_scan(net)
        elif c == '5': results, _ = discover_gateway_and_scan()
        elif c == '6':
            results = []
            for iface in get_all_network_interfaces():
                devs = ping_sweep(iface['network'])
                if devs: results.extend(devs)
        elif c == '7': results = smart_discovery()
        print(f"[*] Found {len(results or [])} devices.")

    def get_network_range(self):
        hostname = socket.gethostname()
        l_ip = socket.gethostbyname(hostname)
        return f"{'.'.join(l_ip.split('.')[:3])}.0/24"

    def port_scanner_menu(self):
        t = input("Target: ")
        s = int(input("Start: "))
        e = int(input("End: "))
        port_scan(t, s, e)

    def service_detection_menu(self):
        t = input("Target: ")
        p = input("Ports (comma): ")
        service_detection(t, [int(x) for x in p.split(',')])

    def os_fingerprint_menu(self):
        t = input("Target: ")
        print(os_fingerprint(t))

    def attack_menu(self):
        print("1. UDP | 2. SYN | 3. ICMP | 4. HTTP | 5. Smurf | 6. Network | 7. Broadcast | 8. DNS")
        c = input("> ")
        t = input("Target: ")
        d = int(input("Duration: "))
        thr = int(input("Threads: "))
        p = int(input("Port: ")) if c in ['1','2','6','7'] else 80
        if c == '1': udp_flood(t, p, d, thr)
        elif c == '2': tcp_flood(t, p, d, thr)
        elif c == '3': icmp_flood(t, d, thr)
        elif c == '4': http_flood(t, d, thr)
        elif c == '5': smurf_attack(t, d, thr)
        elif c == '6': network_wide_udp_flood(t, p, d, thr)
        elif c == '7': broadcast_udp_flood(t, p, d, thr)
        elif c == '8': dns_amplification_attack(t, d, thr)

# --- WEB SERVER ---

app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index(): return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/pages/<path:filename>')
def pages(filename): return send_from_directory(os.path.join(BASE_DIR, 'pages'), filename)

@app.route('/assets/<path:filename>')
def assets(filename): return send_from_directory(os.path.join(BASE_DIR, 'assets'), filename)

@app.route('/api/health')
def api_health(): return jsonify({'status': 'online', 'version': '1.0.4-PRO'})

@app.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.json
    ip = data.get('ip')
    if not is_target_allowed(ip): return jsonify({'success': False, 'message': 'Restricted'}), 403
    res = port_scan(ip, int(data.get('portStart', 1)), int(data.get('portEnd', 1024)), scan_udp=data.get('scan_udp', False))
    return jsonify({'success': True, 'results': res})

@app.route('/api/discovery', methods=['POST'])
def api_discovery():
    data = request.json
    m = data.get('method', '1')
    r = data.get('range')
    if r and not is_range_allowed(r): return jsonify({'success': False, 'message': 'Restricted'}), 403
    res = []
    if m == '1': res = network_discovery(f"{'.'.join(socket.gethostbyname(socket.gethostname()).split('.')[:3])}.0/24", enhanced=True)
    elif m == '2': res = network_discovery(r, enhanced=True)
    elif m == '3': res = ping_sweep(r)
    elif m == '4': res = arp_scan(r)
    elif m == '5': res, _ = discover_gateway_and_scan()
    elif m == '6':
        for iface in get_all_network_interfaces():
            d = ping_sweep(iface['network']); 
            if d: res.extend(d)
    elif m == '7': res = smart_discovery()
    return jsonify({'success': True, 'results': res or []})

@app.route('/api/os_detect', methods=['POST'])
def api_os():
    ip = request.json.get('ip')
    if not is_target_allowed(ip): return jsonify({'success': False, 'message': 'Restricted'}), 403
    res = os_fingerprint(ip)
    return jsonify({'success': True, 'os': res['os'], 'ttl': res['ttl']})

@app.route('/api/service_detect', methods=['POST'])
def api_service():
    data = request.json
    ip = data.get('ip')
    if not is_target_allowed(ip): return jsonify({'success': False, 'message': 'Restricted'}), 403
    res = service_detection(ip, [int(p) for p in data.get('ports', [])])
    return jsonify({'success': True, 'results': res})

@app.route('/api/attack', methods=['POST'])
def api_dos():
    data = request.json
    t = data.get('ip')
    c = data.get('type', '1')
    d = int(data.get('duration', 10))
    thr = int(data.get('threads', 10))
    p = int(data.get('port', 80))
    if c in ['6', '7']:
        if not is_range_allowed(t): return jsonify({'success': False, 'message': 'Restricted'}), 403
    else:
        if not is_target_allowed(t): return jsonify({'success': False, 'message': 'Restricted'}), 403
    def run():
        if c == '1': udp_flood(t, p, d, thr)
        elif c == '2': tcp_flood(t, p, d, thr)
        elif c == '3': icmp_flood(t, d, thr)
        elif c == '4': http_flood(t, d, thr)
        elif c == '5': smurf_attack(t, d, thr)
        elif c == '6': network_wide_udp_flood(t, p, d, thr)
        elif c == '7': broadcast_udp_flood(t, p, d, thr)
        elif c == '8': dns_amplification_attack(t, d, thr)
    threading.Thread(target=run, daemon=True).start()
    return jsonify({'success': True, 'message': 'Attack Initiated'})

def start_web_server():
    app.run(debug=False, port=5555, host='0.0.0.0')

if __name__ == "__main__":
    if "--gui" in os.sys.argv: start_web_server()
    else:
        print("1. CLI | 2. GUI")
        if input("> ") == '2': start_web_server()
        else: NetWolf().run_cli()
