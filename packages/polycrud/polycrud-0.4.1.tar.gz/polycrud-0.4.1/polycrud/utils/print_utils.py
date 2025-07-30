import logging
from collections.abc import Callable
from typing import TypeVar

_logger = logging.getLogger(__name__)

T = TypeVar("T")


def print_style_free(message: str, print_fun: Callable[[str], None] = print) -> None:
    print_fun("")
    print_fun(f"░▒▓█  {message}")


def print_style_time(message: str, print_fun: Callable[[str], None] = print) -> None:
    print_fun("")
    print_fun(f"⏰  {message}")
    print_fun("")


def print_style_warning(message: str, print_fun: Callable[[str], None] = print) -> None:
    print_fun("")
    print_fun(f"⛔️  {message}")
    print_fun("")


def print_style_notice(message: str, print_fun: Callable[[str], None] = print) -> None:
    print_fun("")
    print_fun(f"📌  {message}")
    print_fun("")


def print_line(text: str, print_fun: Callable[[str], None] = print) -> None:
    print_fun("")
    print_fun(f"➖➖➖➖➖➖➖➖➖➖ {text.upper()} ➖➖➖➖➖➖➖➖➖➖")
    print_fun("")


def print_boxed(text: str, print_fun: Callable[[str], None] = print) -> None:
    box_width = len(text) + 2
    border = "═" * box_width
    print_fun("")
    print_fun(f"╒{border}╕")
    print_fun(f"  {text.upper()}  ")
    print_fun(f"╘{border}╛")
    print_fun("")
