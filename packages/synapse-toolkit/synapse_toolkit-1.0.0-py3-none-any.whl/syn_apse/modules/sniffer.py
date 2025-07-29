# syn_apse/modules/sniffer.py
import scapy.all as scapy

def _packet_callback(packet):
    """
    Callback function for every new sniffed packet.
    Finds specific packet information relating to IP, TCP, UDP and ICMP 
    """
   # Check if the packet has an IP layer, as we are interested in internet traffic
    if scapy.IP in packet:
        ip_src = packet[scapy.IP].src
        ip_dst = packet[scapy.IP].dst

        # Check for the protocol within the IP layer
        if scapy.TCP in packet:
            tcp_sport = packet[scapy.TCP].sport # Source Port
            tcp_dport = packet[scapy.TCP].dport # Destination Port
            print(f"[+] TCP Packet: {ip_src}:{tcp_sport} --> {ip_dst}:{tcp_dport}")

        elif scapy.UDP in packet:
            udp_sport = packet[scapy.UDP].sport
            udp_dport = packet[scapy.UDP].dport
            print(f"[+] UDP Packet: {ip_src}:{udp_sport} --> {ip_dst}:{udp_dport}")

        elif scapy.ICMP in packet:
            # ICMP doesn't have ports, it has types (e.g., echo request)
            print(f"[+] ICMP Packet: {ip_src} --> {ip_dst}")
        
        else:
            # Other IP packets
            print(f"[+] IP Packet: {ip_src} --> {ip_dst}")
            
def start_sniffing(interface, filter_str=None, count=0):
    """
    Main function for sniffer module
    """

    print(f"[*] Starting sniffer on interface '{interface}'...")
    
    try:
        scapy.sniff(
            iface=interface,
            filter=filter_str,
            prn=_packet_callback,
            count=count,
            store=False
        )
    except Exception as e:
        print(f"[ERROR] Sniffer failed to start: {e}")