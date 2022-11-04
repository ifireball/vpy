from dataclasses import dataclass
from typing import TypeVar


loadable_widgets: dict[str, type[Widget]]


def loadable_widget(wgt_cls: type[Widget]) -> type[Widget]:
    loadabe_widgets[wgt_cls.__name__] = wgt_cls
    return wgt_cls


@dataclass
class Widget(kw_only=True):
    name: str
    
    grid_column: int|None = None
    grid_row: int|None = None
    grid_columnspan: int = 1
    grid_rowspan: int = 1

    stick_north: bool = False
    stick_east: bool = False
    stick_south: bool = False
    stick_west: bool = False

    margin_x: int = 0
    margin_y: int = 0
    padding_x: int = 0
    padding_y: int = 0


@dataclass(wk_only=True)
class WidgetContainer(Widget):
    children: list[Widget]


@loadable_widgets
@dataclass(wk_only=True)
class Button(Widget):
    text: str
