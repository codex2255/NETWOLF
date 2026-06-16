import socket
import threading
import time
import json
import os
from datetime import datetime
from utils.attack import udp_flood, tcp_flood, icmp_flood, http_flood, smurf_attack
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
            results = network_discovery(network)
            
        elif choice == '2':

            raw_input = input("Enter network range (e.g., 192.168.1.0/24 or 192.168.1.1): ")
            
            network = self.normalize_network_range(raw_input)
            
            print(f"[*] Normalized to: {network}")

            results = network_discovery(network)
            
        elif choice == '3':

            raw_input = input("Enter network range (e.g., 192.168.1.0/24 or 192.168.1.1): ")
            
            network = self.normalize_network_range(raw_input)
            
            print(f"[*] Normalized to: {network}")
            
            results = ping_sweep(network)
            
            if results is None:
                
                results = []
            
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
                
                if results:
                    
                    for host in results:
                        
                        if host.get('is_gateway'):
                            
                            print(f"\n[*] GATEWAY FOUND: {host['ip']}")
            else:
                
                print("[-] Could not find router, falling back to auto-detect")
                
                network = self.get_network_range()
                
                results = network_discovery(network)
                
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
        
        if results is None:
            
            results = []
        
        self.discovered_hosts = results

        if not results:
            
            print("\n[-] No devices found or invalid network range")
            
            return

        print("\n[ DISCOVERED DEVICES ]")
        print("-" * 70)

        print(f"{'IP Address':<20} {'Status':<10} {'Type':<15} {'Hostname':<25}")
        print("-" * 70)

        
        for host in results:


            hostname_str = host.get('hostname', 'Unknown')[:25] if host.get('hostname') else 'Unknown'
            
            device_type = "Router" if host.get('is_gateway') else "Device"

            print(f"{host['ip']:<20} {host['status']:<10} {device_type:<15} {hostname_str:<25}")
        
        print("-" * 70)

        router_count = len([h for h in results if h.get('is_gateway')])
        
        active_count = len([h for h in results if h['status'] == 'active'])

        print(f"\n[*] Total active hosts: {active_count}")
        
        print(f"[*] Routers/Gateways found: {router_count}")
        
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
    
    if scan_udp:
        print("[*] Scanning TCP and common UDP ports")
    
    results = port_scan(target, start_port, end_port, scan_udp)
    
    self.scan_results = results

    print("\n[ OPEN PORTS ]")
    print("-" * 50)
    print(f"{'PORT':<10} {'PROTOCOL':<10} {'SERVICE':<15}")
    print("-" * 50)

    tcp_open = 0
    udp_open = 0
    
    for r in results:
        if r['status'] == 'open':
            print(f"{r['port']:<10} {r['protocol']:<10} {r.get('service', 'unknown'):<15}")
            if r['protocol'] == 'TCP':
                tcp_open += 1
            else:
                udp_open += 1
        elif r['status'] == 'open|filtered':
            print(f"{r['port']:<10} {r['protocol']:<10} UDP (open|filtered)")
            udp_open += 1
    
    print("-" * 50)
    print(f"\n[*] Total open ports: {len([r for r in results if r['status'] in ['open', 'open|filtered']])}")
    print(f"[*] TCP open: {tcp_open}")
    if scan_udp:
        print(f"[*] UDP open: {udp_open}")
    
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

        print("1. UDP Flood")

        print("2. TCP Flood (SYN)")
        print("3. ICMP Flood (Ping)")

        print("4. HTTP Flood")
        print("5. Smurf Attack")
        
        attack_type = input("\nSelect attack type (1-5): ")

        target_ip = input("Target IP: ")
        target_port = input("Target port (if needed): ")

        target_port = int(target_port) if target_port else None
        duration = int(input("Attack duration (seconds): "))

        threads = int(input("Number of threads (1-20): "))
        
        print(f"\n[!] WARNING: Starting {attack_type} attack on {target_ip}")

        print(f"[!] Duration: {duration} seconds | Threads: {threads}")
        confirm = input("[!] Type 'ETHICAL USE ONLY' to confirm: ")


        
        if confirm == "ETHICAL USE ONLY":

            self.attack_log.append({

                'timestamp': datetime.now().isoformat(),
                'target': target_ip,
                'type': attack_type,

                'duration': duration,

                'threads': threads
            })
            
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
                
            print(f"[+] Attack completed - {duration} seconds of {attack_type} traffic sent to {target_ip}")
        else:
            print("[-] Attack cancelled - confirmation failed")
    
    def show_logs(self):
        if not self.attack_log:

            print("[*] No attacks logged yet")
        else:
            print("\n[ ATTACK HISTORY ]")

            for log in self.attack_log:
                print(f"  {log['timestamp']} | {log['type']} | {log['target']} | {log['duration']}s")
    
    def show_discovered_hosts(self):

        if not self.discovered_hosts:
            print("[*] No hosts discovered yet. Run Network Discovery first.")

        else:
            print("\n[ DISCOVERED HOSTS ]")

            print("-" * 70)

            print(f"{'IP Address':<20} {'Status':<10} {'Type':<15} {'Hostname':<25}")

            print("-" * 70)
            
            for host in self.discovered_hosts:

                hostname_str = host.get('hostname', 'Unknown')[:25] if host.get('hostname') else 'Unknown'
                
                device_type = "Router" if host.get('is_gateway') else "Device"

                print(f"{host['ip']:<20} {host['status']:<10} {device_type:<15} {hostname_str:<25}")
            
            print("-" * 70)
    
    def start_gui(self):
        print("[*] Starting web interface on http://127.0.0.1:5000")

        print("[*] Press Ctrl+C in terminal to return to CLI")
        try:
            from web_interface import app

            app.run(debug=False, host='127.0.0.1', port=5000)

        except Exception as e:
            print(f"[-] Failed to start GUI: {e}")

            print("[*] Make sure Flask is installed: pip install flask")

if __name__ == "__main__":

    print("[*] NetWolf v1.0 - Ethical Network Testing Tool")

    print("[*] Choose interface:")

    print("    1. Command Line Interface (CLI)")
    print("    2. Web Graphical Interface (GUI)")
    
    choice = input("\nSelect (1 or 2): ")
    tool = NetWolf()
    
    if choice == '2':
        
        tool.start_gui()
    else:
        tool.run_cli()