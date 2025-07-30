import datetime
import pathlib as pt
from typing import List, Optional, Tuple, Union

import attr


@attr.define
class _OEPTimeseries:
    start: Optional[str] = attr.ib(None)
    end: Optional[str] = attr.ib(None)
    resolutionValue: Optional[str] = attr.ib(None)
    resolutionUnit: Optional[str] = attr.ib(None)
    alignment: Optional[str] = attr.ib(None)
    aggregationType: Optional[str] = attr.ib(None)


@attr.define
class _OEPTemporal:
    referenceDate: Optional[str] = attr.ib(None)
    timeseries: list = attr.ib(factory=list)

    def add_timeseries(
        self,
        start=None,
        end=None,
        resolutionValue=None,
        resolutionUnit=None,
        alignment=None,
        aggregationType=None,
    ):
        _ = _OEPTimeseries(
            start=start,
            end=end,
            resolutionValue=resolutionValue,
            resolutionUnit=resolutionUnit,
            alignment=alignment,
            aggregationType=aggregationType,
        )
        self.timeseries.append(_)
        return _


@attr.define
class _OEPSourceLicense:
    name: Optional[str] = attr.ib(None)
    title: Optional[str] = attr.ib(None)
    path: Optional[str] = attr.ib(None)
    instruction: Optional[str] = attr.ib(None)
    attribution: Optional[str] = attr.ib(None)
    copyrightStatement: Optional[str] = attr.ib(None)


@attr.define
class _OEPSource:
    title: Optional[str] = attr.ib(None)
    authors: Optional[list] = attr.ib(None)
    description: Optional[str] = attr.ib(None)
    publicationYear: Optional[str] = attr.ib(None)
    path: Optional[str] = attr.ib(None)

    sourceLicense: list = attr.ib(factory=list)

    def add_sourceLicense(
        self,
        name=None,
        title=None,
        path=None,
        instruction=None,
        attribution=None,
        copyrightStatement=None,
    ):
        _ = _OEPSourceLicense(
            name=name,
            title=title,
            path=path,
            instruction=instruction,
            attribution=attribution,
            copyrightStatement=copyrightStatement,
        )
        self.sourceLicense.append(_)
        return _


@attr.define
class _OEPLicense:
    name: Optional[str] = attr.ib(None)
    title: Optional[str] = attr.ib(None)
    path: Optional[str] = attr.ib(None)
    instruction: Optional[str] = attr.ib(None)
    attribution: Optional[str] = attr.ib(None)
    copyrightStatement: Optional[str] = attr.ib(None)


@attr.define
class _OEPContributor:
    title: Optional[str] = attr.ib(None)
    path: Optional[str] = attr.ib(None)
    organization: Optional[str] = attr.ib(None)
    roles: Optional[list] = attr.ib(None)
    date: Optional[str] = attr.ib(None)
    object: Optional[str] = attr.ib(None)
    comment: Optional[str] = attr.ib(None)


@attr.define
class _OEPIsabout:
    name: Optional[str] = attr.ib(None)
    at_id: Optional[str] = attr.ib(None)


@attr.define
class _OEPValuereference:
    value: Optional[str] = attr.ib(None)
    name: Optional[str] = attr.ib(None)
    at_id: Optional[str] = attr.ib(None)


@attr.define
class _OEPReference:
    resource: Optional[str] = attr.ib(None)
    fields: Optional[list] = attr.ib(None)


@attr.define
class _OEPForeignkey:
    fields: Optional[list] = attr.ib(None)
    reference: _OEPReference = attr.ib(factory=_OEPReference)


@attr.define
class _OEPField:
    name: Optional[str] = attr.ib(None)
    description: Optional[str] = attr.ib(None)
    type: Optional[str] = attr.ib(None)
    nullable: Optional[str] = attr.ib("false")
    unit: Optional[str] = attr.ib(None)

    isAbout: list = attr.ib(factory=list)

    def add_isabout(self, name=None, at_id=None):
        _ = _OEPIsabout(name=name, at_id=at_id)
        self.isAbout.append(_)
        return _

    valueReference: list = attr.ib(factory=list)

    def add_valuereference(self, value=None, name=None, at_id=None):
        _ = _OEPValuereference(value=value, name=name, at_id=at_id)
        self.valueReference.append(_)
        return _


@attr.define
class _OEPSchema:
    fields: list = attr.ib(factory=list)

    def add_fields(
        self,
        name=None,
        description=None,
        type=None,
        nullable=None,
        unit=None,
        isAbout=None,
        valueReference=None,
    ):
        _ = _OEPField(
            name=name,
            description=description,
            type=type,
            nullable=nullable,
            unit=unit,
            isAbout=isAbout,
            valueReference=valueReference,
        )
        self.fields.append(_)
        return _

    primaryKey: Optional[list] = attr.ib(None)

    foreignKey: list = attr.ib(factory=list)

    def add_foreignKey(self, fields=None, reference=None):
        _ = _OEPForeignkey(fields=fields, reference=reference)
        self.foreignKey.append(_)
        return _


@attr.define
class _OEPDialect:
    delimiter: Optional[str] = attr.ib(None)
    decimalSeparator: Optional[str] = attr.ib(None)


@attr.define
class _OEPReview:
    path: Optional[str] = attr.ib(None)
    badge: Optional[str] = attr.ib(None)


@attr.define
class _OEPExtent:
    name: Optional[str] = attr.ib(None)
    at_id: Optional[str] = attr.ib(None)
    resolutionValue: Optional[str] = attr.ib(None)
    resolutionUnit: Optional[str] = attr.ib(None)
    boundingBox: Optional[list] = attr.ib(default=[0, 0, 0, 0])
    crs: Optional[str] = attr.ib(None)


@attr.define
class _OEPLocation:
    address: Optional[str] = attr.ib(None)
    at_id: Optional[str] = attr.ib(None)
    latitude: Optional[str] = attr.ib(None)
    longitude: Optional[str] = attr.ib(None)


@attr.define
class _OEPSpatial:
    location: _OEPLocation = attr.ib(factory=_OEPLocation)
    extent: _OEPExtent = attr.ib(factory=_OEPExtent)


@attr.define
class _OEPContext:
    title: Optional[str] = attr.ib(None)
    homepage: Optional[str] = attr.ib(None)
    documentation: Optional[str] = attr.ib(None)
    sourceCode: Optional[str] = attr.ib(None)
    publisher: Optional[str] = attr.ib(None)
    publisherLogo: Optional[str] = attr.ib(None)
    contact: Optional[str] = attr.ib(None)
    fundingAgency: Optional[str] = attr.ib(None)
    fundingAgencyLogo: Optional[str] = attr.ib(None)
    grantNo: Optional[str] = attr.ib(None)


@attr.define
class _OEPEmbargoperiod:
    start: Optional[str] = attr.ib(None)
    end: Optional[str] = attr.ib(None)
    isActive: bool = attr.ib(False)


@attr.define
class _OEPSubject:
    name: Optional[str] = attr.ib(None)
    at_id: Optional[str] = attr.ib(None)


@attr.define
class _OEPResource:
    at_id: Optional[str] = attr.ib(None)
    name: Optional[str] = attr.ib(None)
    topic: Optional[list] = attr.ib(None)
    title: Optional[str] = attr.ib(None)
    path: Optional[str] = attr.ib(None)
    description: Optional[str] = attr.ib(None)
    language: Optional[list] = attr.ib(None)

    subject: list = attr.ib(factory=list)

    def add_subject(self, name=None, at_id=None):
        _ = _OEPSubject(name=name, at_id=at_id)
        self.subject.append(_)
        return _

    keyword: Optional[list] = attr.ib(None)
    publicationDate: Optional[str] = attr.ib(None)

    embargoPeriod: _OEPEmbargoperiod = attr.ib(factory=_OEPEmbargoperiod)
    context: _OEPContext = attr.ib(factory=_OEPContext)
    spatial: _OEPSpatial = attr.ib(factory=_OEPSpatial)
    temporal: _OEPTemporal = attr.ib(factory=_OEPTemporal)

    source: list = attr.ib(factory=list)

    def add_source(
        self,
        title=None,
        authors=None,
        description=None,
        publicationYear=None,
        path=None,
        sourceLicense=None,
    ):
        _ = _OEPSource(
            title=title,
            authors=authors,
            description=description,
            publicationYear=publicationYear,
            path=path,
            sourceLicense=sourceLicense,
        )
        self.source.append(_)
        return _

    license: list = attr.ib(factory=list)

    def add_license(
        self,
        name=None,
        title=None,
        path=None,
        instruction=None,
        attribution=None,
        copyrightStatement=None,
    ):
        _ = _OEPLicense(
            name=name,
            title=title,
            path=path,
            instruction=instruction,
            attribution=attribution,
            copyrightStatement=copyrightStatement,
        )
        self.license.append(_)
        return _

    contributor: list = attr.ib(factory=list)

    def add_contributor(
        self,
        title=None,
        path=None,
        organization=None,
        roles=None,
        date=None,
        object=None,
        comment=None,
    ):
        _ = _OEPContributor(
            title=title,
            path=path,
            organization=organization,
            roles=roles,
            date=date,
            object=object,
            comment=comment,
        )
        self.contributor.append(_)
        return _

    type: Optional[list] = attr.ib(None)
    format: Optional[str] = attr.ib(None)
    encoding: Optional[str] = attr.ib(None)

    schema: _OEPSchema = attr.ib(factory=_OEPSchema)
    dialect: _OEPDialect = attr.ib(factory=_OEPDialect)
    review: _OEPReview = attr.ib(factory=_OEPReview)

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
