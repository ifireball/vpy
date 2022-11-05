from abc import ABCMeta

from vpy.model.ui.base import Widget


class WidgetClassFactory(metaclass=ABCMeta):
    def __call__(self, class_name: str) -> Widget|None:
        pass
