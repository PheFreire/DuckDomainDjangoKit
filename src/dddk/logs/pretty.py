from enum import (
    Enum,
)
from json import (
    dumps,
)
from typing import (
    Any,
)
from dataclasses import (
    dataclass,
)

from dddk.logs.jsonify import (
    jsonify,
)


@dataclass
class _Color:
    foreground: int
    background: int


class Colors(Enum):
    DEFAULT = None

    BLACK = _Color(foreground=30, background=40)
    RED = _Color(foreground=31, background=41)
    GREEN = _Color(foreground=32, background=42)
    YELLOW = _Color(foreground=33, background=43)
    BLUE = _Color(foreground=34, background=44)
    PURPLE = _Color(foreground=35, background=45)
    CYAN = _Color(foreground=36, background=46)
    WHITE = _Color(foreground=37, background=47)


class Effects(Enum):
    DEFAULT = 0
    BOLD = 1
    UNDERLINE = 2


_RESET = "\033[0m"


def _ansi(fg: Colors, bg: Colors, eff: Effects) -> str:
    codes = [str(eff.value)]
    if fg != Colors.DEFAULT:
        codes.append(str(fg.value.foreground))
    if bg != Colors.DEFAULT:
        codes.append(str(bg.value.background))
    return f"\033[{';'.join(codes)}m"


class _NOTEXT:
    def __str__(self) -> str:
        return ""


def pretty(
    title: str,
    value: Any = _NOTEXT(),
    *,
    external_padding: int = 1,
    internal_padding: int = 0,
    title_foreground_color: Colors = Colors.DEFAULT,
    title_background_color: Colors = Colors.DEFAULT,
    title_text_effect: Effects = Effects.DEFAULT,
    value_is_json: bool = False,
    value_foreground_color: Colors = Colors.DEFAULT,
    value_background_color: Colors = Colors.DEFAULT,
    value_text_effect: Effects = Effects.DEFAULT,
    has_line: bool = True,
    line_size: int = 50,
    line_symbol: str = "-=",
    line_foreground_color: Colors = Colors.DEFAULT,
    line_background_color: Colors = Colors.DEFAULT,
    line_text_effect: Effects = Effects.DEFAULT,
    has_final_line: bool = False,
) -> None:
    e_padding = "\n" * external_padding
    i_padding = "\n" * internal_padding

    line = ""
    final_line = ""
    if has_line:
        line_ansi = _ansi(
            line_foreground_color, line_background_color, line_text_effect
        )

        distance = line_size - len(title)
        if distance % 2 == 1:
            distance += 1

        iteration_times = (distance // 2) // len(line_symbol)
        line = line_symbol * iteration_times
        line = f"{line_ansi}{line}{_RESET}"

        if has_final_line:
            iteration_times = line_size // len(line_symbol)
            final_line = line_symbol * iteration_times
            final_line = f"{line_ansi}{final_line}{_RESET}"

    if title:
        title_ansi = _ansi(
            title_foreground_color, title_background_color, title_text_effect
        )
        title = f"{title_ansi}({title}){_RESET}"

    if not isinstance(value, _NOTEXT):
        value_ansi = _ansi(
            value_foreground_color, value_background_color, value_text_effect
        )

        if value_is_json:
            value = dumps(
                jsonify(value), indent=3, ensure_ascii=False, default=str
            )

        value = f"{value_ansi}{value}{_RESET}"

    print(f"{e_padding}{line}{title}{line}")

    if not isinstance(value, _NOTEXT):
        print(f"{i_padding}{value}")

    if has_final_line:
        print(final_line)

    if e_padding:
        print(e_padding)
