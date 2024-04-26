import psutil
import platform
from datetime import datetime

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
        
def process_information():
    print("="*40, "System Information", "="*40)
    uname = platform.uname()
    system = f"System: {uname.system}"
    node = f"Node Name: {uname.node}"
    release = f"Release: {uname.release}"
    version = f"Version: {uname.version}"
    machine = f"Machine: {uname.machine}"
    processor = f"Processor: {uname.processor}"
    print(f"{system}\n{node}\n{release}\n{version}\n{machine}\n{processor}\n\n")
    print("="*40, "Boot Time", "="*40)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    print(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}\n\n")
    print("="*40, "Memory Information", "="*40)
    virtual_mem = psutil.virtual_memory()
    total_memory = f"Total: {get_size(virtual_mem.total)}"
    available_memory = f"Available: {get_size(virtual_mem.available)}"
    used_memory = f"Used: {get_size(virtual_mem.used)}"
    percentage_memory = f"Percentage: {virtual_mem.percent}%"
    print(f"{total_memory}\n{available_memory}\n{used_memory}\n{percentage_memory}\n\n")
    print("="*40, "Network Information", "="*40)
    ip_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in ip_addrs.items():
        for address in interface_addresses:
            print(f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")
        net_io = psutil.net_io_counters()
        get_size_of_io = f"Total Bytes Sent: {get_size(net_io.bytes_sent)}"
        get_size_of_io2 = f"Total Bytes Received: {get_size(net_io.bytes_recv)}"
        print(f"{get_size_of_io}\n{get_size_of_io2}\n\n")
        
process_information = process_information()
print(process_information)