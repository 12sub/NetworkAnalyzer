from scapy.all import *
import psutil
from collections import defaultdict
import os
from threading import Thread
import pandas as pd

LOG_FILE = "ProcessNic.csv"
#Getting all network adapters MAC Address
all_mac_addr = {iface.mac for iface in ifaces.values()}
print(all_mac_addr)
connection2pid = {}

#Creating a dictionary to map each process ID (PID) to total uploads and downloads traffic
process_traffic = defaultdict(lambda: [0,0])
global_df = None
is_program_running = True

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
def process_packet(packet):
    global process_traffic
    try:
        #Getting packet source and destination IP addresses and ports
        packet_conn = (packet.sport, packet.dport)
    except (AttributeError, IndexError):
        #If the packet doesn't have source or destination IP addresses or ports, skip it
        pass
    else:
        #Getting packet source and destination MAC addresses
        packet_src_mac = connection2pid.get(packet_conn)
        if packet_src_mac:
            if packet.src in all_mac_addr:
                process_traffic[packet_src_mac][0] += len(packet)
            else:
                
                process_traffic[packet_src_mac][1] += len(packet)
def get_conns():
    global connection2pid
    while is_program_running:
        #using psutil, we can grab each connection's source and destination ports
        for c_stats in psutil.net_connections():
            if c_stats.laddr and c_stats.raddr and c_stats.pid:
                connection2pid[(c_stats.laddr.port, c_stats.raddr.port)] = c_stats.pid
                connection2pid[(c_stats.raddr.port, c_stats.laddr.port)] = c_stats.pid
        time.sleep(1)
        
def print_pidToTraffic():
    global global_df
    processes = []
    for pid, traffic in process_traffic.items():
        try:
            #get the process object from psutil
            p_util = psutil.Process(pid)
            name = p_util.name()
            try:
                create_time = datetime.fromtimestamp(p_util.create_time())
            except OSError:
                create_time = datetime.fromtimestamp(psutil.boot_time())
            process = {
                'pid': pid,
                'Name': name,
                'Create Time': create_time,
                'Upload': traffic[0],
                'Download': traffic[1]
            }
            try:
                process["Upload Speed"] = traffic[0] - global_df.at[pid, "Upload"]
                process["Download Speed"] = traffic[1] - global_df.at[pid, "Download"]
            except KeyError:
                process["Upload Speed"] = traffic[0]
                process["Download Speed"] = traffic[1]
            processes.append(process)
        except psutil.NoSuchProcess:
            #if the process is no longer running, skip it
            break
        
    df = pd.DataFrame(processes)
    try:
        # set the PID as the index of the dataframe
        df = df.set_index("pid")
        #sort by column, feel free to edit the column
        df = df.sort_values(by=["Upload Speed"], ascending=False, inplace=True)
    except KeyError:
        pass
    print_df = df.copy()
    try:
        print_df["Download"] = print_df["Download"].apply(get_size)
        print_df["Upload"] = print_df["Upload"].apply(get_size)
        print_df["Download Speed"] = print_df["Download Speed"].apply(get_size).apply(lambda s: f"{s}/s")
        print_df["Upload Speed"] = print_df["Upload Speed"].apply(get_size).apply(lambda s: f"{s}/s")
    except KeyError:
        pass
    os.system("cls") if "nt" in os.name else os.system("clear")
    # print our dataframe
    print(print_df.to_string())
    print(print_df.to_csv(index=True))
    # update the global df to our dataframe
    global_df = df
    
def stats():
    while is_program_running:
        time.sleep(1)
        print_pidToTraffic()

if __name__ == "__main__":
    #start a thread to get the connection information
    conn_thread = Thread(target=stats)
    conn_thread.start()
    connection_thread = Thread(target=get_conns)
    connection_thread.start()
    print("Start Sniffing!")
    sniff(prn=process_packet, store=False)
    is_program_running = False