import scapy.all as scapy
import traceback # Import the traceback module for detailed errors
import netfilterqueue

def process_packet(packet):

    print(f"[HTTP] Packet received! Length: {len(packet.get_payload())}")

    try:

        scapy_packet = scapy.IP(packet.get_payload())

        print(f"[HTTP] Packet parsed by scapy: {scapy_packet.summary}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        traceback.print_exc()
    
    packet.accept()


def start():
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet)
    print("[HTTP] Packet modifier started. Waiting for traffic...")
    try:
        queue.run()
    except KeyboardInterrupt:
        print("\n[HTTP] Shutting down packet modifier.")
        queue.unbind()
