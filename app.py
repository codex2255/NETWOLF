from flask import Flask, request, jsonify
from flask_cors import CORS
from .main import start_scan, start_attack

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({ 'status': 'online' })

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    ip = data.get('ip')
    start = int(data.get('portStart'))
    end = int(data.get('portEnd'))

    if not ip or not start or not end:
        return jsonify({ 'success': False, 'message': 'Missing fields' }), 400

    ports = list(range(start, end + 1))
    results = start_scan(ip, ports)

    return jsonify({ 'success': True, 'results': results })

@app.route('/dos', methods=['POST'])
def dos():
    data = request.get_json()
    ip = data.get('ip')
    port = int(data.get('port'))
    packets = int(data.get('packetCount'))

    if not ip or not port or not packets:
        return jsonify({ 'success': False, 'message': 'Missing fields' }), 400

    start_attack(ip, port, packets)

    return jsonify({ 'success': True, 'message': 'Attack completed on ' + ip + ':' + str(port) })

if __name__ == '__main__':
    app.run(debug=True, port=5000)