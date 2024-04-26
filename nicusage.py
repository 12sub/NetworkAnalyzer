import psutil
import os
import time
import pandas as pd

UPDATE_DELAY = 1.2
LOG_FILE = "log.csv"
LOG_HEADER = ["time", "cpu_percent", "memory_percent", "disk_percent"]

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
        
def ntwk_usage():
    io = psutil.net_io_counters(pernic=True)
    while True:
        time.sleep(UPDATE_DELAY)
        io2 = psutil.net_io_counters(pernic=True)
        data = []
        for iface, iface_io in io2.items():
            upload_speed, download_speed = io2[iface].bytes_sent - iface_io.bytes_sent, io2[iface].bytes_recv - iface_io.bytes_recv
            data.append({
                "iface": iface,
                "Download": get_size(io2[iface].bytes_recv),
                "Upload": get_size(io2[iface].bytes_sent),
                "upload_speed": f"{get_size(upload_speed / UPDATE_DELAY)}/s",
                "download_speed": f"{get_size(download_speed/ UPDATE_DELAY)}/s"
            })
        io = io2
        df = pd.DataFrame(data)
        file = df.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE))
        df.sort_values(by=['Download'], ascending=False, inplace=True)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(df.to_string(index=False))
        print(file)
        
if __name__ == "__main__":
    ntwk_usage()