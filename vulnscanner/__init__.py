import subprocess
import sys
import nmap
import os

def scan_ports(target='127.0.0.1'):
    print(f'[*] Scanning {target} for open ports and insecure services...')
    scanner = nmap.PortScanner()
    # Scan top 1000 ports on the target
    try:
        scanner.scan(target, arguments='-T4 --top-ports 1000')
    except Exception as e:
        print(f'[!] Nmap scan failed: {e}')
        return

    insecure_services = {'ftp', 'telnet', 'rlogin', 'rsh', 'vnc', 'rdp', 'smb', 'snmp', 'pop3', 'imap', 'mysql', 'mssql', 'postgresql', 'mongodb', 'redis'}
    found_insecure = False

    for host in scanner.all_hosts():
        print(f'Host: {host} ({scanner[host].hostname()})')
        for proto in scanner[host].all_protocols():
            lport = scanner[host][proto].keys()
            for port in sorted(lport):
                state = scanner[host][proto][port]['state']
                service = scanner[host][proto][port]['name']
                print(f'  Port {port}/{proto}: {state} ({service})')
                if service in insecure_services and state == 'open':
                    print(f'    [!] Insecure service detected: {service} on port {port}')
                    found_insecure = True
    if not found_insecure:
        print('[+] No insecure services detected on open ports.')

def scan_software():
    print('[*] Checking for outdated software...')
    # Check Homebrew packages
    try:
        brew_out = subprocess.check_output(['brew', 'outdated'], text=True)
        if brew_out.strip():
            print('[!] Outdated Homebrew packages:')
            for line in brew_out.strip().split('\n'):
                print(f'    {line}')
        else:
            print('[+] All Homebrew packages are up to date.')
    except Exception as e:
        print(f'[!] Could not check Homebrew packages: {e}')
    # Check pip packages
    try:
        pip_out = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=columns'], text=True)
        lines = pip_out.strip().split('\n')
        if len(lines) > 2:
            print('[!] Outdated pip packages:')
            for line in lines[2:]:
                print(f'    {line}')
        else:
            print('[+] All pip packages are up to date.')
    except Exception as e:
        print(f'[!] Could not check pip packages: {e}')

def scan_configs():
    print('[*] Checking for weak configurations...')
    # 1. SSH root login
    sshd_config = '/etc/ssh/sshd_config'
    try:
        if os.path.exists(sshd_config):
            with open(sshd_config) as f:
                lines = f.readlines()
            for line in lines:
                if line.strip().lower().startswith('permitrootlogin'):
                    if 'yes' in line.lower():
                        print('[!] SSH root login is enabled in /etc/ssh/sshd_config')
                    else:
                        print('[+] SSH root login is disabled.')
                    break
            else:
                print('[?] Could not find PermitRootLogin setting in sshd_config.')
        else:
            print('[?] SSH config not found.')
    except Exception as e:
        print(f'[!] Error reading SSH config: {e}')
    # 2. World-writable sensitive files
    sensitive_files = ['/etc/passwd', '/etc/shadow']
    for fpath in sensitive_files:
        if os.path.exists(fpath):
            mode = os.stat(fpath).st_mode
            if mode & 0o002:
                print(f'[!] {fpath} is world-writable!')
            else:
                print(f'[+] {fpath} permissions are OK.')
    # 3. SSH keys permissions
    ssh_dir = os.path.expanduser('~/.ssh')
    if os.path.isdir(ssh_dir):
        for fname in os.listdir(ssh_dir):
            fpath = os.path.join(ssh_dir, fname)
            if os.path.isfile(fpath):
                mode = os.stat(fpath).st_mode
                if mode & 0o077:
                    print(f'[!] SSH key or config {fpath} is too permissive!')
    # 4. Guest user enabled
    try:
        guest_info = subprocess.check_output(['dscl', '.', '-read', '/Users/Guest'], text=True)
        if 'Record not found' in guest_info:
            print('[+] Guest user is disabled.')
        else:
            print('[!] Guest user is enabled!')
    except subprocess.CalledProcessError:
        print('[+] Guest user is disabled.')
    except Exception as e:
        print(f'[?] Could not check guest user: {e}')
    # 5. Firewall status
    try:
        fw = subprocess.check_output(['/usr/libexec/ApplicationFirewall/socketfilterfw', '--getglobalstate'], text=True)
        if 'enabled' in fw.lower():
            print('[+] Firewall is enabled.')
        else:
            print('[!] Firewall is disabled!')
    except Exception as e:
        print(f'[?] Could not check firewall status: {e}')

def scan_patches():
    print('[*] Checking for missing patches...')
    # TODO: Implement missing patch checks
    pass

def scan_credentials():
    print('[*] Scanning for exposed credentials...')
    # TODO: Implement credential exposure checks
    pass 