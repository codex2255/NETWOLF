import socket
import subprocess
import threading
import ipaddress
import platform
import re
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


def get_router_ip():

    try:

        system = platform.system().lower()
        
        if system == 'windows':

            result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=5)
            
            lines = result.stdout.split('\n')
            
            for line in lines:
                
                if 'Default Gateway' in line or 'default gateway' in line.lower():
                    
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    
                    if match:
                        
                        return match.group(1)
        
        elif system == 'linux' or system == 'darwin':

            result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=5)
            
            lines = result.stdout.split('\n')
            
            for line in lines:
                
                if 'default' in line:
                    
                    parts = line.split()
                    
                    if len(parts) > 2:
                        
                        return parts[2]
        
        return None
        
    except:

        return None


def get_network_from_router():

    router_ip = get_router_ip()
    
    if router_ip:

        ip_parts = router_ip.split('.')
        
        network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        
        return network, router_ip
    
    return None, None


def get_all_network_interfaces():

    interfaces = []
    
    try:

        system = platform.system().lower()
        
        if system == 'windows':

            result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=5)
            
            lines = result.stdout.split('\n')
            
            current_ip = None
            
            for line in lines:
                
                if 'IPv4 Address' in line or 'IP Address' in line:
                    
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    
                    if match:
                        
                        current_ip = match.group(1)
                
                if 'Subnet Mask' in line and current_ip:
                    
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    
                    if match:
                        
                        subnet = match.group(1)
                        
                        ip_parts = current_ip.split('.')
                        
                        if subnet == '255.255.255.0':
                            
                            network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
                        
                        elif subnet == '255.255.0.0':
                            
                            network = f"{ip_parts[0]}.{ip_parts[1]}.0.0/16"
                        
                        else:
                            
                            network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
                        
                        interfaces.append({'ip': current_ip, 'network': network, 'subnet': subnet})
                        
                        current_ip = None
        
        elif system == 'linux':

            result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=5)
            
            lines = result.stdout.split('\n')
            
            for line in lines:
                
                if 'inet ' in line and '127.0.0.1' not in line:
                    
                    parts = line.strip().split()
                    
                    if len(parts) > 1:
                        
                        ip_with_cidr = parts[1]
                        
                        interfaces.append({'ip': ip_with_cidr.split('/')[0], 'network': ip_with_cidr})
        
        return interfaces
        
    except:

        return []


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


def discover_gateway_and_scan():

    router_ip = get_router_ip()
    
    if not router_ip:
        
        return None, "Could not find router IP"
    
    network, router = get_network_from_router()
    
    if not network:
        
        return None, "Could not determine network from router"
    
    print(f"[*] Found router IP: {router_ip}")
    
    print(f"[*] Scanning network: {network}")
    
    results = ping_sweep(network)
    
    if results is None:
        
        results = []
    
    gateway_info = {
        'router_ip': router_ip,
        
        'network': network,
        
        'gateway_status': 'active'
    }
    
    gateway_found = False
    
    for host in results:
        
        if host['ip'] == router_ip:
            
            gateway_found = True
            
            host['is_gateway'] = True
            
            host['hostname'] = 'Gateway/Router'
            
            break
    
    if not gateway_found:
        
        results.append({
            
            'ip': router_ip,
            
            'status': 'active',
            
            'hostname': 'Gateway/Router',
            
            'method': 'gateway_discovery',
            
            'is_gateway': True
        })
    
    return results, gateway_info


def ping_sweep(network_str):

    try:
        
        network = ipaddress.ip_network(network_str, strict=False)

        total_hosts = sum(1 for _ in network.hosts())

        if total_hosts == 0:
            
            return []

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
    
    except Exception as e:
        
        print(f"[-] Invalid network range: {network_str}")
        
        return []


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


def arp_scan(network_str):


    if platform.system().lower() == 'windows':


        return arp_scan_windows(network_str)
    
    else:
        return arp_scan_linux(network_str)


def network_discovery(network_str=None, mode='auto'):
    
    if network_str:
        
        try:
            
            ipaddress.ip_network(network_str, strict=False)
            
        except:
            
            print(f"[-] Invalid network format: {network_str}")
            
            print("[*] Please use CIDR format like: 192.168.1.0/24")
            
            return []
    
    if mode == 'gateway':
        
        results, gateway_info = discover_gateway_and_scan()
        
        if results is None:
            
            print(f"[-] Gateway discovery failed: {gateway_info}")
            
            network_str = get_local_network()
            
            results = ping_sweep(network_str)
        
        return results
    
    elif mode == 'router':
        
        results, gateway_info = discover_gateway_and_scan()
        
        return results
    
    elif mode == 'all_interfaces':
        
        all_devices = []
        
        interfaces = get_all_network_interfaces()
        
        for iface in interfaces:
            
            print(f"[*] Scanning interface network: {iface['network']}")
            
            devices = ping_sweep(iface['network'])
            
            if devices:
                
                all_devices.extend(devices)
        
        return all_devices
    
    else:
        
        if network_str is None:

            network_str = get_local_network()
        
        print(f"[*] Starting network discovery on {network_str}")

        print("[*] Method: Ping sweep + ARP scan")
        
        ping_results = ping_sweep(network_str)
        
        if ping_results is None:
            
            ping_results = []
        
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


def smart_discovery():

    router_ip = get_router_ip()
    
    if router_ip and router_ip != '127.0.0.1':
        
        print("[*] Router detected, scanning entire network")
        
        results, _ = discover_gateway_and_scan()
        
        return results
    
    else:
        
        print("[*] No router detected, scanning local subnet")
        
        return network_discovery()