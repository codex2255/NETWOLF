import socket
import struct

import socket

def send_packet( sock, target_ip, target_port):
    try:
        # Send the string IP as bytes
        payload = bytes("192.168.20.102", 'utf-8')
        sock.sendto(payload, (target_ip, target_port))
    except Exception as e:
        print(f"Error sending packet: {e}")