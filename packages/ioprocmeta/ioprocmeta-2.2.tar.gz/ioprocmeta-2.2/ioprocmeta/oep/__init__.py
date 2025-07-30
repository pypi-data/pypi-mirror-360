import datetime
import json
from typing import List, Optional, Union

import attr
from ioprocmeta.oep.sections import (
    _OEPContext,
    _OEPContributor,
    _OEPLicense,
    _OEPRessource,
    _OEPReview,
    _OEPSource,
    _OEPSpatial,
    _OEPSubject,
    _OEPTemporal,
)

from ioprocmeta.oep.sectionsv204 import (
    _OEPResource,
)

from ioprocmeta.base import MetaBase


@attr.define(repr=False)
class OEPMeta_1_5_0(MetaBase):
    """This class represents the OEP Metadata format in version 1.5.0.
    Each section of the meta data format is described by an attrs class.
    The class supports writing of the OEP Metadata format to disk and parsing the format into
    a class instance.
    """

    name: Optional[str] = attr.ib(None)
    title: Optional[str] = attr.ib(None)
    id: Optional[str] = attr.ib(None)
    description: Optional[str] = attr.ib(None)
    language: List[str] = attr.ib(factory=list)
    subject: List[_OEPSubject] = attr.ib(factory=list)
    keywords: List[str] = attr.ib(factory=list)
    publicationDate: Optional[Union[str, datetime.date]] = attr.ib(None)
    context: _OEPContext = attr.ib(factory=_OEPContext)
    spatial: _OEPSpatial = attr.ib(factory=_OEPSpatial)
    temporal: _OEPTemporal = attr.ib(factory=_OEPTemporal)
    sources: List[_OEPSource] = attr.ib(factory=list)
    licenses: List[_OEPLicense] = attr.ib(factory=list)
    contributors: List[_OEPContributor] = attr.ib(factory=list)
    resources: List[_OEPRessource] = attr.ib(factory=list)
    review: _OEPReview = attr.ib(factory=_OEPReview)
    at_id: Optional[Union[str, int]] = attr.ib(None)
    at_context: Optional[str] = attr.ib(None)
    metaMetadata: dict = attr.field(
        default={
            "metadataVersion": "OEP-1.5.0",
            "metadataLicense": {
                "name": "CC0-1.0",
                "title": "Creative Commons Zero v1.0 Universal",
                "path": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
        }
    )

    _comment: dict = attr.field(
        default={
            "metadata": "Metadata documentation and explanation (https://github.com/OpenEnergyPlatform/oemetadata)",
            "dates": "Dates and time must follow the ISO8601 including time zone (YYYY-MM-DD or YYYY-MM-DDThh:mm:ss±hh)",
            "units": "Use a space between numbers and units (100 m)",
            "languages": "Languages must follow the IETF (BCP47) format (en-GB, en-US, de-DE)",
            "licenses": "License name must follow the SPDX License List (https://spdx.org/licenses/)",
            "review": "Following the OEP Data Review (https://github.com/OpenEnergyPlatform/data-preprocessing/blob/master/data-review/manual/review_manual.md)",
            "null": "If not applicable use: null",
            "todo": "If a value is not yet available, use: todo",
        }
    )

    def add_subject(self, name, path):
        s = _OEPSubject(name, path)
        self.subject.append(s)
        return s

    def add_source(self, title, description, path):
        s = _OEPSource(title, description, path)
        self.sources.append(s)
        return s

    def add_license(self, name, title, path, instruction, attribution):
        lic = _OEPLicense(name, title, path, instruction, attribution)
        self.licenses.append(lic)
        return lic

    def add_contributor(self, title, email, date, _object, comment):
        c = _OEPContributor(title, email, date, _object, comment)
        self.contributors.append(c)
        return c

    def add_resource(self, profile, name, path, _format, encoding):
        r = _OEPRessource(profile, name, path, _format, encoding)
        self.resources.append(r)
        return r

    def add_language(self, name):
        self.language.append(name)

    def add_keyword(self, name):
        self.keywords.append(name)

    @staticmethod
    def type():
        return "oep150"

    @classmethod
    def _post_as_dict_cleanup(cls, data):
        data["@id"] = data["at_id"]
        del data["at_id"]
        data["@context"] = data["at_context"]
        del data["at_context"]
        return data

    @classmethod
    def _post_from_dict_cleanup(cls, data):
        data["at_id"] = data["@id"]
        del data["@id"]
        data["at_context"] = data["@context"]
        del data["@context"]
        return data

    def __repr__(self):
        return f"{self.metaMetadata['metadataVersion']} metadata information:\n{self.as_json()}"


@attr.define(repr=False)
class OEPMeta_1_6_0(OEPMeta_1_5_0):
    """This class represents the OEP Metadata format in version 1.6.0.
    Each section of the meta data format is described by an attrs class.
    The class supports writing of the OEP Metadata format to disk and parsing the format into
    a class instance.
    """

    metaMetadata: dict = attr.field(
        default={
            "metadataVersion": "OEP-1.6.0",
            "metadataLicense": {
                "name": "CC0-1.0",
                "title": "Creative Commons Zero v1.0 Universal",
                "path": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
        }
    )

    @staticmethod
    def type():
        return "oep160"


@attr.define(repr=False)
class OEPMeta_2_0_4(MetaBase):
    """This class represents the OEP Metadata format in version 2.0.4.
    Each section of the meta data format is described by an attrs class.
    The class supports writing of the OEP Metadata format to disk and parsing the format into
    a class instance.
    """

    at_context: Optional[str] = attr.ib(None)
    name: Optional[str] = attr.ib(None)
    title: Optional[str] = attr.ib(None)
    description: Optional[str] = attr.ib(None)
    at_id: Optional[str] = attr.ib(None)

    resource: list = attr.ib(factory=list)

    def add_resource(
        self,
        at_id=None,
        name=None,
        topic=None,
        title=None,
        path=None,
        type=None,
    ):
        _ = _OEPResource(
            at_id=at_id,
            name=name,
            topic=topic,
            title=title,
            path=path,
            license=license,
            type=type,
        )
        self.resource.append(_)
        return _

    metaMetadata: dict = attr.field(
        default={
            "metadataVersion": "OEMetadata-2.0.4",
            "metadataLicense": {
                "name": "CC0-1.0",
                "title": "Creative Commons Zero v1.0 Universal",
                "path": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
        }
    )

    @classmethod
    def _post_as_dict_cleanup(cls, data):
        data["@id"] = data["at_id"]
        del data["at_id"]
        data["@context"] = data["at_context"]
        del data["at_context"]
        return data

    @classmethod
    def _post_from_dict_cleanup(cls, data):
        data["at_id"] = data["@id"]
        del data["@id"]
        data["at_context"] = data["@context"]
        del data["@context"]
        return data

    @staticmethod
    def type():
        return "oep204"

    def __repr__(self):
        return f"{self.metaMetadata['metadataVersion']} metadata information:\n{self.as_json()}"
