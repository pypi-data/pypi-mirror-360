
import scapy.all as scapy
import argparse 
import time

def get_mac(ip_address, interface, retries=10, timeout=2):
    """
    Gets the MAC address for a given IP, retrying multiple times if it fails.
    """
    print(f"[UTIL] Resolving MAC for {ip_address} on {interface}...")

    arp_request = scapy.ARP(pdst=ip_address)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    for i in range(retries):
        try:
            # Send the packet and wait for a response
            answered_list = scapy.srp(
                arp_request_broadcast,
                iface=interface,
                timeout=timeout,
                verbose=False
            )[0]

            if answered_list:
                mac = answered_list[0][1].hwsrc
                print(f"[UTIL] MAC found: {mac}")
                return mac

        except Exception as e:
            print(f"[WARN] Scapy error on attempt {i + 1}/{retries}: {e}")

        # If no answer to packet
        if i < retries - 1:
            print(f"[WARN] No reply on attempt {i + 1}/{retries}. Retrying...")
            time.sleep(1) # Wait a second before the next attempt

    # If the loop finishes without returning, it has failed all retries
    print(f"[ERROR] Failed to resolve MAC for {ip_address} after {retries} attempts.")
    return None

# Allow for testable CLI
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="MAC Address Fetcher Utility")
    parser.add_argument("-t", "--target", dest="target_ip", help="IP address of the target to find.")
    options = parser.parse_args()

    if not options.target_ip:
        parser.error("[-] Please specify a target IP address, use --help for more info.")

    mac = get_mac(options.target_ip)
    
    if mac:
        print(f"[+] MAC address for {options.target_ip} is {mac}")
    else:
        print(f"[-] Could not get MAC address for {options.target_ip}. The host may be down or on a different network.")


def get_local_ip():
    """
    Get local IP using Scapy routing
    """
    
    try:
        # Get the IP of the interface used for default route
        local_ip = scapy.get_if_addr(scapy.conf.iface)
        return local_ip
    except:
        return None