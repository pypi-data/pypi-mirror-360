from ansi import Fore, Back, Style, rgb_fore, rgb_back

def print_attrs(cls, label):
    print(Style.BOLD + f"\n=== {label} ===" + Style.RESET)
    for name in dir(cls):
        if name.startswith('_'): continue
        value = getattr(cls, name)
        print(f"{name:20} {value}{name}{Style.RESET}")

def demo_rgb():
    print(Style.BOLD + "\n=== RGB Foreground ===" + Style.RESET)
    hex_colors = ['#ff0000', '#00ff00', '#0000ff', '#ffaa00', '#00ffff', '#ff00ff']
    for hex_code in hex_colors:
        print(f"{hex_code:10} {rgb_fore(hex_code)}{hex_code}{Style.RESET}")

    print(Style.BOLD + "\n=== RGB Background ===" + Style.RESET)
    for hex_code in hex_colors:
        print(f"{hex_code:10} {rgb_back(hex_code)}Foreground on {hex_code}{Style.RESET}")

def main():
    print_attrs(Fore, "Foreground Colors")
    print_attrs(Back, "Background Colors")
    print_attrs(Style, "Text Styles")
    demo_rgb()

if __name__ == "__main__":
    main()