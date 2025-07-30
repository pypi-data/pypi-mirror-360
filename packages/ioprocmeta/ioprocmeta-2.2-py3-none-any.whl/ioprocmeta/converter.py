import datetime
import pathlib as pt
from typing import Optional, Union

import cattr


class StructuringConverter:
    def __init__(self, cls):
        self._converter = cattr.Converter()
        self.__class = cls

        self._converter.register_structure_hook(
            Optional[Union[int, str]], lambda v, t: t(v) if v is not None else None
        )
        self._converter.register_structure_hook(Optional[Union[datetime.date, str]], self.__str_hook_1)
        self._converter.register_structure_hook(Optional[Union[str, pt.Path]], self.__str_hook_2)

        self._converter.register_unstructure_hook(StructuringConverter, lambda v: None)
        self._converter.register_unstructure_hook(Optional[Union[datetime.date, str]], self.__ustr_hook_1)
        self._converter.register_unstructure_hook(Optional[Union[str, pt.Path]], self.__ustr_hook_2)

    def __ustr_hook_1(self, v):
        return v.isoformat() if isinstance(v, datetime.date) else v

    def __ustr_hook_2(self, v):
        return v.as_posix() if isinstance(v, pt.Path) else v

    def __str_hook_1(self, v, t):
        if v is None:
            return None
        if isinstance(v, datetime.date):
            return v
        if isinstance(v, str):
            try:
                ret = datetime.datetime.strptime(v, "%Y-%m-%d")
            except:
                try:
                    ret = datetime.datetime.strptime(v, "%Y-%m-%dT%H:%M%z")
                except:
                    raise IOError(f'Unknown date format "{v}"')
            return ret
        raise IOError(f"malformed date input '{v}'")

    def __str_hook_2(self, v, t):
        return None if v is None else pt.Path(v)

    def unstructure(self, instance):
        return self._converter.unstructure(instance)

    def structure(self, data):
        return self._converter.structure(data, self.__class)
