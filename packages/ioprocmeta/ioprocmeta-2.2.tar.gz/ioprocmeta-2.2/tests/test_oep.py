from ioprocmeta.oep import OEPMeta_1_5_0
from ioprocmeta.oep import OEPMeta_2_0_4
import pytest
import ioprocmeta
from ioprocmeta.base import MetaBase


@pytest.mark.parametrize("profile_name", {"oep150", "oep160", "oep204"})
def test_default_instantiation(profile_name):

    assert profile_name in ioprocmeta.available_standard_formats
    inst = ioprocmeta.available_standard_formats[profile_name]()
    assert isinstance(inst, MetaBase)
    assert inst.type() == profile_name


def test_empty_oep():
    m = OEPMeta_1_5_0()

    assert m.name is None
    assert m.title is None
    assert m.id is None
    assert m.description is None
    assert isinstance(m.language, list)
    assert len(m.language) == 0
    assert isinstance(m.subject, list)
    assert len(m.subject) == 0
    assert isinstance(m.keywords, list)
    assert len(m.keywords) == 0
    assert m.publicationDate is None
    assert m.context.homepage is None
    assert m.context.documentation is None
    assert m.context.sourceCode is None
    assert m.context.contact is None
    assert m.context.grantNo is None
    assert m.context.fundingAgency is None
    assert m.context.fundingAgencyLogo is None
    assert m.context.publisherLogo is None
    assert m.spatial.location is None
    assert (
        isinstance(m.spatial.extent, tuple)
        and len(m.spatial.extent) == 2
        and m.spatial.extent[0] is None
        and m.spatial.extent[1] is None
    )
    assert (
        isinstance(m.spatial.resolution, tuple)
        and len(m.spatial.resolution) == 2
        and m.spatial.resolution[0] is None
        and m.spatial.resolution[1] is None
    )
    assert m.temporal.referenceDate is None
    assert isinstance(m.temporal.timeseries, list)
    assert len(m.temporal.timeseries) == 0
    assert isinstance(m.sources, list)
    assert len(m.sources) == 0
    assert isinstance(m.licenses, list)
    assert len(m.licenses) == 0
    assert isinstance(m.contributors, list)
    assert len(m.contributors) == 0
    assert isinstance(m.resources, list)
    assert len(m.resources) == 0
    assert m.review.path is None
    assert m.review.badge is None
    assert isinstance(m.metaMetadata, dict)
    assert m.metaMetadata["metadataVersion"] == "OEP-1.5.0"
    assert isinstance(m.metaMetadata["metadataLicense"], dict)
    assert m.metaMetadata["metadataLicense"]["name"] == "CC0-1.0"
    assert (
        m.metaMetadata["metadataLicense"]["title"]
        == "Creative Commons Zero v1.0 Universal"
    )
    assert (
        m.metaMetadata["metadataLicense"]["path"]
        == "https://creativecommons.org/publicdomain/zero/1.0/"
    )
    assert isinstance(m._comment, dict)
    assert (
        m._comment["metadata"]
        == "Metadata documentation and explanation (https://github.com/OpenEnergyPlatform/oemetadata)"
    )
    assert (
        m._comment["dates"]
        == "Dates and time must follow the ISO8601 including time zone (YYYY-MM-DD or YYYY-MM-DDThh:mm:ss±hh)"
    )
    assert m._comment["units"] == "Use a space between numbers and units (100 m)"
    assert (
        m._comment["languages"]
        == "Languages must follow the IETF (BCP47) format (en-GB, en-US, de-DE)"
    )
    assert (
        m._comment["licenses"]
        == "License name must follow the SPDX License List (https://spdx.org/licenses/)"
    )
    assert (
        m._comment["review"]
        == "Following the OEP Data Review (https://github.com/OpenEnergyPlatform/data-preprocessing/blob/master/data-review/manual/review_manual.md)"
    )
    assert m._comment["null"] == "If not applicable use: null"
    assert m._comment["todo"] == "If a value is not yet available, use: todo"
    assert m.at_id is None
    assert m.at_context is None


def test_oep_as_dict():
    m = OEPMeta_1_5_0()
    m = m.as_dict()
    assert isinstance(m, dict)
    assert m["name"] is None
    assert m["spatial"]["extent"][0] is None


def test_oep_150_as_json():
    m = OEPMeta_1_5_0()
    out = m.as_json()
    ref = """{
    "name": null,
    "title": null,
    "id": null,
    "description": null,
    "language": [],
    "subject": [],
    "keywords": [],
    "publicationDate": null,
    "context": {
        "homepage": null,
        "documentation": null,
        "sourceCode": null,
        "contact": null,
        "grantNo": null,
        "fundingAgency": null,
        "fundingAgencyLogo": null,
        "publisherLogo": null
    },
    "spatial": {
        "location": null,
        "extent": [
            null,
            null
        ],
        "resolution": [
            null,
            null
        ]
    },
    "temporal": {
        "referenceDate": null,
        "timeseries": []
    },
    "sources": [],
    "licenses": [],
    "contributors": [],
    "resources": [],
    "review": {
        "path": null,
        "badge": null
    },
    "metaMetadata": {
        "metadataVersion": "OEP-1.5.0",
        "metadataLicense": {
            "name": "CC0-1.0",
            "title": "Creative Commons Zero v1.0 Universal",
            "path": "https://creativecommons.org/publicdomain/zero/1.0/"
        }
    },
    "_comment": {
        "metadata": "Metadata documentation and explanation (https://github.com/OpenEnergyPlatform/oemetadata)",
        "dates": "Dates and time must follow the ISO8601 including time zone (YYYY-MM-DD or YYYY-MM-DDThh:mm:ss\\u00b1hh)",
        "units": "Use a space between numbers and units (100 m)",
        "languages": "Languages must follow the IETF (BCP47) format (en-GB, en-US, de-DE)",
        "licenses": "License name must follow the SPDX License List (https://spdx.org/licenses/)",
        "review": "Following the OEP Data Review (https://github.com/OpenEnergyPlatform/data-preprocessing/blob/master/data-review/manual/review_manual.md)",
        "null": "If not applicable use: null",
        "todo": "If a value is not yet available, use: todo"
    },
    "@id": null,
    "@context": null
}"""

    for iref_line, iout_line in zip(ref.split("\n"), out.split("\n")):
        assert iref_line == iout_line


def test_oep_204_as_json():
    m = OEPMeta_2_0_4()
    out = m.as_json()
    ref = """{
    "name": null,
    "title": null,
    "description": null,
    "resource": [],
    "metaMetadata": {
        "metadataVersion": "OEMetadata-2.0.4",
        "metadataLicense": {
            "name": "CC0-1.0",
            "title": "Creative Commons Zero v1.0 Universal",
            "path": "https://creativecommons.org/publicdomain/zero/1.0/"
        }
    },
    "@id": null,
    "@context": null
}"""

    for iref_line, iout_line in zip(ref.split("\n"), out.split("\n")):
        assert iref_line == iout_line


def test_setting_values():
    m = OEPMeta_1_5_0()
    s = m.add_source("test", None, None)
    assert s == m.sources[0]
    assert len(m.sources) == 1
    assert m.sources[0].title == "test"

    s = m.add_subject("test", None)
    assert s == m.subject[0]
    assert len(m.subject) == 1
    assert m.subject[0].name == "test"

    s = m.add_license("test", None, None, None, None)
    assert s == m.licenses[0]
    assert len(m.licenses) == 1
    assert m.licenses[0].name == "test"

    s = m.add_contributor("test", None, None, None, None)
    assert s == m.contributors[0]
    assert len(m.contributors) == 1
    assert m.contributors[0].title == "test"

    s = m.add_resource("test", None, None, None, None)
    assert s == m.resources[0]
    assert len(m.resources) == 1
    assert m.resources[0].profile == "test"

    m.add_language("test")
    assert len(m.language) == 1
    assert m.language[0] == "test"

    m.add_keyword("test")
    assert len(m.keywords) == 1
    assert m.keywords[0] == "test"

    s = m.temporal.add_timeseries(None, None, None, None, "test")
    assert s == m.temporal.timeseries[0]
    assert len(m.temporal.timeseries) == 1
    assert m.temporal.timeseries[0].aggregationType == "test"

    s = m.sources[0].add_license("test", None, None, None, None)
    assert s == m.sources[0].licenses[0]
    assert len(m.sources[0].licenses) == 1
    assert m.sources[0].licenses[0].name == "test"

    assert m.resources[0].schema.dialect.delimeter is None
    assert m.resources[0].schema.dialect.decimalSeparator == "."

    m.resources[0].schema.add_primary_key("test")
    f = m.resources[0].schema.add_field("test", None, None, None)
    fk = m.resources[0].schema.add_foreign_key()
    assert m.resources[0].schema.primaryKey[0] == "test"

    assert f == m.resources[0].schema.fields[0]
    assert m.resources[0].schema.fields[0].name == "test"
    assert len(m.resources[0].schema.fields) == 1

    assert fk == m.resources[0].schema.foreignKeys[0]
    assert len(m.resources[0].schema.foreignKeys) == 1

    m.resources[0].schema.foreignKeys[0].add_field("test")
    assert len(m.resources[0].schema.foreignKeys[0].fields) == 1
    assert m.resources[0].schema.foreignKeys[0].fields[0] == "test"
