import unittest
from unittest.mock import Mock, call, create_autospec
from textwrap import dedent
import tkinter
import tkinter.ttk

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

    @staticmethod
    def mk_cls_w_mocked_init():
        class ClsWMockedInit:
            __init__ = Mock(return_value=None)

        return ClsWMockedInit

    def test_compile_creates_class_decorator(self):
        model = self.frame_cls(name="Frame1")

        result_code = self.uikit.compile_user_class_dec(model)

        mock_import = Mock()
        mock_globals = {
            "__builtins__": {
                "__import__": mock_import,
                "super": super,
            }
        }
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

        self.assertIsNotNone(
            tk := mock_globals.get("tk"),
            "tkinter is not imported as 'tk'"
        )
        self.assertIsNotNone(
            ttk := mock_globals.get("ttk"),
            "tkinter.ttk is not imported as 'ttk'"
        )
        self.assertIsNotNone(
            decorator := mock_globals.get("decorate_class"),
            "Decorator function 'decorate_class' was not defined"
        )
        tk.Misc = self.mk_cls_w_mocked_init()
        ttk.Frame = self.mk_cls_w_mocked_init()
        
        class UserAppFrame(ttk.Frame):
            pass

        decorated = decorator(UserAppFrame)

        self.assertIs(
            UserAppFrame, decorated,
            "Decorator does not return the user class"
        )
        self.assertIsNot(
            UserAppFrame.__init__, ttk.Frame.__init__,
            "User class __init__ was not patched"
        )

        decorated()

        ttk.Frame.__init__.assert_called_once()


if __name__ == "__main__":
    unittest.main()
