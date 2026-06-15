from flask import Flask, request, jsonify
from flask_cors import CORS
from main import start_scan, start_attack

app = Flask(__name__)
CORS(app)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    target_ip = data.get('ip')
    port_start = int(data.get('portStart'))
    port_end = int(data.get('portEnd'))
    
    ports = list(range(port_start, port_end + 1))
    results = start_scan(target_ip, ports)
    
    return jsonify({ 'success': True, 'results': results })

@app.route('/dos', methods=['POST'])
def dos():
    data = request.get_json()
    target_ip = data.get('ip')
    target_port = int(data.get('port'))
    packet_count = int(data.get('packetCount'))
    
    start_attack(target_ip, target_port, packet_count)
    
    return jsonify({ 'success': True, 'message': f'Attack completed on {target_ip}:{target_port}' })

if __name__ == '__main__':
    app.run(debug=True, port=5000)