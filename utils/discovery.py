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


def get_mac_address(ip):
    
    try:
        
        system = platform.system().lower()
        
        if system == 'windows':
            
            result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True, timeout=3)
            
            lines = result.stdout.split('\n')
            
            for line in lines:
                
                if ip in line:
                    
                    match = re.search(r'([0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2})', line)
                    
                    if match:
                        
                        return match.group(1).replace('-', ':')
        
        elif system == 'linux' or system == 'darwin':
            
            result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True, timeout=3)
            
            lines = result.stdout.split('\n')
            
            for line in lines:
                
                if ip in line:
                    
                    parts = line.split()
                    
                    if len(parts) >= 3:
                        
                        mac = parts[2]
                        
                        if re.match(r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}', mac):
                            
                            return mac
        
        return None
        
    except:
        
        return None


def get_manufacturer_from_mac(mac):
    
    if not mac:
        
        return "Unknown"
    
    mac_prefix = mac.replace(':', '').upper()[:6]
    
    oui_database = {
        '0000AA': 'Xerox',
        '00037F': 'Apple',
        '000E6C': 'Apple',
        '0010FA': 'Apple',
        '0017F2': 'Apple',
        '001EC2': 'Apple',
        '00241C': 'Apple',
        '00254B': 'Apple',
        '006042': 'Apple',
        '0060A5': 'Apple',
        '0080D3': 'Apple',
        '00A0C9': 'Apple',
        '00C04F': 'Microsoft',
        '00D04C': 'Microsoft',
        '000C29': 'VMware',
        '005056': 'VMware',
        '000C6E': 'Dell',
        '00144F': 'Dell',
        '0018F3': 'Dell',
        '00215A': 'Dell',
        '00A0C6': 'Dell',
        '000ACD': 'HP',
        '001CBF': 'HP',
        '002197': 'HP',
        '0022B0': 'HP',
        '000E7F': 'Intel',
        '001255': 'Intel',
        '001A11': 'Intel',
        '00806F': 'Intel',
        '008087': 'Intel',
        '0010E0': 'Raspberry Pi',
        '0022D7': 'Raspberry Pi',
        '004A3B': 'Samsung',
        '00A042': 'Samsung',
        '008040': 'Samsung',
        '00808B': 'Samsung',
        '0005D8': 'Google',
        '001A6C': 'Google',
        '0022A5': 'Google',
        '00807A': 'Google',
        'F0D5BF': 'TP-Link',
        '00257B': 'Cisco',
        '001BE9': 'Cisco',
        '000FDB': 'Cisco',
        '000B46': 'Sony',
        '0080A3': 'Sony',
        '0018B7': 'Linux',
        '001DD2': 'Linux',
        '0001E6': 'Linux',
        '525400': 'QEMU/VirtualBox',
        '080027': 'VirtualBox',
        '00163E': 'Xensource',
        '000C2A': 'Nintendo',
        '00E06A': 'Siemens',
        '0001C0': 'Zyxel',
        '000A5A': 'Netgear',
        '001B2F': 'Netgear',
        '0024B2': 'Netgear',
        '0050C2': 'IBM',
        '0004D2': 'SMC Networks',
        '00115E': 'ASUS',
        '001A92': 'ASUS',
        '002215': 'ASUS',
        '000E3B': 'Acer',
        '00188B': 'Acer',
        '00C0F0': 'Acer',
        '00A0DF': 'LG',
        '00226B': 'LG',
        '0050F9': 'Huawei',
        '0050F8': 'Huawei',
        'F8F21E': 'Xiaomi',
        'F8F21A': 'Xiaomi',
        'FCECDA': 'Xiaomi',
        '00AABB': 'Synology',
        '001132': 'Synology',
        '002275': 'Synology',
    }
    
    return oui_database.get(mac_prefix, "Unknown")


def identify_device_type(ip, mac, hostname, os_info):
    
    if ip and ip == get_router_ip():
        
        return "Router/Gateway"
    
    if mac:
        
        mac_upper = mac.upper()
        
        if 'VMWARE' in get_manufacturer_from_mac(mac) or 'VIRTUAL' in get_manufacturer_from_mac(mac):
            
            return "Virtual Machine"
        
        if 'RASPBERRY' in get_manufacturer_from_mac(mac):
            
            return "Raspberry Pi"
        
        if 'APPLE' in get_manufacturer_from_mac(mac):
            
            return "Apple Device"
        
        if 'SAMSUNG' in get_manufacturer_from_mac(mac) or 'LG' in get_manufacturer_from_mac(mac):
            
            return "Smart TV/Mobile"
        
        if 'CISCO' in get_manufacturer_from_mac(mac) or 'NETGEAR' in get_manufacturer_from_mac(mac) or 'TP-LINK' in get_manufacturer_from_mac(mac):
            
            return "Network Equipment"
    
    if hostname:
        
        hostname_lower = hostname.lower()
        
        if 'iphone' in hostname_lower or 'ipad' in hostname_lower:
            
            return "Apple Mobile"
        
        if 'android' in hostname_lower or 'galaxy' in hostname_lower:
            
            return "Android Device"
        
        if 'windows' in hostname_lower or 'win-' in hostname_lower or 'desktop' in hostname_lower:
            
            return "Windows PC"
        
        if 'linux' in hostname_lower or 'ubuntu' in hostname_lower:
            
            return "Linux System"
        
        if 'raspberry' in hostname_lower or 'raspi' in hostname_lower:
            
            return "Raspberry Pi"
        
        if 'mac' in hostname_lower or 'mbp' in hostname_lower:
            
            return "Mac Computer"
        
        if 'printer' in hostname_lower or 'print' in hostname_lower:
            
            return "Printer"
        
        if 'camera' in hostname_lower or 'cam' in hostname_lower:
            
            return "Security Camera"
    
    if os_info:
        
        if 'windows' in os_info.lower():
            
            return "Windows PC"
        
        if 'linux' in os_info.lower():
            
            return "Linux/Unix"
        
        if 'mac' in os_info.lower() or 'darwin' in os_info.lower():
            
            return "Mac/Apple"
    
    return "Device"


def get_os_from_ttl(ttl):
    
    if ttl <= 64:
        
        return "Linux/Unix/Android"
    
    elif ttl <= 128:
        
        return "Windows"
    
    elif ttl <= 255:
        
        return "Solaris/Cisco"
    
    else:
        
        return "Unknown"


def quick_os_detect(ip):
    
    try:
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        
        sock.settimeout(2)
        
    except:
        
        try:
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            sock.settimeout(1)
            
            sock.connect((ip, 80))
            
            ttl = sock.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
            
            sock.close()
            
            return get_os_from_ttl(ttl)
            
        except:
            
            return "Unknown"
    
    return "Unknown"


def get_device_hostname(ip):
    
    try:
        
        hostname = socket.gethostbyaddr(ip)[0]
        
        return hostname
        
    except:
        
        return None


def enhanced_ping_host(ip, results, index):
    
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    command = ['ping', param, '1', '-W', '1', ip]
    
    try:
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        
        if result.returncode == 0:

            hostname = get_device_hostname(ip)
            
            mac = get_mac_address(ip)
            
            manufacturer = get_manufacturer_from_mac(mac)
            
            os_type = quick_os_detect(ip)
            
            device_type = identify_device_type(ip, mac, hostname, os_type)
            
            results[index] = {
                'ip': ip,

                'status': 'active',

                'hostname': hostname if hostname else None,
                
                'mac': mac,
                
                'manufacturer': manufacturer,
                
                'os': os_type,
                
                'device_type': device_type,

                'method': 'ping'
            }
        else:
            results[index] = {
                'ip': ip,

                'status': 'inactive',
                
                'hostname': None,
                
                'mac': None,
                
                'manufacturer': None,
                
                'os': None,
                
                'device_type': None,

                'method': 'ping'
            }
    except:
        results[index] = {
            'ip': ip,

            'status': 'timeout',
            
            'hostname': None,
            
            'mac': None,
            
            'manufacturer': None,
            
            'os': None,
            
            'device_type': None,

            'method': 'ping'
        }


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


def discover_gateway_and_scan():

    router_ip = get_router_ip()
    
    if not router_ip:
        
        return None, "Could not find router IP"
    
    network, router = get_network_from_router()
    
    if not network:
        
        return None, "Could not determine network from router"
    
    print(f"[*] Found router IP: {router_ip}")
    
    print(f"[*] Scanning network: {network}")
    
    results = enhanced_ping_sweep(network)
    
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
            
            host['device_type'] = 'Router/Gateway'
            
            if not host['hostname']:
                
                host['hostname'] = 'Gateway/Router'
            
            break
    
    if not gateway_found:
        
        results.append({
            
            'ip': router_ip,
            
            'status': 'active',
            
            'hostname': 'Gateway/Router',
            
            'mac': None,
            
            'manufacturer': None,
            
            'os': 'Router OS',
            
            'device_type': 'Router/Gateway',
            
            'method': 'gateway_discovery',
            
            'is_gateway': True
        })
    
    return results, gateway_info


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


def enhanced_ping_sweep(network_str):

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
                thread = threading.Thread(target=enhanced_ping_host, args=(ip, results, idx))


                threads.append(thread)

                thread.start()
            
            for thread in threads:

                thread.join()


            threads = []
        
        return [r for r in results if r and r['status'] == 'active']
    
    except Exception as e:
        
        print(f"[-] Invalid network range: {network_str}")
        
        return []


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

                    hostname = get_device_hostname(ip_str)
                    
                    mac = get_mac_address(ip_str)
                    
                    manufacturer = get_manufacturer_from_mac(mac)
                    
                    os_type = quick_os_detect(ip_str)
                    
                    device_type = identify_device_type(ip_str, mac, hostname, os_type)

                    results.append({

                        'ip': ip_str,

                        'status': 'active',

                        'hostname': hostname,
                        
                        'mac': mac,
                        
                        'manufacturer': manufacturer,
                        
                        'os': os_type,
                        
                        'device_type': device_type,

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

                    hostname = get_device_hostname(ip)
                    
                    mac = get_mac_address(ip)
                    
                    manufacturer = get_manufacturer_from_mac(mac)
                    
                    os_type = quick_os_detect(ip)
                    
                    device_type = identify_device_type(ip, mac, hostname, os_type)

                    results.append({

                        'ip': ip,

                        'status': 'active',

                        'hostname': hostname,
                        
                        'mac': mac,
                        
                        'manufacturer': manufacturer,
                        
                        'os': os_type,
                        
                        'device_type': device_type,

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


def network_discovery(network_str=None, mode='auto', enhanced=True):
    
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
            
            if enhanced:
                
                results = enhanced_ping_sweep(network_str)
            
            else:
                
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
            
            if enhanced:
                
                devices = enhanced_ping_sweep(iface['network'])
            
            else:
                
                devices = ping_sweep(iface['network'])
            
            if devices:
                
                all_devices.extend(devices)
        
        return all_devices
    
    else:
        
        if network_str is None:

            network_str = get_local_network()
        
        print(f"[*] Starting network discovery on {network_str}")

        print("[*] Method: Enhanced ping sweep + MAC detection + OS fingerprinting")
        
        if enhanced:
            
            ping_results = enhanced_ping_sweep(network_str)
        
        else:
            
            ping_results = ping_sweep(network_str)
        
        if ping_results is None:
            
            ping_results = []
        
        arp_results = arp_scan(network_str)
        
        all_hosts = {}

        for host in ping_results:

            all_hosts[host['ip']] = host
        
        for host in arp_results:

            if host['ip'] in all_hosts:
                
                if 'mac' in host and host['mac']:
                    
                    all_hosts[host['ip']]['mac'] = host['mac']
                
                if 'manufacturer' in host:
                    
                    all_hosts[host['ip']]['manufacturer'] = host['manufacturer']
                
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