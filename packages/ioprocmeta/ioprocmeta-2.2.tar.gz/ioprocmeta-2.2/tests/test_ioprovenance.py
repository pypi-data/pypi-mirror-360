import pathlib as pt
import pytest

import ioprocmeta

from ioprocmeta.base import MetaBase


@pytest.mark.parametrize("profile_name", {"oep150"})
def test_profile_registry(profile_name):

    assert profile_name in ioprocmeta.available_standard_formats

    assert isinstance(ioprocmeta.available_standard_formats[profile_name](), MetaBase)


def test_standard_formats():
    for iprofile, iclass in ioprocmeta.available_standard_formats.items():
        assert iprofile == iclass.type()
        assert issubclass(iclass, MetaBase)
