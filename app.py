import socket
import threading
import time
import ipaddress
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from utils.attack import send_packet
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def is_local_ip(ip):
    try:
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback
    except:
        return False


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


def scan_port(target, port, results, lock):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((target, port))
        s.close()
        status = 'open' if result == 0 else 'closed'
        with lock:
            results.append({'port': port, 'status': status, 'protocol': 'TCP'})
    except Exception:
        with lock:
            results.append({'port': port, 'status': 'error', 'protocol': 'TCP'})


def run_scan(target, ports):
    threads = []
    results = []
    lock = threading.Lock()
    for port in ports:
        t = threading.Thread(target=scan_port, args=(target, port, results, lock))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return results


def run_attack(target_ip, target_port, packet_count):
    sent = [0]
    lock = threading.Lock()

    def worker():
        while True:
            with lock:
                if sent[0] >= packet_count:
                    return
                sent[0] += 1
            try:
                send_packet(target_ip, target_port)
            except Exception:
                pass
            time.sleep(0.00001)

    threads = []
    for _ in range(4):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    ip = data.get('ip')
    start = data.get('portStart')
    end = data.get('portEnd')

    if not ip or start is None or end is None:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    if not is_local_ip(ip):
        return jsonify({'success': False, 'message': 'Only local network IPs allowed for ethical use.'}), 403

    ports = list(range(int(start), int(end) + 1))
    results = run_scan(ip, ports)
    return jsonify({'success': True, 'results': results})


@app.route('/dos', methods=['POST'])
def dos():
    data = request.get_json()
    ip = data.get('ip')
    port = data.get('port')
    packets = data.get('packetCount')

    if not ip or port is None or packets is None:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    if not is_local_ip(ip):
        return jsonify({'success': False, 'message': 'Only local network IPs allowed for ethical use.'}), 403

    run_attack(ip, int(port), int(packets))
    return jsonify({'success': True, 'message': f'Attack completed on {ip}:{port}'})


if __name__ == '__main__':
    print('[*] NETWOLF running at http://127.0.0.1:5000')
    app.run(debug=True, port=5000)