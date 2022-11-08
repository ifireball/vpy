from dataclasses import dataclass, fields, Field
from collections.abc import Iterable
from configparser import ConfigParser, SectionProxy
import re

from vpy.interfaces.uikit import WidgetClassFactory
from vpy.model.ui.base import Widget


class LoaderError(Exception):
    pass


@dataclass(kw_only=True)
class Loader:
    get_class: WidgetClassFactory
    
    def __call__(self, stream: Iterable[str]) -> Widget:
        cfg = self._parse_stream(stream)
        for section, items in cfg.items():
            if section == ".default":
                continue
            widget = self._load_widget(section, items)
            return widget

    def _load_widget(self, section: str, items: SectionProxy) -> Widget:
            cls = self._get_wgt_cls(section, items)
            wgt_cfg = {
                field.name: self._data_for_field(field, items)
                for field in fields(cls)
                if field.name in items
            }
            widget = cls(name=section, **wgt_cfg)
            return widget

    @staticmethod
    def _data_for_field(field: Field, items: SectionProxy) -> object:
        types_and_getters = {
            int: items.getint,
            bool: items.getboolean,
            str: items.get,
        }
        for type_, getter in types_and_getters.items():
            if issubclass(type_, field.type):
                try:
                    return getter(field.name)
                except ValueError:
                    raise LoaderError(
                        f"Invalid {type_.__name__} value "
                        f"for {items.name}.{field.name}"
                    )
        else:
            raise TypeError(f"Unsupported Widget field type: {field.type}")

    def _get_wgt_cls(self, section: str, items: SectionProxy) -> type(Widget):
            wgt_cls_name = items.get('class', None)
            if wgt_cls_name is None:
                raise LoaderError(f"Widget class not specified for '{section}'")
            cls = self.get_class(wgt_cls_name)
            if cls is None:
                raise LoaderError(f"Invalid widget class: '{wgt_cls_name}'")
            return cls

    def _parse_stream(self, stream: Iterable[str]) -> ConfigParser:
        cfg = ConfigParser(
            delimiters=(':',),
            comment_prefixes=('#',),
            default_section=".default",
            interpolation=None
        )
        cfg.SECTRE = re.compile(r"\[\s*(?P<header>(:?\.?\w+))\s*\]")
        cfg.read_file(stream)
        return cfg
