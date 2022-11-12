import unittest
from unittest.mock import create_autospec
from textwrap import dedent
from itertools import permutations

from vpy.interfaces.uikit import WidgetClassFactory
from vpy.model.ui.widgets import Button
from vpy.model.ui.layout_widgets import Frame
from vpy.model.ui.loader import Loader, LoaderError


class TestLoader(unittest.TestCase):
    def setUp(self):
        self.widget1 = Button(name="Widget1")
        self.widget2 = Button(name="Widget2")
        self.widget3 = Button(name="Widget3")
        
        self.wgt_cls = create_autospec(Button, wraps=Button)
        self.wgt_cls.side_effect = lambda **kwargs: {
                "Widget1": self.widget1,
                "Widget2": self.widget2,
                "Widget3": self.widget3,
        }[kwargs["name"]]

        self.lay_widget1 = Frame(name="LayWidget1")
        self.lay_widget2 = Frame(name="LayWidget2")
        self.lay_widget3 = Frame(name="LayWidget3")

        self.lay_wgt_cls = create_autospec(Frame, wraps=Frame)
        self.lay_wgt_cls.side_effect = lambda **kwargs: {
                "LayWidget1": self.lay_widget1,
                "LayWidget2": self.lay_widget2,
                "LayWidget3": self.lay_widget3,
        }[kwargs["name"]]

        self.cls_factory = create_autospec(WidgetClassFactory)
        self.cls_factory.side_effect = {
            "WgtCls": self.wgt_cls,
            "LayWgtCls": self.lay_wgt_cls,
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
            text: Big, red button!
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
            text="Big, red button!"
        )
        self.assertEqual(expected, out)

    def test_read_widget_in_layout(self):
        configs = [
            (
                "In order",
                """\
                [LayWidget1]
                class: LayWgtCls

                [Widget1]
                class: WgtCls
                parent: LayWidget1
                """
            ),
            (
                "Out of order",
                """\
                [Widget1]
                class: WgtCls
                parent: LayWidget1

                [LayWidget1]
                class: LayWgtCls            
                """
            )
        ]
        for name, config in configs:
            with self.subTest(name):
                self.setUp()
                out = self.load(dedent(config).splitlines())
        
                self.lay_wgt_cls.assert_called_once_with(name="LayWidget1")
                self.assertEqual(self.lay_widget1, out)

                self.wgt_cls.assert_called_once_with(name="Widget1")

                self.assertEqual(out.children, [self.widget1])
                
    def test_read_widgets_in_layout(self):
        cfg_sections = [
            """\
            [LayWidget1]
            class: LayWgtCls""",
            """\
            [Widget1]
            class: WgtCls
            parent: LayWidget1""",
            """\
            [Widget2]
            class: WgtCls
            parent: LayWidget1""",
        ]
        exp_sct_child = [
            None,
            self.widget1,
            self.widget2,
        ]
        
        configs = (
            dedent("\n".join(cfg_sections_p)).splitlines()
            for cfg_sections_p in permutations(cfg_sections)
        )
        exp_child_lists = (
            list(filter(bool, exp_sct_child_p))
            for exp_sct_child_p in permutations(exp_sct_child)
        )

        for config, exp_children in zip(configs, exp_child_lists):
            with self.subTest():
                self.setUp()
                out = self.load(config)
        
                self.lay_wgt_cls.assert_called_once_with(name="LayWidget1")
                self.assertEqual(self.lay_widget1, out)

                self.wgt_cls.assert_any_call(name="Widget1")
                self.wgt_cls.assert_any_call(name="Widget2")
                self.assertEqual(2, self.wgt_cls.call_count)

                self.assertEqual(out.children, exp_children)
                 
    def test_nested_layouts(self):
        cfg_sections = [
            """\
            [LayWidget1]
            class: LayWgtCls""",
            """\
            [LayWidget2]
            class: LayWgtCls
            parent: LayWidget1
            [LayWidget3]
            class: LayWgtCls
            parent: LayWidget1""",
            """\
            [Widget1]
            class: WgtCls
            parent: LayWidget2""",
            """\
            [Widget2]
            class: WgtCls
            parent: LayWidget3
            [Widget3]
            class: WgtCls
            parent: LayWidget3""",
        ]
        configs = (
            dedent("\n".join(cfg_sections_p)).splitlines()
            for cfg_sections_p in permutations(cfg_sections)
        )
        expected = Frame(
            name="LayWidget1",
            children=[
                Frame(
                    name="LayWidget2",
                    children=[Button(name="Widget1")],
                ),
                Frame(
                    name="LayWidget3",
                    children=[Button(name="Widget2"), Button(name="Widget3")],
                ),
            ],
        )
        for config in configs:
            with self.subTest():
                self.setUp()
                out = self.load(config)
                self.assertEqual(expected, out)


    def test_invalid_config_detected(self):
        invalid_configs = [
            (
                "No class def",
                """\
                [Widget1]
                """,
                "^Widget class not specified for 'Widget1'$"
            ),
            (
                "Non existant class",
                """\
                [Widget1]
                class: NoSuchClass
                """,
                "Invalid widget class: 'NoSuchClass'"
            ),
            (
                "Bad int value",
                """\
                [Widget1]
                class: WgtCls
                grid_column: A
                """,
                "Invalid int value for Widget1.grid_column"
            ),
            (
                "Bad bool value",
                """\
                [Widget1]
                class: WgtCls
                stick_north: absolutely not!
                """,
                "Invalid bool value for Widget1.stick_north"
            ),
            (
                "Missing root",
                """\
                [Widget1]
                class: WgtCls
                parent: NoSuchWgt
                """,
                "Root widget not found"
            ),
            (
                "More then one root",
                """\
                [Widget1]
                class: WgtCls
                [Widget2]
                class: WgtCls
                """,
                "Attempt to set 'Widget2' as root while 'Widget1' is"
                " already set as such"
            ),
            (
                "Missing parent",
                """\
                [Widget1]
                class: WgtCls
                parent: NoSuchWgt
                [Widget2]
                class: WgtCls
                """,
                "Could not find 'NoSuchWgt' the parent of 'Widget1'"
            ),
            (
                "Parent is not a container",
                """\
                [Widget1]
                class: WgtCls
                parent: Widget2
                [Widget2]
                class: WgtCls
                """,
                "'Widget2' set as parent of 'Widget1', but its not a container"
            ),
        ]
        for st_name, invalid_config, err_re in invalid_configs:
            with self.subTest(st_name):
                with self.assertRaisesRegex(LoaderError, err_re):
                    self.load(invalid_config.splitlines())


if __name__ == "__main__":
    unittest.main()
