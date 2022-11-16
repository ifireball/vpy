import unittest
from unittest.mock import Mock, call
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

        result_code = self.uikit.compile_user_class_dec(model)

        mock_import = Mock()
        mock_globals = {"__builtins__": {"__import__": mock_import}}
        exec(result_code, mock_globals)

        self.assertEqual(mock_import.call_count, 3)
        mock_import.assert_has_calls(
            [
                call('tkinter', mock_globals, mock_globals, None, 0),
                call('tkinter.ttk', mock_globals, mock_globals, None, 0),
                call('typing', mock_globals, mock_globals, ('TypeVar',), 0)
            ],
            any_order=False
        )

        self.assertIsNotNone(tk := mock_globals.get("tk"))
        self.assertIsNotNone(ttk := mock_globals.get("ttk"))


if __name__ == "__main__":
    unittest.main()
