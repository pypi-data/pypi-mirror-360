from colorama import Fore, Style

COLOR_THEME = {
    'TRACE': Fore.LIGHTBLUE_EX,
    'DEBUG': Style.BRIGHT + Fore.CYAN,
    'VERBOSE': Style.BRIGHT + Fore.GREEN,
    'INFO': Style.BRIGHT + Fore.BLUE,
    'SUCCESS': Style.BRIGHT + Fore.GREEN,
    'WARN': Style.BRIGHT + Fore.YELLOW,
    'ERROR': Fore.RED,
    'CRITICAL': Style.BRIGHT + Fore.RED,
    'TIME': Style.BRIGHT + Fore.LIGHTBLUE_EX,
    'NAME': Style.BRIGHT + Fore.MAGENTA,
    'RESET': Style.RESET_ALL,
    'MESSAGE': Style.BRIGHT + Fore.WHITE
}
