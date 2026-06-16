import socket
import subprocess
import threading
import ipaddress
import platform
from queue import Queue

def get_local_network():
    try:

        hostname = socket.gethostname()

        local_ip = socket.gethostbyname(hostname)
        ip_parts = local_ip.split('.')

        network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        return network
    except:
        return "192.168.1.0/24"

def ping_host(ip, results, index):

    param = '-n' if platform.system().lower() == 'windows' else '-c'

    command = ['ping', param, '1', '-W', '1', ip]
    
    try:
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        
        if result.returncode == 0:

            try:
                hostname = socket.gethostbyaddr(ip)[0]

            except:

                hostname = None
            
            results[index] = {
                'ip': ip,

                'status': 'active',

                'hostname': hostname,

                'method': 'ping'
            }
        else:
            results[index] = {
                'ip': ip,

                'status': 'inactive',
                'hostname': None,

                'method': 'ping'
            }
    except:
        results[index] = {
            'ip': ip,

            'status': 'timeout',
            'hostname': None,

            'method': 'ping'
        }

def arp_scan_linux(network_str):

    results = []

    try:
        network = ipaddress.ip_network(network_str, strict=False)

        
        for ip in network.hosts():

            ip_str = str(ip)
            try:
                result = subprocess.run(['arping', '-c', '1', '-W', '1', ip_str], 
                                        
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                if result.returncode == 0:

                    try:
                        hostname = socket.gethostbyaddr(ip_str)[0]

                    except:

                        hostname = None
                    
                    results.append({

                        'ip': ip_str,

                        'status': 'active',

                        'hostname': hostname,

                        'method': 'arp'
                    })
            except:
                pass
    except:

        pass

    return results

def arp_scan_windows(network_str):

    results = []

    try:

        result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)

        lines = result.stdout.split('\n')
        
        for line in lines:

            parts = line.split()

            if len(parts) >= 3 and '.' in parts[0]:

                ip = parts[0]

                if ip.startswith(network_str.split('.')[0]):

                    try:

                        hostname = socket.gethostbyaddr(ip)[0]

                    except:
                        hostname = None

                    
                    results.append({

                        'ip': ip,

                        'status': 'active',

                        'hostname': hostname,

                        'method': 'arp'
                    })
    except:
        pass
    return results

def ping_sweep(network_str):

    network = ipaddress.ip_network(network_str, strict=False)

    total_hosts = sum(1 for _ in network.hosts())

    results = [None] * total_hosts
    threads = []


    max_threads = 50
    
    host_list = list(network.hosts())
    
    for i in range(0, total_hosts, max_threads):

        batch = range(i, min(i + max_threads, total_hosts))
        for idx in batch:

            ip = str(host_list[idx])
            thread = threading.Thread(target=ping_host, args=(ip, results, idx))


            threads.append(thread)

            thread.start()
        
        for thread in threads:

            thread.join()


        threads = []
    
    return [r for r in results if r and r['status'] == 'active']

def arp_scan(network_str):


    if platform.system().lower() == 'windows':


        return arp_scan_windows(network_str)
    
    else:
        return arp_scan_linux(network_str)

def network_discovery(network_str=None):
    
    if network_str is None:


        network_str = get_local_network()
    
    print(f"[*] Starting network discovery on {network_str}")


    print("[*] Method: Ping sweep + ARP scan")
    
    ping_results = ping_sweep(network_str)
    
    arp_results = arp_scan(network_str)
    
    all_hosts = {}

    for host in ping_results:


        all_hosts[host['ip']] = host
    
    for host in arp_results:

        if host['ip'] in all_hosts:


            all_hosts[host['ip']]['method'] = 'ping+arp'
        else:

            all_hosts[host['ip']] = host

    
    return list(all_hosts.values())

def quick_discovery():

    network = get_local_network()

    
    return ping_sweep(network)