import unittest
from unittest.mock import Mock, call, create_autospec
from typing import Callable
from textwrap import dedent
import tkinter
import tkinter.ttk

from vpy.model.ui.base import Widget
from vpy.model.ui.widgets import Button
from vpy.model.ui.layout_widgets import Frame
from vpy.uikits.tkinter import TkInterKit


class TestTkInterCompiler(unittest.TestCase):
    def setUp(self) -> None:
        self.uikit = TkInterKit()

        self.button_cls = self.uikit.widget_class_factory("Button")
        self.frame_cls = self.uikit.widget_class_factory("Frame")

    def test_button_cls(self) -> None:
        assert issubclass(self.button_cls, Button)

    def test_frame_cls(self) -> None:
        assert issubclass(self.frame_cls, Frame)

    @staticmethod
    def mk_cls_w_mocked_init() -> type:
        class ClsWMockedInit:
            __init__ = Mock(return_value=None)

        return ClsWMockedInit

    def compile_and_exec_model(self, model: Widget) -> tuple[Mock, Mock, Callable]:
        result_code = self.uikit.compile_user_class_dec(model)

        mock_import = Mock()
        mock_globals = {
            "__builtins__": {
                "__import__": mock_import,
                "super": super,
            }
        }
        exec(result_code, mock_globals)
        
        self.assert_imports(mock_import, mock_globals)
        return self.assert_and_extract_libs_and_decorator(mock_globals)

    def assert_imports(self, mock_import: Mock, mock_globals: dict[str, object]) -> None:
        self.assertEqual(mock_import.call_count, 3)
        mock_import.assert_has_calls(
            [
                call('tkinter', mock_globals, mock_globals, None, 0),
                call('tkinter.ttk', mock_globals, mock_globals, None, 0),
                call('typing', mock_globals, mock_globals, ('TypeVar',), 0)
            ],
            any_order=False
        )

    def assert_and_extract_libs_and_decorator(
        self, mock_globals: dict
    ) -> tuple[Mock, Mock, Callable]:
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
        return tk, ttk, decorator

    @classmethod
    def mockup_widget_classes(cls, tk: Mock, ttk: Mock) -> None:
        tk.Misc = cls.mk_cls_w_mocked_init()
        ttk.Frame = cls.mk_cls_w_mocked_init()

    def create_and_decorate_user_class(
        self, tk: Mock, ttk: Mock, decorator: Callable
    ) -> type:
        self.mockup_widget_classes(tk, ttk)
        
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

        return decorated
            
    def test_compile_creates_class_decorator(self) -> None:
        model = self.frame_cls(name="Frame1")

        tk, ttk, decorator = self.compile_and_exec_model(model)
        user_class = self.create_and_decorate_user_class(tk, ttk, decorator)

        user_class()

        ttk.Frame.__init__.assert_called_once()


if __name__ == "__main__":
    unittest.main()
