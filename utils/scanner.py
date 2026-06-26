import socket
import threading
from queue import Queue

def scan_port(target, port, results, index, timeout=0.5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))
        
        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            
            results[index] = {
                'port': port, 
                'status': 'open', 
                'protocol': 'TCP',
                'service': service
            }
        else:
            results[index] = {
                'port': port, 
                'status': 'closed', 
                'protocol': 'TCP',
                'service': None
            }
        sock.close()
    except:
        results[index] = {
            'port': port, 
            'status': 'error', 
            'protocol': 'TCP',
            'service': None
        }

def scan_udp_port(target, port, timeout=1):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        sock.sendto(b'', (target, port))
        try:
            data, addr = sock.recvfrom(1024)
            sock.close()
            return {'port': port, 'status': 'open', 'protocol': 'UDP'}
        except socket.timeout:
            sock.close()
            return {'port': port, 'status': 'open|filtered', 'protocol': 'UDP'}
    except:
        return {'port': port, 'status': 'closed', 'protocol': 'UDP'}

def port_scan(target, start_port, end_port, scan_udp=False, timeout=0.5):
    total_ports = end_port - start_port + 1
    results = [None] * total_ports
    threads = []
    max_threads = 100
    
    for i in range(0, total_ports, max_threads):
        batch = range(i, min(i + max_threads, total_ports))
        for idx in batch:
            port = start_port + idx
            thread = threading.Thread(target=scan_port, args=(target, port, results, idx, timeout))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        threads = []
    
    tcp_results = [r for r in results if r and r['status'] == 'open']
    
    if scan_udp:
        print("[*] Also scanning common UDP ports...")
        udp_common = [53, 67, 68, 69, 123, 161, 520, 1900]
        udp_results = []
        
        for port in udp_common:
            if start_port <= port <= end_port:
                result = scan_udp_port(target, port, timeout=timeout)
                if result['status'] in ['open', 'open|filtered']:
                    udp_results.append(result)
        
        return tcp_results + udp_results
    
    return tcp_results

def service_detection(target, port_list):
    results = []
    service_map = {
        21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
        53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
        443: 'HTTPS', 993: 'IMAPS', 995: 'POP3S',
        3306: 'MySQL', 5432: 'PostgreSQL', 27017: 'MongoDB',
        6379: 'Redis', 11211: 'Memcached', 8080: 'HTTP-Alt'
    }
    
    for port in port_list:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((target, port))
            
            banner = ''
            try:
                if port in [80, 443, 8080, 8000]:
                    sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
                elif port in [21, 25, 110, 143]:
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                else:
                    sock.send(b'\r\n')
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
            except:
                pass
            
            service = service_map.get(port, 'Unknown')
            results.append({
                'port': port,
                'protocol': 'TCP',
                'service': service,
                'banner': banner[:100] if banner else 'No banner'
            })
            sock.close()
        except:
            results.append({
                'port': port, 
                'protocol': 'TCP',
                'service': 'Closed/Filtered', 
                'banner': ''
            })
    
    return results

def os_fingerprint(target):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((target, 80))
        
        ttl = sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
        sock.close()
        
        if ttl <= 64:
            os_type = "Linux/Unix/Android (TTL=64)"
        elif ttl <= 128:
            os_type = "Windows (TTL=128)"
        elif ttl <= 255:
            os_type = "Solaris/Cisco (TTL=255)"
        else:
            os_type = "Unknown"
        
        return {'os': os_type, 'ttl': ttl, 'window': 0}
    except:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.settimeout(2)
            sock.close()
            return {'os': 'Linux/Unix (ICMP available)', 'ttl': 64, 'window': 0}
        except:
            return {'os': 'Unknown (no response)', 'ttl': 0, 'window': 0}