import socket
import threading
from queue import Queue


def scan_port(target, port, results, index):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.settimeout(0.5)

        result = sock.connect_ex((target, port))
        
        if result == 0:
            results[index] = {'port': port, 'status': 'open'}

        else:
            results[index] = {'port': port, 'status': 'closed'}

        sock.close()
    except:
        results[index] = {'port': port, 'status': 'error'}

def port_scan(target, start_port, end_port):

    total_ports = end_port - start_port + 1

    results = [None] * total_ports

    threads = []

    max_threads = 100
    
    for i in range(0, total_ports, max_threads):

        batch = range(i, min(i + max_threads, total_ports))
        for idx in batch:

            port = start_port + idx

            thread = threading.Thread(target=scan_port, args=(target, port, results, idx))
            threads.append(thread)

            thread.start()
        
        for thread in threads:

            thread.join()

        threads = []
    
    return [r for r in results if r and r['status'] == 'open']


def service_detection(target, port_list):

    results = []

    service_map = {
        21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',

        53: 'DNS', 80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL',
        5432: 'PostgreSQL', 27017: 'MongoDB', 6379: 'Redis'
    }
    
    for port in port_list:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.settimeout(1)

            sock.connect((target, port))
            
            banner = ''
            try:
                sock.send(b'HEAD / HTTP/1.0\r\n\r\n')

                banner = sock.recv(1024).decode('utf-8', errors='ignore')

            except:

                pass
            
            service = service_map.get(port, 'Unknown')
            results.append({

                'port': port,
                'service': service,

                'banner': banner[:100]
            })
            sock.close()
        except:
            results.append({'port': port, 'service': 'Closed/Filtered', 'banner': ''})
    
    return results

def os_fingerprint(target):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

        sock.settimeout(2)
    except:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.settimeout(2)

            sock.connect((target, 80))

            ttl = sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)

            sock.close()
            
            if ttl <= 64:

                os_type = "Linux/Unix-like"
            elif ttl <= 128:

                os_type = "Windows"

            else:
                os_type = "Unknown"

            
            return {'os': os_type, 'ttl': ttl, 'window': 0}
        
        except:
            
            return {'os': 'Unknown', 'ttl': 0, 'window': 0}
    
    return {'os': 'Unknown', 'ttl': 0, 'window': 0}