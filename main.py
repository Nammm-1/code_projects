import argparse
from vulnscanner import scan_ports, scan_software, scan_configs, scan_patches, scan_credentials

def main():
    parser = argparse.ArgumentParser(description='Vulnerability Scanner CLI')
    parser.add_argument('--all', action='store_true', help='Run all scans')
    parser.add_argument('--ports', action='store_true', help='Scan for open ports and insecure services')
    parser.add_argument('--software', action='store_true', help='Check for outdated software')
    parser.add_argument('--configs', action='store_true', help='Check for weak configurations')
    parser.add_argument('--patches', action='store_true', help='Check for missing patches')
    parser.add_argument('--credentials', action='store_true', help='Scan for exposed credentials')
    parser.add_argument('--target', type=str, default='127.0.0.1', help='Target IP address or network (default: 127.0.0.1)')
    args = parser.parse_args()

    if args.all or not any([args.ports, args.software, args.configs, args.patches, args.credentials]):
        scan_ports(target=args.target)
        scan_software()
        scan_configs()
        scan_patches()
        scan_credentials()
    else:
        if args.ports:
            scan_ports(target=args.target)
        if args.software:
            scan_software()
        if args.configs:
            scan_configs()
        if args.patches:
            scan_patches()
        if args.credentials:
            scan_credentials()

if __name__ == '__main__':
    main() 