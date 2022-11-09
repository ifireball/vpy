from dataclasses import dataclass

from .base import WidgetContainer


@dataclass(kw_only=True)
class Frame(WidgetContainer):
    pass
