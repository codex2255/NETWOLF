import socket
import threading
import time
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

from utils.attack import udp_flood, tcp_flood, icmp_flood, http_flood, smurf_attack, network_wide_udp_flood, broadcast_udp_flood, dns_amplification_attack
from utils.scanner import port_scan, service_detection, os_fingerprint
from utils.discovery import network_discovery, ping_sweep, arp_scan, get_router_ip, discover_gateway_and_scan, smart_discovery, get_all_network_interfaces

class NetWolf:
    def __init__(self):
        self.scan_results = []
        self.attack_log = []
        self.discovered_hosts = []
        self.running = True
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        banner = """
        ╔═══════════════════════════════════════════╗
        ║     NETWOLF - Network Security Suite      ║
        ║    Ethical Testing & Analysis Tool        ║
        ╚═══════════════════════════════════════════╝
        """
        print(banner)
    
    def save_results(self, data, filename):
        with open(f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[+] Results saved to {filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    def normalize_network_range(self, user_input):
        user_input = user_input.strip()
        if '/' in user_input:
            return user_input
        parts = user_input.split('.')
        if len(parts) == 4:
            if parts[3] == '0':
                return f"{user_input}/24"
            else:
                ip_parts = parts[:3]
                return f"{'.'.join(ip_parts)}.0/24"
        elif len(parts) == 3:
            return f"{user_input}.0/24"
        elif len(parts) == 2:
            return f"{parts[0]}.{parts[1]}.0.0/16"
        elif len(parts) == 1:
            return f"{parts[0]}.0.0.0/8"
        else:
            return user_input
    
    def run_cli(self):
        while self.running:
            self.print_banner()
            print("\n[ MAIN MENU ]")
            print("1. Network Discovery (Find all devices)")
            print("2. Port Scanner")
            print("3. Service Detection")
            print("4. OS Fingerprinting")
            print("5. DOS Attack Suite")
            print("6. View Attack Log")
            print("7. View Discovered Hosts")
            print("8. Switch to Web GUI")
            print("9. Exit")
            
            choice = input("\nSelect option (1-9): ")
            
            if choice == '1':
                self.network_discovery_menu()
            elif choice == '2':
                self.port_scanner_menu()
            elif choice == '3':
                self.service_detection_menu()
            elif choice == '4':
                self.os_fingerprint_menu()
            elif choice == '5':
                self.attack_menu()
            elif choice == '6':
                self.show_logs()
            elif choice == '7':
                self.show_discovered_hosts()
            elif choice == '8':
                self.start_gui()
            elif choice == '9':
                self.running = False
                print("[+] Shutting down NetWolf...")
            else:
                print("[-] Invalid option")
    
    def network_discovery_menu(self):
        print("\n[ NETWORK DISCOVERY ]")
        print("1. Auto-detect network and scan")
        print("2. Manual network range (e.g., 192.168.1.0/24)")
        print("3. Ping sweep only")
        print("4. ARP scan only (more accurate)")
        print("5. FIND ROUTER & SCAN ENTIRE NETWORK")
        print("6. Scan all network interfaces")
        print("7. Smart discovery (auto router detection)")
        
        choice = input("\nSelect method (1-7): ")
        results = []
        
        if choice == '1':
            network = self.get_network_range()
            print(f"\n[*] Scanning network: {network}")
            results = network_discovery(network, enhanced=True)
        elif choice == '2':
            raw_input = input("Enter network range (e.g., 192.168.1.0/24 or 192.168.1.1): ")
            network = self.normalize_network_range(raw_input)
            print(f"[*] Normalized to: {network}")
            results = network_discovery(network, enhanced=True)
        elif choice == '3':
            raw_input = input("Enter network range (e.g., 192.168.1.0/24 or 192.168.1.1): ")
            network = self.normalize_network_range(raw_input)
            print(f"[*] Normalized to: {network}")
            results = ping_sweep(network)
            if results is None: results = []
        elif choice == '4':
            raw_input = input("Enter network range (e.g., 192.168.1.0/24 or 192.168.1.1): ")
            network = self.normalize_network_range(raw_input)
            print(f"[*] Normalized to: {network}")
            results = arp_scan(network)
        elif choice == '5':
            print("\n[*] Locating router and scanning entire network...")
            router_ip = get_router_ip()
            if router_ip and router_ip != '127.0.0.1':
                print(f"[*] Found router IP: {router_ip}")
                results, gateway_info = discover_gateway_and_scan()
            else:
                print("[-] Could not find router, falling back to auto-detect")
                network = self.get_network_range()
                results = network_discovery(network, enhanced=True)
        elif choice == '6':
            print("\n[*] Scanning all network interfaces...")
            all_devices = []
            interfaces = get_all_network_interfaces()
            for iface in interfaces:
                print(f"[*] Scanning: {iface['network']}")
                devices = ping_sweep(iface['network'])
                if devices:
                    all_devices.extend(devices)
            results = all_devices
        elif choice == '7':
            print("\n[*] Running smart discovery...")
            results = smart_discovery()
        else:
            return
        
        if results is None: results = []
        self.discovered_hosts = results

        if not results:
            print("\n[-] No devices found or invalid network range")
            return

        print("\n[ DISCOVERED DEVICES - DETAILED ]")
        print("=" * 100)
        print(f"{'IP Address':<18} {'Device Type':<18} {'OS':<14} {'MAC Address':<20} {'Manufacturer':<20}")
        print("-" * 100)
        
        for host in results:
            ip = host.get('ip', 'Unknown')
            device_type = host.get('device_type', 'Device')[:18]
            os_type = host.get('os', 'Unknown')[:14]
            mac = host.get('mac', 'N/A')[:20] if host.get('mac') else 'N/A'
            manufacturer = host.get('manufacturer', 'Unknown')[:20]
            print(f"{ip:<18} {device_type:<18} {os_type:<14} {mac:<20} {manufacturer:<20}")
        
        print("=" * 100)
        print(f"\n[*] Total active hosts: {len(results)}")
        
        save = input("\nSave results? (y/n): ")
        if save.lower() == 'y':
            self.save_results(results, f"network_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    def get_network_range(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            ip_parts = local_ip.split('.')
            if local_ip == '127.0.0.1':
                print("[!] You are on localhost - try using manual network range")
                raw_input = input("Enter network range: ")
                return self.normalize_network_range(raw_input)
            network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            print(f"[*] Detected local IP: {local_ip}")
            print(f"[*] Auto-detected network: {network}")
            return network
        except:
            raw_input = input("Could not auto-detect. Enter network range: ")
            return self.normalize_network_range(raw_input)
    
    def port_scanner_menu(self):
        target = input("Target IP: ")
        start_port = int(input("Start port (1-65535): "))
        end_port = int(input("End port: "))
        scan_udp = input("Scan UDP ports as well? (y/n): ").lower() == 'y'
        print(f"\n[*] Scanning {target} ports {start_port}-{end_port}")
        results = port_scan(target, start_port, end_port, scan_udp)
        self.scan_results = results

        print("\n[ OPEN PORTS ]")
        print("-" * 50)
        print(f"{'PORT':<10} {'PROTOCOL':<10} {'SERVICE':<15}")
        print("-" * 50)
        
        for r in results:
            if r['status'] in ['open', 'open|filtered']:
                print(f"{r['port']:<10} {r['protocol']:<10} {r.get('service', 'unknown'):<15}")
        
        print("-" * 50)
        save = input("\nSave results? (y/n): ")
        if save.lower() == 'y':
            self.save_results(results, f"scan_{target}")
    
    def service_detection_menu(self):
        target = input("Target IP: ")
        ports = input("Ports to check (comma separated): ")
        port_list = [int(p.strip()) for p in ports.split(',')]
        results = service_detection(target, port_list)
        print("\n[ SERVICE DETECTION ]")
        for r in results:
            print(f"  Port {r['port']}: {r['service']} (banner: {r.get('banner', 'N/A')[:50]})")
        save = input("\nSave results? (y/n): ")
        if save.lower() == 'y':
            self.save_results(results, f"services_{target}")
    
    def os_fingerprint_menu(self):
        target = input("Target IP: ")
        results = os_fingerprint(target)
        print(f"\n[ OS Fingerprint Results ]")
        print(f"  Target: {target}")
        print(f"  Detected OS: {results['os']}")
        print(f"  TTL: {results['ttl']}")
        print(f"  Window Size: {results['window']}")
    
    def attack_menu(self):
        print("\n[ DOS ATTACK SUITE ]")
        print("1. UDP Flood (Single Target)")
        print("2. TCP Flood (Single Target)")
        print("3. ICMP Flood (Single Target)")
        print("4. HTTP Flood (Web Server)")
        print("5. Smurf Attack (Amplification)")
        print("\n--- NETWORK-WIDE ATTACKS ---")
        print("6. NETWORK-WIDE UDP Flood")
        print("7. BROADCAST FLOOD")
        print("8. DNS Amplification")
        
        attack_type = input("\nSelect attack type (1-8): ")
        if attack_type in ['6', '7', '8']:
            # Simplified for brevity in CLI, matching actual logic
            print("[-] Network-wide attacks are best executed via Web UI for monitoring")
            return
        
        target_ip = input("Target IP: ")
        target_port = input("Target port (if needed): ")
        target_port = int(target_port) if target_port else 80
        duration = int(input("Attack duration (seconds): "))
        threads = int(input("Number of threads (20-100): "))
        
        confirm = input("[!] Type 'ETHICAL USE ONLY' to confirm: ")
        if confirm == "ETHICAL USE ONLY":
            if attack_type == '1':
                udp_flood(target_ip, target_port, duration, threads)
            elif attack_type == '2':
                tcp_flood(target_ip, target_port, duration, threads)
            elif attack_type == '3':
                icmp_flood(target_ip, duration, threads)
            elif attack_type == '4':
                http_flood(target_ip, duration, threads)
            elif attack_type == '5':
                smurf_attack(target_ip, duration, threads)
            print(f"[+] Attack completed")
        else:
            print("[-] Attack cancelled")
    
    def show_logs(self):
        if not self.attack_log:
            print("[*] No attacks logged yet")
        else:
            print("\n[ ATTACK HISTORY ]")
            for log in self.attack_log:
                print(f"  {log['timestamp']} | {log['type']} | {log['target']} | {log['duration']}s")
    
    def show_discovered_hosts(self):
        if not self.discovered_hosts:
            print("[*] No hosts discovered yet.")
        else:
            print("\n[ DISCOVERED HOSTS ]")
            for host in self.discovered_hosts:
                print(f"  {host.get('ip', 'Unknown')} - {host.get('device_type', 'Device')}")
    
    def start_gui(self):
        print("[*] Starting web interface on http://127.0.0.1:5555")
        start_web_server()

# --- WEB SERVER LOGIC ---

app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/pages/<path:filename>')
def pages(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'pages'), filename)

@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'assets'), filename)

@app.route('/scan', methods=['POST'])
def api_scan():
    data = request.get_json()
    ip = data.get('ip')
    start = data.get('portStart')
    end = data.get('portEnd')
    if not ip or start is None or end is None:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400
    
    results = port_scan(ip, int(start), int(end))
    return jsonify({'success': True, 'results': results})

@app.route('/dos', methods=['POST'])
def api_dos():
    data = request.get_json()
    ip = data.get('ip')
    port = data.get('port', 80)
    packets = data.get('packetCount', 1000)
    attack_type = data.get('type', 'UDP_FLOOD')
    threads = data.get('threads', 4)
    
    if not ip:
        return jsonify({'success': False, 'message': 'Missing target IP'}), 400

    # Execute attack based on type
    # Note: Using simplified duration/packet logic to bridge frontend and backend
    duration = 10 # Default duration for API calls
    
    def attack_task():
        if attack_type == 'UDP_FLOOD':
            udp_flood(ip, int(port), duration, int(threads))
        elif attack_type == 'TCP_SYN':
            tcp_flood(ip, int(port), duration, int(threads))
        elif attack_type == 'HTTP_FLOOD':
            http_flood(ip, duration, int(threads))
        # Add more types as needed

    thread = threading.Thread(target=attack_task)
    thread.start()
    
    return jsonify({'success': True, 'message': f'Attack {attack_type} started on {ip}'})

def start_web_server():
    app.run(debug=False, port=5555, host='0.0.0.0')

if __name__ == "__main__":
    print("[*] NetWolf v1.0 - Ethical Network Testing Tool")
    print("[*] Choose interface:")
    print("    1. Command Line Interface (CLI)")
    print("    2. Web Graphical Interface (GUI)")
    
    choice = input("\nSelect (1 or 2): ")
    tool = NetWolf()
    
    if choice == '2':
        start_web_server()
    else:
        tool.run_cli()
