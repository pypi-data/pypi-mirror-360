import re as regex
from typing import List, Any

from colored import fore, back, style as styler
from colored.exceptions import InvalidColor, InvalidStyle

decolorize_regex = regex.compile(r'\x1b[^m]*m')


def colorize(text: Any, foreground: str | None = None, background: str | None = None, styles: List[str] | None = None):
    if styles is None:
        styles = []
    try:
        foreground_exp = fore(foreground) if foreground else ""
    except InvalidColor:
        raise Exception(f"Invalid foreground color name {foreground}")
    try:
        background_exp = back(background) if background else ""
    except InvalidColor:
        raise Exception(f"Invalid Background color name {foreground}")

    style_exps: List[str] = []
    for style in styles:
        try:
            style_exps.append(styler(style))
        except InvalidStyle:
            raise Exception(f"Invalid Style name {style}")
    return (
        f"{''.join(style_exps) if style_exps else ''}"
        f"{foreground_exp}"
        f"{background_exp}"
        f"{text}"
        f"{styler('reset')}"
    )


def decolorize(text: str) -> str:
    return decolorize_regex.sub('', text)
