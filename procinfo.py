import argparse
import datetime
import psutil
import time
import pandas as pd
import os

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', default='output.json', help='output file name')
    parser.add_argument('--columns', '-c',  help='Input Columns',  default="name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,nice,n_threads,cores")
    parser.add_argument('--sort_by', '-s', dest='sort_by', help='Sort Between ascending or descending', default="memory_usage")
    parser.add_argument("-n", help="Number of processes to show, will show all if 0 is specified, default is 25 .", default=25)
    parser.add_argument("-u", "--update", action="store_true", help="Whether to keep the program on and updating process information each second")
    args = parser.parse_args()
    return args

def get_process():
    process = []
    for proc in psutil.process_iter():
        with proc.oneshot():
            pid = proc.pid
            if pid == 0:
                continue
            name = proc.name()
            try:
                create_time = datetime.datetime.fromtimestamp(proc.create_time())
            except OSError:
                create_time = datetime.datetime.fromtimestamp(psutil.boot_time())
                
            status = proc.status()
            try:
                s_nice = int(proc.nice())
            except psutil.AccessDenied:
                s_nice = 0
                
            try:
                # get the memory usage in bytes
                memory_usage = proc.memory_full_info().uss
            except psutil.AccessDenied:
                memory_usage = 0
            cpu_usage = proc.cpu_percent()    
            num_threads = proc.num_threads()
            io_counters = proc.io_counters()
            read_bytes = io_counters.read_bytes
            write_bytes = io_counters.write_bytes
            username = proc.username()
            if username == psutil.AccessDenied:
                username = "N/A"
            process.append({'pid':pid, 'cpu_usage':cpu_usage, 'memory_usage':memory_usage, 'name':name, 'create_time':create_time, 'status':status, 's_nice':s_nice, 
                         'num_threads':num_threads, 'read_bytes':read_bytes, 'write_bytes':write_bytes, 'username':username})
        return process
    
def construct_dataframes_for_processes(process):
    df = pd.DataFrame(process)
    df.set_index('pid', inplace=True)
    df.sort_values(sort_by, inplace=True, ascending=False)
    df['memory_usage'] = df['memory_usage'].apply(get_size)
    df['write_bytes'] = df['write_bytes'].apply(get_size)
    df['read_bytes'] = df['read_bytes'].apply(get_size)
    #df['create_time'] = df['create_time'].apply(datetime.datetime.strftime, args=("%Y-%m-%d %H:%M:%S"))
    df = df[columns.split(",")]
    return df
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

arguments = get_args()
columns = arguments.columns
sort_by = arguments.sort_by
number_of_processes = int(arguments.n)
update = arguments.update
output_file = arguments.output

process_info = get_process()
df = construct_dataframes_for_processes(process_info)
if number_of_processes == 0:
    print(df.to_string())
elif number_of_processes > 0:
    print(df.head(number_of_processes).to_string())
while update:
    time.sleep(1)
    process_info = get_process()
    df = construct_dataframes_for_processes(process_info)
    os.system("cls") if "nt" in os.name else os.system("clear")
    if number_of_processes == 0:
        print(df.to_string())
    elif number_of_processes > 0:
        print(df.head(number_of_processes).to_string())
    time.sleep(1)
        