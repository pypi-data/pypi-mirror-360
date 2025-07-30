# What is ioprocmeta

ioprocmeta is a library providing interfaces for writing and reading and processing meta data formats like the [Open Energy Platform meta data format 1.5.0](https://github.com/OpenEnergyPlatform/oemetadata).

The library currently implements only the OEP 1.5.0 meta data format, but can be extended to other meta data formats.

ioprocmeta provides:

- class based interface representing hierarchical meta data formats
- serialisation of the meta data into a text format (at the moment json)
- serialisation of the meta data format into python _dict()_
- checks for data consistency on the level of used data types and completeness of information
- provides a default valid meta data structure that can be used as a template

# Installation

ioprocmeta is pip installable via: `pip install ioprocmeta`.

If you use a virtual environment system like conda or virtualenv then the usual ceveats apply. Please activate/source your environment prior to installing ioprocmeta via pip.

Dependencies:

- attrs
- cattrs

# How to use

ioprocmeta provides interface classes, which represent a meta data format. Each class can be instantiated without input and will then contain defaults for all meta data fields.

To access the meta data classes ioprocmeta provides two ways. The first is by direct import:

```python
from ioprocmeta.oep import OEPMeta_1_5_0

meta_data = OEPMeta_1_5_0()

```

Alternatively you can also request a meta data class based on the identifier of the meta data format via the ioprocmeta registry:

```python
import ioprocmeta as prov

MetaDataClass = prov.available_standard_formats['oep150']
meta_data = MetaDataClass()

# the identifier of the meta data format can be accessed like this:
meta_data.type()
```

After creating a meta data instance you can provide information, more precisely set fields with the necessary information.
Here some examples for the oep meta data format in version 1.5.0:

```python
from ioprocmeta.oep import OEPMeta_1_5_0

meta_data = OEPMeta_1_5_0()

meta_data.name = 'Jane Doe'
```

Most meta data formats are hierarchical and have subsections for some of the stored information. To set information in a subsection a method call is usually required:

```python
meta_data.add_contributor(
    title='John Doe', 
    email='John.Doe@doe.net', 
    date=datetime.date(1970, 1, 1), 
    _object=None, 
    comment='Personal correspondance',
)
```

After filling out the meta data field, you most likely would want to write the meta data as a json file to disk:

```python
meta_data.write_json(pathlib.Path('./meta.json'))
```

Alternatively you can also get the json string, if you do not want to write the data immediately to disk:

```python
meta_json = meta_data.as_json()
```

And if you want to make your own serialisation or work with a dictionary in python you can also get the data transformed:

```python
meta_dict = meta_data.as_dict()
```

If you want to know which fields to fill in a specific meta data specification, please look up the corresponding documentation of the meta data specification. There all information should be noted down and also which defaults are acceptable or what should be noted down for missing values.

# Good to know when using ioprocmeta

- subsections are created with interface methods like `add_license()`
- to parse meta data from a json string or a dict, please use the supplied interfaces on the class level with the following syntax: `meta = OEPMeta_1_5_0.from_json(json_data)`.

# Technical / design information

ioprocmeta relies heavily on attrs and cattr library to create an object related mapper to the underlying meta data files.
It provides read and write methods and serialization to json. The meta data objects are classes with attributes representing fields in the meta data specification.

Subsections or hierarchies in the meta data specification are implemented as classes that are integrated into a hierarchical class structure via composition.

One central design decision is, that each subsection in the meta data specification is interfaced with a method in the mother class. This method is responsible for creating an instance of the class representing the subsection and
for setting all values based on the arguments passed to the method.

An example for this is the subsection "license" in the OEP 1.5.0 which is represented by the class __OEPLicense_.
The mother class is in this case __OEPSource_ (section "source" in OEP 1.5.0) has implemented a method _add_license()_.

```python
def add_license(self, name, title, path, instruction, attribution):
    ...
```

The signature of the method indicates, that the license information required by OEP 1.5.0 is the name, title, path and so on.

The streaming of specific information with special datatypes that are not fundamental like int or bool, requires a special translation or serialisation interface.
The cattr library has a hook interface forseen for this occasion and ioprocmeta implements an appropriate class for this interface called _StructuringConverter_.
This structuring converter implements serialisations for _datetime.date_ and _pathlib.Path_ data types into string and back.

## Design quirks

- Subsections are implemented by generator methods that then create a class instance representing the substructure. The sub classes are not intended to be instantiated directly.
- Parsing methods like _from_dict_ or _from_json_, are implemented as classmethods or in other words as alternative constructors / factories which return a complete instance representing the provided data.
This has implications, as a custom serialisation for data types like _datetime.date_ is needed. Due to the design of attrs and cattrs it is currently necessary
to instantiate the serialisation class after the meta data class object is available. This could be solved by using the post init hook provided by cattrs and which could instantiate a serialisation interface class after the instance is initialized. This approach has two drawbacks. First, all constructor methods like _from_dict_ could not be implemented as classmethods and second the serialisation interface class could not be provided by inheritance. The second point would increase complexity for developers as they would be required to not only inherit from an abstract base class and follow the instructions there but also to have to implement an attrs post init hook to instantiate the serialisation interface. To circumvent this ioprocmeta decided to rely on an injection mechanism based on a decorator. The decorator, defined in the "base.py" module, checks if the __converter_ attribute (defined and inherited from the BaseMeta class) is set (in other words, is not set to None). If this is not the case, the decorator sets the attribute __converter_ to a new instance of the serialisation interface _StructuringConverter()_. This enables ioprocmeta the definition of generic interface class methods for serialisation into dict and json which can be inherited directly from the _BaseMeta_ class. To facilitate cleanup before and after serialisation, post processsing hooks are implemented as classmethods __post_as_dict_cleanup_ and __post_from_dict_cleanup_. These can be overridden in a meta data class definition to clean up fields after parsing a json file for example. Other serialisation methods should therefor be implemented in the BaseMeta class and not in any meta data class. Meta classes should implement, if needed, the hooks __post_as_dict_cleanup_ and __post_from_dict_cleanup_ as abstract class methods.

# License

ioprocmeta is available under BSD 3 clause.

# Contact

The library is developed by Benjamin Fuchs, Jan Buschmann and Felix Nitsch. If you want to get in touch, we recommend the gilab issue system. Or if you want to contact us via email then please refer to [Benjamin.Fuchs@dlr.de](mailto:Benjamin.Fuchs@dlr.de).
