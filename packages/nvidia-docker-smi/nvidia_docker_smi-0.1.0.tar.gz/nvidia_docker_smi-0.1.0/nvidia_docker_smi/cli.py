import os
import sys
import time
import subprocess
from pathlib import Path

CACHE_FILE = "/tmp/container_pids.txt"
CACHE_TTL = 60  # seconds

def run_command(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def refresh_container_pid_map(force_refresh=False):
    cache = Path(CACHE_FILE)
    
    if force_refresh or not cache.exists():
        _rebuild_container_cache()
        return
    
    # Check if any GPU PIDs are missing from cache
    gpu_pids = set()
    pmon_output = run_command("nvidia-smi pmon -c 1")
    for line in pmon_output.splitlines()[1:]:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 8:
            type_ = parts[2]  # Type is the third column
            # Only consider Compute processes, skip Graphics processes
            if type_ != "G":
                gpu_pids.add(parts[1])  # PID is the second column
    
    if gpu_pids:
        container_map = get_container_map()
        missing_pids = gpu_pids - set(container_map.keys())
        if missing_pids:
            _rebuild_container_cache()

def _rebuild_container_cache():
    """Rebuild the container PID cache"""
    lines = []
    docker_ps = run_command("docker ps --format '{{.ID}} {{.Names}} {{.Image}}'")
    for line in docker_ps.splitlines():
        cid, name, image = line.split(maxsplit=2)
        pids = run_command(f"docker top {cid} -eo pid").splitlines()[1:]
        for pid in pids:
            lines.append(f"{pid.strip()}\t{name}\t{image}")
    
    cache = Path(CACHE_FILE)
    cache.write_text("\n".join(lines))

def get_gpu_memory_usage():
    lines = run_command("nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits")
    return {line.split(",")[0].strip(): line.split(",")[1].strip() + "M" for line in lines.splitlines()}

def get_gpu_stats():
    """Get GPU utilization and memory stats in a single command"""
    lines = run_command("nvidia-smi --query-gpu=utilization.gpu,memory.total,memory.used,memory.free --format=csv,noheader,nounits")
    gpu_stats = []
    for line in lines.splitlines():
        util, total, used, free = line.split(", ")
        gpu_stats.append({
            'utilization': util.strip() + "%",
            'total_memory': total.strip() + "M",
            'used_memory': used.strip() + "M", 
            'free_memory': free.strip() + "M"
        })
    return gpu_stats

def get_ps_data():
    lines = run_command("ps -eo pid,user,%cpu,%mem --no-headers")
    data = {}
    for line in lines.splitlines():
        parts = line.split(None, 4)
        data[parts[0]] = {
            "user": parts[1],
            "cpu": parts[2] + "%",
            "mem": parts[3] + "%"
        }
    return data

def get_container_map():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE) as f:
        return {line.split()[0]: (line.split()[1], line.split()[2]) for line in f}

def prepare_data_rows(pid_mem, gpu_stats, ps_data, container_map):
    rows = ["pid,user,proc,type,container,gpu_util,gpu_mem,cpu,mem,gpu"]
    
    pmon_output = run_command("nvidia-smi pmon -c 1")
    for line in pmon_output.splitlines()[1:]:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        if len(parts) < 8:
            continue
        gpu, pid, type_, sm, mem, enc, dec, pname = parts[:8]
            
        gpu_idx = int(gpu)
        gpu_util = gpu_stats[gpu_idx]['utilization'] if gpu_idx < len(gpu_stats) else "N/A"

        ps_info = ps_data.get(pid, {})
        username = ps_info.get("user", "N/A")
        cpu_usage = ps_info.get("cpu", "N/A")
        mem_usage = ps_info.get("mem", "N/A")

        cname, cimage = container_map.get(pid, ("-", "-"))
        if len(cname) > 20:
            cname = cname[:17] + "..."
        used_mem = pid_mem.get(pid, "N/A")

        row = f"{pid},{username},{pname},{type_},{cname},{gpu_util},{used_mem},{cpu_usage},{mem_usage},GPU-{gpu}"
        rows.append(row)
    
    return rows

def display_formatted_output(rows):
    formatted_data = "\n".join(rows)
    os.system(f'echo "{formatted_data}" | column -t -s ,')

def display_gpu_summary():
    """Display GPU utilization and memory usage summary"""
    gpu_stats = get_gpu_stats()
    
    print("\n--- GPU Summary ---")
    for i, stats in enumerate(gpu_stats):
        print(f"GPU-{i}: Util: {stats['utilization']}, Mem: {stats['used_memory']}/{stats['total_memory']} (Free: {stats['free_memory']})")
    print("-------------------\n")

def main():
    debug_mode = "--debug" in sys.argv
    
    start_time = time.time()
    profile_times = {}
    
    # Profile refresh_container_pid_map
    step_start = time.time()
    refresh_container_pid_map()
    profile_times['refresh_container_pid_map'] = time.time() - step_start
    
    # Profile get_gpu_memory_usage
    step_start = time.time()
    pid_mem = get_gpu_memory_usage()
    profile_times['get_gpu_memory_usage'] = time.time() - step_start
    
    # Profile get_gpu_stats
    step_start = time.time()
    gpu_stats = get_gpu_stats()
    profile_times['get_gpu_stats'] = time.time() - step_start
    
    # Profile get_ps_data
    step_start = time.time()
    ps_data = get_ps_data()
    profile_times['get_ps_data'] = time.time() - step_start
    
    # Profile get_container_map
    step_start = time.time()
    container_map = get_container_map()
    profile_times['get_container_map'] = time.time() - step_start
    
    # Profile display_gpu_summary
    step_start = time.time()
    display_gpu_summary()
    profile_times['display_gpu_summary'] = time.time() - step_start
    
    # Profile prepare_data_rows
    step_start = time.time()
    rows = prepare_data_rows(pid_mem, gpu_stats, ps_data, container_map)
    profile_times['prepare_data_rows'] = time.time() - step_start
    
    # Profile display_formatted_output
    step_start = time.time()
    display_formatted_output(rows)
    profile_times['display_formatted_output'] = time.time() - step_start
    
    total_time = time.time() - start_time
    
    # Display profiling results only in debug mode
    if debug_mode:
        print("\n--- Performance Profile ---")
        for step, duration in profile_times.items():
            percentage = (duration / total_time) * 100
            print(f"{step:30}: {duration:8.4f}s ({percentage:5.1f}%)")
        print(f"{'Total execution time':30}: {total_time:8.4f}s")
        print("---------------------------")

if __name__ == "__main__":
    main()