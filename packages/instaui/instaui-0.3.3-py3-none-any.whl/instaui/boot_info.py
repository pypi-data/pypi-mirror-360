from pathlib import Path
from typing import Literal
from instaui.version import __version__

_colors = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
}


def zero_boot_info(file: Path):
    message = f"""{_app_message("zero")}
{_arrow_right()}file: {_with_color(str(file))}
"""
    print(message)


def web_boot_info(ip: str):
    message = f"""{_app_message("web")}
{_arrow_right()}Local: {_with_color(str(ip), "blue")}
"""
    print(message)


def webview_boot_info():
    pass


def _app_message(mode: str) -> str:
    return f"""{_with_color(f"InstaUI {__version__}")}
mode: {_with_color(mode)}"""


def _with_color(
    text: str, color: Literal["red", "green", "yellow", "blue"] = "green"
) -> str:
    return f"{_colors[color]}{text}\033[0m"


def _arrow_right() -> str:
    return _with_color("➜ ")
