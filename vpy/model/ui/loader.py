from dataclasses import dataclass
from collections.abc import Iterable

from vpy.interfaces.uikit import WidgetClassFactory
from vpy.model.ui.base import Widget


@dataclass(kw_only=True)
class Loader:
    get_class: WidgetClassFactory
    
    def __call__(self, stream: Iterable[str]) -> Widget:
        pass
