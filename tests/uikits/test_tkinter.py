import unittest
from textwrap import dedent

from vpy.model.ui.widgets import Button
from vpy.model.ui.layout_widgets import Frame
from vpy.uikits.tkinter import TkInterKit


class TestTkInterCompiler(unittest.TestCase):
    def setUp(self):
        self.uikit = TkInterKit()

        self.button_cls = self.uikit.widget_class_factory("Button")
        self.frame_cls = self.uikit.widget_class_factory("Frame")

    def test_button_cls(self):
        assert issubclass(self.button_cls, Button)

    def test_frame_cls(self):
        assert issubclass(self.frame_cls, Frame)

    def test_compile_top_frame(self):
        model = self.frame_cls(name="Frame1")
        expected = dedent(
            """\
            import tkinter as tk
            import tkinter.ttk as ttk
            from typing import TypeVar

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


if __name__ == "__main__":
    unittest.main()
