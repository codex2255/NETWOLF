import socket
import threading
import sys
import threading
from argparse import ArgumentParser

import utils

from utils.attack import send_packet



global target_ip
global target_port
global packet_count
global ports


def scan_port(target, port):
    try:
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        s.settimeout(1)
        
        result = s.connect_ex((target, port))

        ports = result
        
        if result == 0:
            print(f"Port {port} is open")
            
        s.close()
        
    except:
        
        pass

def start_scan(target, ports):
    
    for port in ports:
        
        thread = threading.Thread(target=scan_port, args=(target, port))
        
        thread.start()


def start_attack(target_ip, target_port, packet_count):
    print(f"Starting attack on {target_ip}:{target_port} with {packet_count} packets.")
    
    def attack_thread():
        while True:
            ip = target_ip
            try:
                send_packet(target_ip, target_port, ip)
            except Exception as e:
                print(f"Error in thread: {e}")

    threads = []
    max_threads = 10  # Limit the number of threads to prevent resource exhaustion
    for _ in range(max_threads):
        thread = threading.Thread(target=attack_thread)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join(packet_count)
        


def main_menu():
    while True:
        print("\n--- Network Scanner Menu ---")
        print("1. Run Port Scan")
        print("2. Perfomr DOS")
        print("3. Exit")
        
        choice = input("Please select an option (1 or 2): ")
        
        if choice == '1':
            target_ip = input("Enter target IP: ")
            ports_to_scan = range(1, 1025)
    
            start_scan(target_ip, ports_to_scan)

        elif choice == '2':
            target_ip = input("Enter target IP: ")
            target_port = int(input("Enter target port: "))
            packet_count = int(input("Enter number of packets to send: "))
    
            start_attack(target_ip, target_port, packet_count)
            
       
       
        elif choice == '3':
            print("Exiting the program. Goodbye!")
            break

        
            
        else:
            print("Invalid choice. Please type 1, 2 or 3.")


    

if __name__ == "__main__":

    main_menu()
    
    target_ip = input("Enter target IP: ")
    ports_to_scan = range(1, 1025)
    
    start_scan(target_ip, ports_to_scan)

    