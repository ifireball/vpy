import unittest
from unittest.mock import create_autospec
from textwrap import dedent

from vpy.interfaces.uikit import WidgetClassFactory
from vpy.model.ui.base import Widget
from vpy.model.ui.loader import Loader, LoaderError


class TestLoader(unittest.TestCase):
    def setUp(self):
        self.widget1 = create_autospec(Widget, instance=True)
        
        self.wgt_cls = create_autospec(Widget, wraps=Widget)
        self.wgt_cls.return_value = self.widget1

        self.cls_factory = create_autospec(WidgetClassFactory)
        self.cls_factory.side_effect = {
            "WgtCls": self.wgt_cls
        }.get
        
        self.load = Loader(get_class=self.cls_factory)
    
    def test_read_single_widget(self):
        ui_def_str = dedent(
            """\
            [Widget1]
            class: WgtCls
            grid_row: 1
            grid_column: 1
            stick_north: True
            stick_east: Yes
            stick_south: False
            stick_west: No
            """
        )
        expected = self.widget1
        
        out = self.load(ui_def_str.splitlines())
        
        self.cls_factory.assert_called_once_with("WgtCls")
        self.wgt_cls.assert_called_once_with(
            name="Widget1",
            grid_row=1,
            grid_column=1,
            stick_north=True,
            stick_east=True,
            stick_south=False,
            stick_west=False,
        )
        self.assertEqual(expected, out)

    def test_invalid_config_detected(self):
        invalid_configs = [
            (
                "No class def",
                """\
                [Widget1]
                """
            ),
            (
                "Non existant class",
                """\
                [Widget1]
                class: NoSuchClass
                """
            ),
        ]
        for st_name, invalid_config in invalid_configs:
            with self.subTest(st_name):
                with self.assertRaises(LoaderError):
                    self.load(invalid_config.splitlines())


if __name__ == "__main__":
    unittest.main()
