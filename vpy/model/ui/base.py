"""Base classes for UI data model. We should generally not heve
instances of these floating around but only subclasses thereof,
but Python does not seem to allow something to be both a
dataclass and a Protocol at the same time, while ABCs do not
prevent instanciation where there are no abstract methods.
"""
from dataclasses import dataclass, field
from abc import ABCMeta


@dataclass(kw_only=True)
class Widget(metaclass=ABCMeta):
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


@dataclass(kw_only=True)
class WidgetContainer(Widget, metaclass=ABCMeta):
    children: list[Widget] = field(default_factory=list)
