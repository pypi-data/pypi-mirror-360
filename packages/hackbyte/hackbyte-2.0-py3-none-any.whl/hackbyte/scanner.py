import json
from . import logs as LOG
from .valuetypes import parse_value, parse_value_type
from .utils import read_memory_regions, scan_memory, read_memory_value

class MemoryScanner:
	def __init__(self, pid):
		self.pid = pid
		self.results = []
		self.fuzzy_results = []

	def first_scan(self, type_, value):
		val_bytes = parse_value(type_, value)
		regions = read_memory_regions(self.pid)
		self.results = scan_memory(self.pid, regions, val_bytes)
		LOG.success(f"Found {len(self.results)} results.")

	def refine_scan(self, type_, value):
		new_val = parse_value(type_, value)
		refined = []
		for addr, _ in self.results:
			try:
				mem_val = read_memory_value(self.pid, addr, len(new_val))
				if mem_val == new_val:
					refined.append((addr, mem_val))
			except OSError as e:
				continue
		self.results = refined
		LOG.success(f"Results after refining: {len(self.results)}")

	def save_results(self, filename):
		with open(filename, 'w') as f:
			json.dump(self.results, f)
		LOG.success(f"Saved to {filename}")

	def load_results(self, filename):
		with open(filename, 'r') as f:
			self.results = json.load(f)
		LOG.success(f"Loaded from {filename}")
		
	def fuzzy_start(self, valtype):
		self.fuzzy_type = valtype
		val_parser = parse_value_type(valtype)
		regions = read_memory_regions(self.pid)
		self.fuzzy_results = []
	
		for start, end in regions:
			addr = start
			while addr < end:
				try:
					raw = read_memory_value(self.pid, addr, val_parser.size)
					val = val_parser.unpack(raw)
					self.fuzzy_results.append((addr, val))
					addr += val_parser.size
				except:
					addr += val_parser.size
		LOG.success(f"Fuzzy base scan completed. {len(self.fuzzy_results)} addresses recorded.")
	
	def fuzzy_filter(self, direction):
		val_parser = parse_value_type(self.fuzzy_type)
		refined = []
	
		for addr, old_val in self.fuzzy_results:
			try:
				raw = read_memory_value(self.pid, addr, val_parser.size)
				new_val = val_parser.unpack(raw)
				if (direction == "increased" and new_val > old_val) or \
				   (direction == "decreased" and new_val < old_val):
					refined.append((addr, new_val))
			except:
				continue
	
		self.results = refined
		LOG.success(f"Fuzzy refine ({direction}): {len(refined)} results.")