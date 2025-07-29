class Fore:
    BLACK        = '\033[30m'
    RED          = '\033[31m'
    GREEN        = '\033[32m'
    YELLOW       = '\033[33m'
    BLUE         = '\033[34m'
    MAGENTA      = '\033[35m'
    CYAN         = '\033[36m'
    WHITE        = '\033[37m'

    BRIGHT_BLACK   = '\033[90m'
    BRIGHT_RED     = '\033[91m'
    BRIGHT_GREEN   = '\033[92m'
    BRIGHT_YELLOW  = '\033[93m'
    BRIGHT_BLUE    = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN    = '\033[96m'
    BRIGHT_WHITE   = '\033[97m'

class Back:
    BLACK        = '\033[40m'
    RED          = '\033[41m'
    GREEN        = '\033[42m'
    YELLOW       = '\033[43m'
    BLUE         = '\033[44m'
    MAGENTA      = '\033[45m'
    CYAN         = '\033[46m'
    WHITE        = '\033[47m'

    BRIGHT_BLACK   = '\033[100m'
    BRIGHT_RED     = '\033[101m'
    BRIGHT_GREEN   = '\033[102m'
    BRIGHT_YELLOW  = '\033[103m'
    BRIGHT_BLUE    = '\033[104m'
    BRIGHT_MAGENTA = '\033[105m'
    BRIGHT_CYAN    = '\033[106m'
    BRIGHT_WHITE   = '\033[107m'

class Style:
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET     = '\033[0m'

def rgb_fore(hex_color: str) -> str:
    """Convert hex color (e.g. '#ff0000') to ANSI foreground escape code."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'\033[38;2;{r};{g};{b}m'

def rgb_back(hex_color: str) -> str:
    """Convert hex color (e.g. '#00ff00') to ANSI background escape code."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'\033[48;2;{r};{g};{b}m'