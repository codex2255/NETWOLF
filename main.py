import socket
import threading
import time
import json
import os
from datetime import datetime
from utils.attack import udp_flood, tcp_flood, icmp_flood, http_flood, smurf_attack
from utils.scanner import port_scan, service_detection, os_fingerprint

class NetWolf:
    def __init__(self):
        self.scan_results = []

        self.attack_log = []
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
    
    def run_cli(self):
        while self.running:
            self.print_banner()
            print("\n[ MAIN MENU ]")
            print("1. Port Scanner")

            print("2. Service Detection")
            print("3. OS Fingerprinting")
            print("4. DOS Attack Suite")

            print("5. View Attack Log")
            print("6. Switch to Web GUI")
            print("7. Exit")
            
            choice = input("\nSelect option (1-7): ")
            
            if choice == '1':
                self.port_scanner_menu()
            elif choice == '2':
                self.service_detection_menu()
            elif choice == '3':
                self.os_fingerprint_menu()
            elif choice == '4':
                self.attack_menu()

            elif choice == '5':
                self.show_logs()
            elif choice == '6':
                self.start_gui()
            elif choice == '7':
                self.running = False
                print("[+] Shutting down NetWolf...")
            else:
                print("[-] Invalid option")
    
    def port_scanner_menu(self):

        target = input("Target IP: ")
        start_port = int(input("Start port (1-65535): "))

        end_port = int(input("End port: "))
        
        print(f"\n[*] Scanning {target} ports {start_port}-{end_port}")

        results = port_scan(target, start_port, end_port)
        
        self.scan_results = results
        print("\n[ OPEN PORTS ]")
        for r in results:
            if r['status'] == 'open':
                print(f"  Port {r['port']}: OPEN")
        
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
        else:
            print("[-] Attack cancelled - confirmation failed")
    
    def show_logs(self):
        if not self.attack_log:
            print("[*] No attacks logged yet")
        else:
            print("\n[ ATTACK HISTORY ]")
            for log in self.attack_log:
                print(f"  {log['timestamp']} | {log['type']} | {log['target']} | {log['duration']}s")
    
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