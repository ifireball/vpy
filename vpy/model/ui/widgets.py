from dataclasses import dataclass

from .abc import Widget


@dataclass(wk_only=True)
class Button(Widget):
    text: str
