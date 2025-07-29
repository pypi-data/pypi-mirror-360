import os
import time

def get_process_info(pid):
	proc_path = f"/proc/{pid}"
	if not os.path.exists(proc_path):
		return {"error": f"Process {pid} is no longer running."}

	try:
		with open(f"{proc_path}/cmdline", "rb") as f:
			name = f.read().split(b'\x00')[0].decode(errors='ignore').strip()

		with open(f"{proc_path}/stat") as f:
			stat = f.read().split()
			start_time_ticks = int(stat[21])
			num_threads = stat[19]

		uptime_seconds = _get_uptime_seconds(start_time_ticks)
		exe_path = os.readlink(f"{proc_path}/exe")

		with open(f"{proc_path}/status") as f:
			status = f.read()
		uid_line = next((line for line in status.splitlines() if line.startswith("Uid:")), "")
		gid_line = next((line for line in status.splitlines() if line.startswith("Gid:")), "")
		vmrss_line = next((line for line in status.splitlines() if line.startswith("VmRSS:")), "")

		return {
			"pid": pid,
			"name": name,
			"status": "Running",
			"uptime": uptime_seconds,
			"uid": uid_line[5:].strip(),
			"gid": gid_line[5:].strip(),
			"memory": vmrss_line[7:].strip() if vmrss_line else "N/A",
			"threads": num_threads,
			"exe": exe_path
		}

	except Exception as e:
		return {"error": f"Failed to retrieve info: {e}"}

def _get_uptime_seconds(start_time_ticks):
	with open("/proc/uptime") as f:
		uptime = float(f.readline().split()[0])
	clk_tck = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
	process_start_time = start_time_ticks / clk_tck
	return uptime - process_start_time