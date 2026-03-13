import socket
import threading

def scan_port(target, port):
    try:
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        s.settimeout(1)
        
        result = s.connect_ex((target, port))
        
        if result == 0:
            print(f"Port {port} is open")
            
        s.close()
        
    except:
        
        pass

def start_scan(target, ports):
    
    for port in ports:
        
        thread = threading.Thread(target=scan_port, args=(target, port))
        
        thread.start()
        
        

if __name__ == "__main__":
    
    target_ip = input("Enter target IP: ")
    ports_to_scan = range(1, 1025)
    
    start_scan(target_ip, ports_to_scan)