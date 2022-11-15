from abc import ABCMeta, abstractmethod
from typing import Protocol

from vpy.model.ui.base import Widget


class WidgetClassFactory(Protocol):
    @abstractmethod
    def __call__(self, class_name: str) -> type[Widget]|None:
        pass


class UiKit(metaclass=ABCMeta):
    @abstractmethod
    def widget_class_factory(self, class_name: str) -> type[Widget]|None:
        pass

    @abstractmethod
    def compile_user_class_dec(self, model: Widget) -> str:
        pass
