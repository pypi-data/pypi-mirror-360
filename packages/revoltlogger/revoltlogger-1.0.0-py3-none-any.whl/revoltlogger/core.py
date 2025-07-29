import sys
from datetime import datetime
from colorama import init, Style
from revoltlogger.levels import LogLevel
from revoltlogger.themes import COLOR_THEME
init(autoreset=True)

class Logger:
    def __init__(self, name=None, level=LogLevel.INFO, colored=True):
        self.name = name
        self.level = level
        self.colored = colored

    def _should_log(self, level):
        return level.value >= self.level.value and self.level != LogLevel.NONE

    def _format(self, level, message):
        time_str = datetime.now().strftime("%H:%M:%S")
        level_name = level.name
        name_part = f"[{self.name}]" if self.name else ""

        if self.colored:
            color = COLOR_THEME.get(level_name, "")
            return f"[{COLOR_THEME['TIME']}{time_str}{Style.RESET_ALL}] {COLOR_THEME['NAME']}{name_part}{Style.RESET_ALL} [{color}{level_name}{Style.RESET_ALL}]: {COLOR_THEME['MESSAGE']}{message}{Style.RESET_ALL}"
        else:
            return f"[{time_str}] {name_part} [{level_name}]: {message}"

    def log(self, level, message):
        if self._should_log(level):
            print(self._format(level, message), file=sys.stderr)

    def trace(self, msg): self.log(LogLevel.TRACE, msg)
    def debug(self, msg): self.log(LogLevel.DEBUG, msg)
    def verbose(self, msg): self.log(LogLevel.VERBOSE, msg)
    def info(self, msg): self.log(LogLevel.INFO, msg)
    def success(self, msg): self.log(LogLevel.SUCCESS, msg)
    def warn(self, msg): self.log(LogLevel.WARN, msg)
    def error(self, msg): self.log(LogLevel.ERROR, msg)
    def critical(self, msg): self.log(LogLevel.CRITICAL, msg)

    def custom(self, level_name: str, message: str, color: str = COLOR_THEME['MESSAGE']):
        time_str = datetime.now().strftime("%H:%M:%S")
        name_part = f"[{self.name}]" if self.name else ""

        if self.colored:
            level_str = f"{Style.BRIGHT}{color}{level_name.upper()}{Style.RESET_ALL}"
            message = f"{COLOR_THEME['MESSAGE']}{message}{Style.RESET_ALL}"
            line = f"[{COLOR_THEME['TIME']}{time_str}{Style.RESET_ALL}] {COLOR_THEME['NAME']}{name_part}{Style.RESET_ALL} [{level_str}]: {message}"
        else:
            line = f"[{time_str}] {name_part} [{level_name.upper()}]: {message}"

        print(line, file=sys.stderr)

    def bannerlog(self, banner: str):
        print(f"{banner}", file=sys.stderr)

    def stdinlog(self, message: str):
        print(message)