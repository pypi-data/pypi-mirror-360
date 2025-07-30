import datetime
import pathlib as pt
from typing import List, Optional, Tuple, Union

import attr


@attr.define
class _OEPSubject:
    name: Optional[str] = attr.ib(None)
    path: Optional[Union[str, pt.Path]] = attr.ib(None)


@attr.define
class _OEPContext:
    homepage: Optional[str] = attr.ib(None)
    documentation: Optional[str] = attr.ib(None)
    sourceCode: Optional[str] = attr.ib(None)
    contact: Optional[str] = attr.ib(None)
    grantNo: Optional[str] = attr.ib(None)
    fundingAgency: Optional[str] = attr.ib(None)
    fundingAgencyLogo: Optional[str] = attr.ib(None)
    publisherLogo: Optional[str] = attr.ib(None)


@attr.define
class _OEPSpatial:
    location: Optional[str] = attr.ib(None)
    extent: Tuple = attr.ib(factory=lambda: (None, None))
    resolution: Tuple = attr.ib(factory=lambda: (None, None))
    resolution: Tuple = attr.ib(factory=lambda: (None, None))


@attr.define
class _OEPTimeseries:
    start: Optional[Union[datetime.date, str]] = attr.ib(None)
    end: Optional[Union[datetime.date, str]] = attr.ib(None)
    resolution: Optional[str] = attr.ib(None)
    alignment: Optional[str] = attr.ib(None)
    aggregationType: Optional[str] = attr.ib(None)


@attr.define
class _OEPTemporal:
    referenceDate: Optional[Union[datetime.date, str]] = attr.ib(None)
    timeseries: List[_OEPTimeseries] = attr.ib(factory=list)

    def add_timeseries(self, start, end, resolution, alignment, aggregationType):
        ts = _OEPTimeseries(start, end, resolution, alignment, aggregationType)
        self.timeseries.append(ts)
        return ts


@attr.define
class _OEPLicense:
    name: Optional[str] = attr.ib(None)
    title: Optional[str] = attr.ib(None)
    path: Optional[Union[pt.Path, str]] = attr.ib(None)
    instruction: Optional[str] = attr.ib(None)
    attribution: Optional[str] = attr.ib(None)


@attr.define
class _OEPSource:
    title: Optional[str] = attr.ib(None)
    description: Optional[str] = attr.ib(None)
    path: Optional[Union[pt.Path, str]] = attr.ib(None)
    licenses: List[_OEPLicense] = attr.ib(factory=list)

    def add_license(self, name, title, path, instruction, attribution):
        lic = _OEPLicense(name, title, path, instruction, attribution)
        self.licenses.append(lic)
        return lic


@attr.define
class _OEPContributor:
    title: Optional[str] = attr.ib(None)
    email: Optional[str] = attr.ib(None)
    date: Optional[Union[datetime.date, str]] = attr.ib(None)
    object: Optional[str] = attr.ib(None)
    comment: Optional[str] = attr.ib(None)


@attr.define
class _OEPReview:
    path: Optional[Union[pt.Path, str]] = attr.ib(None)
    badge: Optional[str] = attr.ib(None)


@attr.define
class _OEPValueReference:
    value: Optional[str] = attr.ib(None)
    name: Optional[str] = attr.ib(None)
    path: Optional[Union[str, pt.Path]] = attr.ib(None)


@attr.define
class _OEPIsAbout:
    name: Optional[str] = attr.ib(None)
    path: Optional[str] = attr.ib(None)


@attr.define
class _OEPField:
    name: Optional[str] = attr.ib(None)
    description: Optional[str] = attr.ib(None)
    type: Optional[str] = attr.ib(None)
    unit: Optional[str] = attr.ib(None)
    isAbout: List[_OEPIsAbout] = attr.ib(factory=list)
    valueReference: List[_OEPValueReference] = attr.ib(_OEPValueReference)

    def add_is_about(self, name, path):
        ia = _OEPIsAbout(name, path)
        self.isAbout.append(ia)
        return ia

    def add_value_reference(self, value, name, path):
        v = _OEPValueReference(value, name, path)
        self.valueReference.append(v)
        return v


@attr.define
class _OEPReference:
    resource: Optional[str] = attr.ib(None)
    fields: List[str] = attr.ib(factory=list)


@attr.define
class _OEPForeignKey:
    fields: List[str] = attr.ib(factory=list)
    reference: _OEPReference = attr.ib(factory=_OEPReference)

    def add_field(self, name):
        self.fields.append(name)


@attr.define
class _OEPDialect:
    delimeter: Optional[str] = attr.ib(None)
    decimalSeparator: str = attr.ib(".")


@attr.define
class _OEPSchema:
    fields: List[_OEPField] = attr.ib(factory=list)
    primaryKey: List[str] = attr.ib(factory=list)
    foreignKeys: List[_OEPForeignKey] = attr.ib(factory=list)
    dialect: _OEPDialect = attr.ib(factory=_OEPDialect)

    def add_primary_key(self, name):
        self.primaryKey.append(name)

    def add_field(self, name, description, type, unit):
        f = _OEPField(name, description, type, unit)
        self.fields.append(f)
        return f

    def add_foreign_key(self):
        fk = _OEPForeignKey()
        self.foreignKeys.append(fk)
        return fk


@attr.define
class _OEPRessource:
    profile: Optional[str] = attr.ib(None)
    name: Optional[str] = attr.ib(None)
    path: Optional[str] = attr.ib(None)
    format: Optional[str] = attr.ib(None)
    encoding: Optional[str] = attr.ib(None)
    schema: _OEPSchema = attr.ib(factory=_OEPSchema)
    dialect: _OEPDialect = attr.ib(factory=_OEPDialect)
