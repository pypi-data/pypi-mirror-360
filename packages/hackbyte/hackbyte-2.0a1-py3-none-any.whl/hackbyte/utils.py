import os
from . import logs as LOG

def read_memory_regions(pid):
	maps = f"/proc/{pid}/maps"
	regions = []
	try:
		with open(maps, 'r', encoding='utf-8', errors='ignore') as f:
			for line in f:
				parts = line.split()
				if len(parts) < 5 or 'r' not in parts[1]:
					continue
				addr = parts[0]
				start, end = [int(x, 16) for x in addr.split('-')]
				regions.append((start, end))
	except Exception as e:
		LOG.error(f"Failed to read maps: {e}")
	return regions

def list_processes(keyword=None):
	print("PID\tNAME")
	for pid in filter(str.isdigit, os.listdir("/proc")):
		try:
			with open(f"/proc/{pid}/cmdline", 'r') as f:
				name = f.read().strip().replace('\0', ' ')
				if not name:
					continue
				if keyword is None or keyword.lower() in name.lower():
					print(f"{pid}\t{name}")
		except:
			continue

def find_pid_by_name(name):
	for pid in filter(str.isdigit, os.listdir("/proc")):
		try:
			with open(f"/proc/{pid}/cmdline", 'r') as f:
				cmd = f.read().strip().replace('\0', ' ')
				if name in cmd:
					return int(pid)
		except:
			continue
	return None

def scan_memory(pid, regions, value):
	matches = []
	with open(f"/proc/{pid}/mem", 'rb', 0) as mem:
		for start, end in regions:
			try:
				mem.seek(start)
				chunk = mem.read(end - start)
				offset = chunk.find(value)
				while offset != -1:
					matches.append((start + offset, value))
					offset = chunk.find(value, offset + 1)
			except:
				continue
	return matches

def write_memory(pid, address, value):
	with open(f"/proc/{pid}/mem", 'rb+', 0) as mem:
		mem.seek(address)
		mem.write(value)

def read_memory_value(pid, address, size):
	with open(f"/proc/{pid}/mem", 'rb', 0) as mem:
		mem.seek(address)
		return mem.read(size)

