from dataclasses import dataclass

from .base import Widget


@dataclass(kw_only=True)
class Button(Widget):
    text: str = "Click me!"
