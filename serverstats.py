import psutil
import json
from datetime import datetime

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    mem = psutil.virtual_memory()
    return {
        "total_mb": round(mem.total / (1024 * 1024), 2),
        "used_mb": round(mem.used / (1024 * 1024), 2),
        "percent": mem.percent
    }

def get_disk_usage():
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "percent": usage.percent
            })
        except PermissionError:
            continue
    return disks

def get_load_average():
    try:
        return {
            "1min": psutil.getloadavg()[0],
            "5min": psutil.getloadavg()[1],
            "15min": psutil.getloadavg()[2],
        }
    except:
        return "Not supported on this OS"

def get_top_processes(limit=5):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(proc.info)

    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    top_mem = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:limit]

    return {
        "top_cpu": top_cpu,
        "top_memory": top_mem
    }

def collect_stats():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": get_cpu_usage(),
        "memory": get_memory_usage(),
        "disk": get_disk_usage(),
        "load_avg": get_load_average(),
        "processes": get_top_processes()
    }

def print_stats(stats):
    print("===== Server Performance Stats =====")
    print(f"Timestamp: {stats['timestamp']}")
    print(f"CPU Usage: {stats['cpu_percent']}%")

    mem = stats['memory']
    print(f"Memory Usage: {mem['used_mb']}MB / {mem['total_mb']}MB ({mem['percent']}%)")

    print("\nDisk Usage:")
    for d in stats['disk']:
        print(f"{d['device']} ({d['mountpoint']}): {d['used_gb']}GB / {d['total_gb']}GB ({d['percent']}%)")

    print("\nLoad Average:", stats['load_avg'])

    print("\nTop Processes by CPU:")
    for p in stats['processes']['top_cpu']:
        print(f"{p['pid']} - {p['name']} | CPU: {p['cpu_percent']}% | MEM: {p['memory_percent']:.2f}%")

    print("\nTop Processes by Memory:")
    for p in stats['processes']['top_memory']:
        print(f"{p['pid']} - {p['name']} | CPU: {p['cpu_percent']}% | MEM: {p['memory_percent']:.2f}%")

    print("====================================")

if __name__ == "__main__":
    stats = collect_stats()
    print_stats(stats)

    # Optional: Save as JSON
    with open("server_stats.json", "w") as f:
        json.dump(stats, f, indent=4)