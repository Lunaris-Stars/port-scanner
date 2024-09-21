import socket
import concurrent.futures
from urllib.parse import urlparse

def scan_port(domain, port):
    try:
        hostname = urlparse(domain).hostname
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)  # set timeout to 0.5 seconds
        result = sock.connect_ex((hostname, port))
        if result == 0:
            print(f"Port {port} is open")
            service = socket.getservbyport(port, 'tcp')
            print(f"Service: {service}")
            banner = get_banner(sock)
            if banner:
                print(f"Banner: {banner}")
            sock.close()
            return port, service, banner
        sock.close()
    except socket.gaierror:
        print(f"Hostname {hostname} could not be resolved.")
    except socket.error:
        print(f"Couldn't connect to server {hostname}")
    return None

def get_banner(sock):
    try:
        sock.send(b'\r\n')
        banner = sock.recv(1024).decode().strip()
        return banner
    except socket.error:
        return None

def scan_ports(domain, start_port, end_port):
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(scan_port, domain, port) for port in range(start_port, end_port + 1)]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                open_ports.append(result)
    return open_ports

domain = input("Enter the domain: ")
start_port = 1
end_port = 65535  # maximum possible port number

open_ports = scan_ports(domain, start_port, end_port)
print(f"Open ports on {domain}:")
for port, service, banner in open_ports:
    print(f"Port {port}: {service} - {banner}")