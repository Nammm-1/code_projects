import socket
import threading
import argparse
from queue import Queue

open_ports = []

# Banner grabbing function
def grab_banner(host, port):
    try:
        with socket.create_connection((host, port), timeout=1) as sock:
            sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = sock.recv(1024).decode().strip()
            return banner
    except:
        return ""

# Worker thread for scanning
def scan_worker(host, q):
    while not q.empty():
        port = q.get()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                result = sock.connect_ex((host, port))
                if result == 0:
                    banner = grab_banner(host, port)
                    service = socket.getservbyport(port, 'tcp') if port in range(1, 1025) else "Unknown"
                    print(f"[+] Port {port} OPEN ({service.upper()}) Banner: {banner}")
                    open_ports.append((port, service.upper(), banner))
        except Exception:
            pass
        finally:
            q.task_done()

# Main function
def main():
    parser = argparse.ArgumentParser(description="Multithreaded Port Scanner with Banner Grabbing")
    parser.add_argument("host", help="Target hostname or IP")
    parser.add_argument("-p", "--ports", help="Port range (e.g., 1-1000)", default="1-1024")
    parser.add_argument("-t", "--threads", help="Number of threads", type=int, default=100)
    args = parser.parse_args()

    # Resolve host and port range
    host = args.host
    start_port, end_port = map(int, args.ports.split('-'))

    print(f"Scanning {host} from port {start_port} to {end_port}...")

    # Create a queue of ports
    q = Queue()
    for port in range(start_port, end_port + 1):
        q.put(port)

    # Start worker threads
    for _ in range(args.threads):
        thread = threading.Thread(target=scan_worker, args=(host, q), daemon=True)
        thread.start()

    q.join()

    # Summary
    if open_ports:
        print("\nSummary of open ports:")
        for port, service, banner in sorted(open_ports):
            print(f"Port {port}: {service} | Banner: {banner}")
    else:
        print("\nNo open ports found.")

if __name__ == "__main__":
    main()