import threading
import time
from .valuetypes import parse_value
from .utils import write_memory

class MemoryEditor:
	def __init__(self, pid):
		self.pid = pid
		self.freezes = []

	def edit_direct(self, address, new_value):
		val = parse_value('dword', new_value)  # default dword
		write_memory(self.pid, address, val)

	def freeze_direct(self, address, value):
		val = parse_value('dword', value)
		self.freezes.append((address, val))
		threading.Thread(target=self._freeze_loop, daemon=True).start()

	def _freeze_loop(self):
		while True:
			for addr, val in self.freezes:
				write_memory(self.pid, addr, val)
			time.sleep(0.5)