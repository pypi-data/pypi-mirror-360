import abc
import pathlib as pt
import json
from ioprocmeta.converter import StructuringConverter
from functools import wraps


def ensure_structure_converter_is_initialized(m):
    @wraps(m)
    def __decorator__(*args, **kwargs):
        cls = args[0]
        if cls._converter is None:
            cls._converter = StructuringConverter(cls)
        return m(*args, **kwargs)

    return __decorator__


class MetaBase(metaclass=abc.ABCMeta):
    _converter: StructuringConverter = None

    @abc.abstractmethod
    def type(self):
        pass

    @ensure_structure_converter_is_initialized
    def as_json(self):
        res = self.as_dict()
        return json.dumps(res, indent=4)

    @ensure_structure_converter_is_initialized
    def as_dict(self):
        data = self._converter.unstructure(self)
        self._post_as_dict_cleanup(data)
        return data

    # attention: the order of these decorators matters, as otherwise cls is not available!
    @classmethod
    @ensure_structure_converter_is_initialized
    def from_dict(cls, data):
        cls._post_from_dict_cleanup(data)
        return cls._converter.structure(data)

    @classmethod
    def _post_as_dict_cleanup(cls, data):
        pass

    @classmethod
    def _post_from_dict_cleanup(cls, data):
        pass

    @abc.abstractstaticmethod
    def type():
        pass

    @classmethod
    def read_json(cls, path: pt.Path):
        if not path.exists():
            raise IOError(f'Input file "{path.as_posix()}" does not exist.')

        with path.open("r") as ipf:
            data = json.load(ipf)
        return cls.from_dict(data)

    def write_json(self, path: pt.Path):
        with path.open("w") as opf:
            opf.write(self.as_json())
