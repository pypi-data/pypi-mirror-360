from .cli import HackByteShell

def main():
	shell = HackByteShell()
	try:
		shell.cmdloop()
	except KeyboardInterrupt:
		print("\nGoodbye!")

if __name__ == '__main__':
	main()