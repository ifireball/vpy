import unittest
from unittest.mock import create_autospec
from textwrap import dedent

from vpy.interfaces.uikit import WidgetClassFactory
from vpy.model.ui.base import Widget
from vpy.model.ui.loader import Loader


class TestLoader(unittest.TestCase):
    def setUp(self):
        self.widget1 = create_autospec(Widget, instance=True)
        
        self.wgt_cls = create_autospec(Widget)
        self.wgt_cls.return_value = self.widget1

        self.cls_factory = create_autospec(WidgetClassFactory)
        self.cls_factory.return_value = self.wgt_cls
        
        self.load = Loader(get_class=self.cls_factory)
    
    def test_read_single_widget(self):
        ui_def_str = dedent(
            """\
            [Widget1]
            class: WgtCls
            """
        )
        expected = self.widget1
        
        out = self.load(ui_def_str)
        
        self.cls_factory.assert_called_with("WgtCls")


if __name__ == "__main__":
    unittest.main()
