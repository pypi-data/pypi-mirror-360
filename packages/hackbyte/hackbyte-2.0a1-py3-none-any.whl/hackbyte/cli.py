import cmd, getpass, os
from . import logs as LOG
from .scanner import MemoryScanner
from .memeditor import MemoryEditor
from .dummyproc import DummyProcess
from .utils import list_processes, find_pid_by_name
from hackbyte.info import get_process_info
from .version import __version__
from .ansi_colors import Fore as F, Style as S

class HackByteShell(cmd.Cmd):
	user_str = (F.BRIGHT_RED if getpass.getuser() == "root" else F.BLUE) + getpass.getuser()
	logo = f"""
{S.BOLD}{F.RED}    __  __           __   ____        __	 
   / / / /___ ______/ /__/ __ )__  __/ /____ 
  / /_/ / __ `/ ___/ //_/ /_/ / / / / __/ _ \\
{F.WHITE} / __  / /_/ / /__/ ,< / /_/ / /_/ / /_/  __/
/_/ /_/\\__,_/\\___/_/|_/_____/\\__, /\\__/\\___/ 
      {S.RESET}Maintained By {S.BOLD}Dx4Grey{S.BOLD} /____/{S.RESET} v{S.BOLD}{__version__}{S.RESET}\n"""
	intro = f"{logo}\nWelcome Hacker!! Type \"help\" or \"?\" for help."
	prompt = f"{user_str}@hackbyte{S.RESET}> "
	
	def __init__(self):
		super().__init__()
		self.proc = None
		self.scanner = None
		self.editor = None

	def do_ls(self, arg):
		"""List active processes. Usage: ls [keyword]"""
		try:
			keyword = arg.strip() if arg else None
			list_processes(keyword)
		except Exception as e:
			LOG.error(f"Failed to list processes: {e}")

	def do_attach(self, pid_or_name):
		"Attach to a process by PID or name: attach <pid|name>"
		try:
			if not pid_or_name:
				LOG.info("Usage: attach <pid|name>")
				return
			if pid_or_name.isdigit():
				pid = int(pid_or_name)
			else:
				pid = find_pid_by_name(pid_or_name)
				if pid is None:
					LOG.error("Process not found.")
					return
			self.proc = pid
			self.scanner = MemoryScanner(pid)
			self.editor = MemoryEditor(pid)
			LOG.success(f"Attached to PID {pid}")
		except Exception as e:
			LOG.error(f"Failed to attach: {e}")

	def do_kill(self, pid_or_name):
		"Kill a process by PID or name: kill <pid|name>"
		try:
			if not pid_or_name:
				LOG.info("Usage: kill <pid|name>")
				return
			pid = int(pid_or_name) if pid_or_name.isdigit() else find_pid_by_name(pid_or_name)
			if pid is None:
				LOG.error("Process not found.")
				return
			os.kill(pid, 9)
			LOG.success(f"Killed process {pid}")
		except Exception as e:
			LOG.error(f"Failed to kill process: {e}")

	def do_scan(self, arg):
		"Scan value: scan <type> <value>"
		if not self.scanner:
			LOG.error("Not attached to any process yet.")
			return
		args = arg.split()
		if len(args) < 2:
			LOG.info("Usage: scan <type> <value>")
			return
		type_, value = args[0], ' '.join(args[1:])
		try:
			self.scanner.first_scan(type_, value)
		except Exception as e:
			LOG.error(f"Scan failed: {e}")

	def do_refine(self, arg):
		"Refine scan results: refine <type> <value>"
		if not self.scanner or not self.scanner.results:
			LOG.error("No results to refine.")
			return
		args = arg.split()
		if len(args) < 2:
			LOG.info("Usage: refine <type> <value>")
			return
		type_, value = args[0], ' '.join(args[1:])
		try:
			self.scanner.refine_scan(type_, value)
		except Exception as e:
			LOG.error(f"Refine failed: {e}")

	def do_results(self, arg):
		"Show last scan results: results"
		if not self.scanner or not self.scanner.results:
			LOG.error("No scan results yet.")
			return
		try:
			for i, (addr, val) in enumerate(self.scanner.results):
				LOG.info(f"[{i}] {hex(addr)} => {val}")
		except Exception as e:
			LOG.error(f"Failed to show results: {e}")

	def do_edit(self, arg):
		"Edit memory value by index or *: edit <index|*> <new_value>"
		args = arg.strip().split()
		if len(args) < 2:
			LOG.info("Usage: edit <index|*> <new_value>")
			return
		if not self.scanner or not self.scanner.results:
			LOG.error("No scan results found.")
			return
		index_or_all, new_val = args[0], args[1]
		try:
			if index_or_all == '*':
				for i, (addr, _) in enumerate(self.scanner.results):
					self.editor.edit_direct(addr, new_val)
					LOG.success(f"Edited result {i} at {hex(addr)} → {new_val}")
			else:
				index = int(index_or_all)
				if index < 0 or index >= len(self.scanner.results):
					LOG.error(f"Invalid index. Found {len(self.scanner.results)} result(s).")
					return
				addr, _ = self.scanner.results[index]
				self.editor.edit_direct(addr, new_val)
				LOG.success(f"Edited address {hex(addr)} → {new_val}")
		except Exception as e:
			LOG.error(f"Edit failed: {e}")

	def do_freeze(self, arg):
		"Freeze memory value by index or *: freeze <index|*>"
		args = arg.strip().split()
		if len(args) < 1:
			LOG.info("Usage: freeze <index|*>")
			return
		if not self.scanner or not self.scanner.results:
			LOG.error("No scan results found.")
			return
		index_or_all = args[0]
		try:
			if index_or_all == '*':
				for i, (addr, val) in enumerate(self.scanner.results):
					self.editor.freeze_direct(addr, val)
					LOG.success(f"Freezing result {i} at {hex(addr)}")
			else:
				index = int(index_or_all)
				if index < 0 or index >= len(self.scanner.results):
					LOG.error(f"Invalid index. Found {len(self.scanner.results)} result(s).")
					return
				addr, val = self.scanner.results[index]
				self.editor.freeze_direct(addr, val)
				LOG.success(f"Freezing address {hex(addr)}")
		except Exception as e:
			LOG.error(f"Freeze failed: {e}")

	def do_script(self, path):
		"Execute a HackByte script file (supports HackByte & bash commands)."
		if not path:
			LOG.info("Usage: script <file_path>")
			return
		if not os.path.isfile(path):
			LOG.error(f"Script file not found: {path}")
			return
		try:
			with open(path) as f:
				for line in f:
					line = line.strip()
					if not line or line.startswith("#"):
						continue
					if line.startswith("!"):
						os.system(line[1:])
					else:
						print(f"{self.prompt}{line}")
						self.onecmd(line)
		except Exception as e:
			LOG.info(f"Failed to execute script: {e}")

	def do_save(self, arg):
		"Save scan results: save <filename>"
		if not self.scanner or not self.scanner.results:
			LOG.info("No scan results to save.")
			return
		if not arg:
			LOG.info("Usage: save <filename>")
			return
		try:
			self.scanner.save_results(arg)
		except Exception as e:
			LOG.error(f"Save failed: {e}")

	def do_load(self, arg):
		"Load scan results from file: load <filename>"
		if not arg:
			LOG.info("Usage: load <filename>")
			return
		try:
			self.scanner.load_results(arg)
		except Exception as e:
			LOG.error(f"Load failed: {e}")

	def do_dummy(self, arg):
		"Use dummy mode for testing without root"
		try:
			self.proc = DummyProcess()
			self.scanner = MemoryScanner(self.proc)
			self.editor = MemoryEditor(self.proc)
			LOG.success("Dummy process is active for simulation.")
		except Exception as e:
			LOG.error(f"Failed to activate dummy mode: {e}")

	def do_clear(self, arg):
		"Clear terminal screen"
		try:
			print("c", end="")
		except Exception as e:
			LOG.error(f"Failed to clear screen: {e}")

	def do_info(self, arg):
		"Show info about the currently attached process"
		if not self.proc:
			LOG.error("No process is currently attached.")
			return
		try:
			info = get_process_info(self.proc)
			if 'error' in info:
				LOG.error(f"{info['error']}")
			else:
				LOG.info_plus(f"PID		: {info['pid']}")
				LOG.info_plus(f"Name	: {info['name']}")
				LOG.info_plus(f"Status	: {info['status']}")
				LOG.info_plus(f"Uptime	: {info['uptime']:.1f} seconds")
				LOG.info_plus(f"UID/GID	: {info['uid']} / {info['gid']}")
				LOG.info_plus(f"Memory	: {info['memory']}")
				LOG.info_plus(f"Threads	: {info['threads']}")
				LOG.info_plus(f"Executable	: {info['exe']}")
		except Exception as e:
			LOG.error(f"Failed to get process info: {e}")

	def do_fuzzy(self, arg):
		"Fuzzy memory search: fuzzy start <type> | fuzzy increased | fuzzy decreased"
		args = arg.strip().split()
		if not self.scanner:
			LOG.error("Not attached to any process.")
			return
		if not args:
			LOG.info("Usage: fuzzy start <type> | fuzzy increased | fuzzy decreased")
			return
		try:
			if args[0] == "start" and len(args) == 2:
				self.scanner.fuzzy_start(args[1])
			elif args[0] in ["increased", "decreased"]:
				self.scanner.fuzzy_filter(args[0])
			else:
				LOG.error("Invalid fuzzy command.")
		except Exception as e:
			LOG.error(f"Fuzzy search failed: {e}")
			
	def do_help(self, arg):
		if arg:
			print()
			cmd_func = getattr(self, f"do_{arg}", None)
			if cmd_func and cmd_func.__doc__:
				LOG.info_plus(f"Help for command '{arg}':")
				print(f"{S.RESET}{cmd_func.__doc__}")
			else:
				LOG.warn(f"No help available for '{arg}'")
		else:
			LOG.info_plus("Available Commands:")
		
			commands = sorted(
				(cmd[3:], getattr(self, cmd).__doc__ or "No description")
				for cmd in dir(self) if cmd.startswith("do_")
			)
		
			for name, doc in commands:
				first_line = doc.strip().splitlines()[0] if doc else ""
				print(f"  {name:<10} {first_line}")
				
	def do_exit(self, arg):
		"Exit the program"
		LOG.info("Exiting...")
		return True