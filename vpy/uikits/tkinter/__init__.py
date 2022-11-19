from typing import Final
from collections.abc import Mapping
from textwrap import dedent

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
        generated_code = dedent(
            """\
            import tkinter as tk
            import tkinter.ttk as ttk
            from typing import TypeVar

            _CT = TypeVar("_CT", bound=tk.Misc)

            def decorate_class(cls: _CT) -> _CT:
                def _new_init(self, parent: tk.Misc|None = None):
                    super(cls, self).__init__(parent)
                    
                cls.__init__ = _new_init
                return cls
            """
        )
        ( # this is for later...
            """\
            _CT = TypeVar("_CT", bound=tk.Misc)

            def decorate_class(cls: _CT) -> _CT:
                def _new_init(self, parent: tk.Misc|None = None, **options):
                    config = {}
                    config.update(options)
                    super(cls, self).__init__(parent, **config)

                cls.__init__ = _new_init
                cls.__init__.__qualname__ = f"{cls.__qualname__}.__init__"
                return cls
            """
        )
        return generated_code
