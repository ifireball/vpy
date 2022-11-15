from typing import Final
from collections.abc import Mapping

from vpy.interfaces.uikit import UiKit
from vpy.model.ui.base import Widget
from vpy.model.ui.widgets import Button
from vpy.model.ui.layout_widgets import Frame


class TkInterKit(UiKit):
    WIDGET_CLASSES: Final[Mapping] = {
        cls.__name__: cls for cls in [
            Button,
            Frame
        ]
    }
    
    def widget_class_factory(self, class_name: str) -> type[Widget]|None:
        return self.WIDGET_CLASSES.get(class_name)

    def compile_user_class_dec(self, model: Widget) -> str:
        pass
