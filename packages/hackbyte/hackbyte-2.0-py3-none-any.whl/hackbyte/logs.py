from .ansi_colors import Fore as F, Style as S

def success(msg):
	print(f"{F.GREEN}[+] {S.RESET}{msg}")

def error(msg):
	print(f"{F.RED}[-] {S.RESET}{msg}")

def warn(msg):
	print(f"{F.YELLOW}[!] {S.RESET}{msg}")

def info(msg):
	print(f"{F.CYAN}[i] {S.RESET}{msg}")

def info_plus(msg):
	"""Info with [+] tag in blue (not green)."""
	print(f"{F.BLUE}[+] {S.RESET}{msg}")

def custom(tag, msg, color):
	"""
	tag: string like 'DEBUG', 'NOTE', etc.
	msg: the message string
	color: ansi_colors.Fore color (e.g. F.MAGENTA)
	"""
	print(f"{color}[{tag}] {S.RESET}{msg}")