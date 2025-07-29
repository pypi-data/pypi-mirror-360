# syn_apse/cli.py

import argparse
from .modules import sniffer  # We import the whole modules package
from .core import start_mitm_attack 
from .core import start_dns_spoofer 

def main():
    parser = argparse.ArgumentParser(
        prog="syn-apse",
        description="A modular Man-in-the-Middle toolkit for network analysis.",
        epilog="Use 'syn-apse <command> --help' for more information on a specific command."
    )
    
    # This creates the sub-command system
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # Sniffer Command
    parser_sniff = subparsers.add_parser('sniff', help='Run the network packet sniffer.')
    parser_sniff.add_argument(
        '-i', '--interface', 
        required=True, 
        help="The network interface to sniff on (e.g., eth0, en0)."
    )
    parser_sniff.add_argument(
        '-f', '--filter', 
        help="BPF filter for sniffing (e.g., 'tcp port 80')."
    )
    parser_sniff.add_argument(
        '-c', '--count', 
        type=int, 
        default=0, 
        help="Number of packets to capture (0 for unlimited)."
    )

    parser_mitm = subparsers.add_parser('mitm', help='Run a full MitM attack (ARP spoof + Sniffer).')
    parser_mitm.add_argument('-t', '--target', required=True, help="The IP address of the target device.")
    parser_mitm.add_argument('-g', '--gateway', required=True, help="The IP address of the network gateway/router.")
    parser_mitm.add_argument('-i', '--interface', required=True, help="The network interface to use.")

    parser_dns_spoofer = subparsers.add_parser('dns_spoof', help='Run a DNS Spoofing attack (ARP spoof + DNS spoof).')
    parser_dns_spoofer.add_argument('-t', '--target', required=True, help="The IP address of the target device.")
    parser_dns_spoofer.add_argument('-g', '--gateway', required=True, help="The IP address of the network gateway/router.")
    parser_dns_spoofer.add_argument('-i', '--interface', required=True, help="The network interface to use.")
    parser_dns_spoofer.add_argument('-d', '--domain', required=True, help="The domain to spoof.")

    # For ARP spoofing
    parser_spoof = subparsers.add_parser('spoof', help='Run an ARP spoofing attack.')


    # Parse the arguments provided by the user
    args = parser.parse_args()

    # Execute the appropriate function based on the command
    if args.command == 'sniff':
        try:
            # Call the function from our sniffer module
            sniffer.start_sniffing(args.interface, args.filter, args.count)
        except PermissionError:
            print("[ERROR] Permission denied. Packet sniffing requires root privileges. Try running with 'sudo'.")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred: {e}")
    elif args.command == 'spoof':
        print("Spoof module not yet implemented.")
    elif args.command == "dns_spoof":
        try:
            start_dns_spoofer(args.target, args.gateway, args.interface, args.domain)
        except PermissionError:
            print(f"[ERROR] Permission denied; try running with sudo")
        except KeyboardInterrupt:
            print("\n[+] Ctrl+C detected. Shutting down...")
        
    elif args.command == "mitm":
        try:
            start_mitm_attack(args.target, args.gateway, args.interface)
        except PermissionError:
            print(f"[ERROR] Permission denied; try running with sudo")
        except KeyboardInterrupt:
            print("\n[+] Ctrl+C detected. Shutting down...")
            
            
if __name__ == "__main__":
    main()
