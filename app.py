import socket
import threading
import time
import ipaddress
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from utils.attack import udp_flood, tcp_flood, http_flood
from utils.scanner import port_scan
from utils.discovery import network_discovery, get_local_network, get_router_ip

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCANS_DIR = os.path.join(BASE_DIR, 'data', 'scans')
DEMO_SCAN = os.path.join(BASE_DIR, 'scan_192.168.20.1_20260616_144357.json')


def ensure_scans_dir():
    os.makedirs(SCANS_DIR, exist_ok=True)
    existing = [f for f in os.listdir(SCANS_DIR) if f.endswith('.json')]
    if not existing and os.path.exists(DEMO_SCAN):
        with open(DEMO_SCAN, 'r', encoding='utf-8') as f:
            demo_results = json.load(f)
        sample = {
            'ip': '192.168.20.1',
            'time': '14:43:57',
            'results': demo_results if isinstance(demo_results, list) else demo_results.get('results', [])
        }
        with open(os.path.join(SCANS_DIR, 'sample_scan_192.168.20.1.json'), 'w', encoding='utf-8') as f:
            json.dump(sample, f, indent=2)


ensure_scans_dir()


def is_local_ip(ip):
    try:
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback
    except Exception:
        return False


def save_scan_report(ip, results):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_id = f'scan_{ip.replace(".", "_")}_{timestamp}.json'
    time_str = datetime.now().strftime('%H:%M:%S')
    report = {'ip': ip, 'time': time_str, 'results': results}
    path = os.path.join(SCANS_DIR, report_id)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    return report_id


def list_scan_reports():
    reports = []
    for name in os.listdir(SCANS_DIR):
        if not name.endswith('.json'):
            continue
        path = os.path.join(SCANS_DIR, name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            results = data.get('results', data if isinstance(data, list) else [])
            if isinstance(data, list):
                results = data
                data = {'ip': 'unknown', 'time': '', 'results': results}
            open_count = sum(1 for r in results if r.get('status') in ('open', 'open|filtered'))
            reports.append({
                'id': name,
                'ip': data.get('ip', 'unknown'),
                'time': data.get('time', ''),
                'openCount': open_count,
                'mtime': os.path.getmtime(path)
            })
        except Exception:
            continue
    reports.sort(key=lambda r: r['mtime'], reverse=True)
    for r in reports:
        del r['mtime']
    return reports


@app.route('/')
def index():
    return send_file(os.path.join(BASE_DIR, 'index.html'))


@app.route('/pages/<path:filename>')
def pages(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'pages'), filename)


@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'assets'), filename)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'online'})


@app.route('/network/info', methods=['GET'])
def network_info():
    return jsonify({
        'success': True,
        'localNetwork': get_local_network(),
        'routerIp': get_router_ip()
    })


@app.route('/reports', methods=['GET'])
def reports_list():
    return jsonify({'success': True, 'reports': list_scan_reports()})


@app.route('/reports/<report_id>', methods=['GET'])
def report_get(report_id):
    safe_name = os.path.basename(report_id)
    path = os.path.join(SCANS_DIR, safe_name)
    if not os.path.isfile(path):
        return jsonify({'success': False, 'message': 'Report not found'}), 404
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        data = {'ip': 'unknown', 'time': '', 'results': data}
    return jsonify({'success': True, 'report': data, 'id': safe_name})


@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json() or {}
    ip = data.get('ip')
    start = data.get('portStart')
    end = data.get('portEnd')
    scan_udp = bool(data.get('scanUdp', False))
    timeout_ms = int(data.get('timeout', 1000))
    timeout_sec = max(0.1, timeout_ms / 1000.0)

    if not ip or start is None or end is None:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    if not is_local_ip(ip):
        return jsonify({'success': False, 'message': 'Only local network IPs allowed for ethical use.'}), 403

    start_port = int(start)
    end_port = int(end)
    if start_port < 1 or end_port > 65535 or start_port > end_port:
        return jsonify({'success': False, 'message': 'Invalid port range'}), 400

    results = port_scan(ip, start_port, end_port, scan_udp=scan_udp, timeout=timeout_sec)

    for r in results:
        if r.get('protocol') == 'UDP' and 'service' not in r:
            r['service'] = 'unknown'

    report_id = save_scan_report(ip, results)
    return jsonify({'success': True, 'results': results, 'reportId': report_id})


@app.route('/discover', methods=['POST'])
def discover():
    data = request.get_json() or {}
    mode = data.get('mode', 'auto')
    network = data.get('network') or None
    enhanced = bool(data.get('enhanced', True))

    if mode not in ('auto', 'gateway', 'router', 'all_interfaces'):
        return jsonify({'success': False, 'message': 'Invalid discovery mode'}), 400

    try:
        hosts = network_discovery(network_str=network, mode=mode, enhanced=enhanced)
        if hosts is None:
            hosts = []
        return jsonify({'success': True, 'hosts': hosts})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/dos', methods=['POST'])
def dos():
    data = request.get_json() or {}
    ip = data.get('ip')
    port = data.get('port')
    attack_type = data.get('attackType', 'UDP_FLOOD')
    thread_count = min(4, max(1, int(data.get('threadCount', 4))))
    duration = min(60, max(1, int(data.get('duration', 10))))

    if not ip:
        return jsonify({'success': False, 'message': 'Missing IP'}), 400

    if not is_local_ip(ip):
        return jsonify({'success': False, 'message': 'Only local network IPs allowed for ethical use.'}), 403

    if attack_type != 'HTTP_FLOOD' and port is None:
        return jsonify({'success': False, 'message': 'Missing port'}), 400

    start = time.time()
    packets_sent = 0

    if attack_type == 'UDP_FLOOD':
        packets_sent = udp_flood(ip, int(port), duration, thread_count)
    elif attack_type == 'TCP_SYN':
        packets_sent = tcp_flood(ip, int(port), duration, thread_count)
    elif attack_type == 'HTTP_FLOOD':
        packets_sent = http_flood(ip, duration, thread_count)
    else:
        return jsonify({'success': False, 'message': 'Unknown attack type'}), 400

    elapsed = time.time() - start
    pps = int(packets_sent / elapsed) if elapsed > 0 else 0

    return jsonify({
        'success': True,
        'message': f'Attack completed on {ip}',
        'packetsSent': packets_sent,
        'duration': round(elapsed, 2),
        'pps': pps
    })


if __name__ == '__main__':
    print('[*] NETWOLF running at http://127.0.0.1:5000')
    app.run(debug=True, port=5000)
