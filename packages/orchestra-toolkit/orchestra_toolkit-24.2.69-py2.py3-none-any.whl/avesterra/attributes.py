""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import avesterra.aspects as aspects
from avesterra.avial import *
from avesterra.taxonomy import AvAttribute, AvAspect


def insert_attribute(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Inserts an attribute of `attribute` and `value` at `index`, if specified, into `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to insert into `entity`
    value : AvValue
        Value to insert into attribute `attribute`
    index : AvIndex
        Index to insert the attribute into
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Insert attribute using `attribute`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(4), authorization=authorization)

    >>> import avesterra.attributes as attributes # Insert attribute into `index`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.ENTITY, value=AvValue.encode_integer(2), authorization=authorization)
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.WIDTH, index=2, value=AvValue.encode_integer(3), authorization=authorization)


    Raises
    ______
    ApplicationError
        When an attribute of `attribute` is already present

    """
    aspects.insert(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        value=value,
        index=index,
        parameter=parameter,
        authorization=authorization,
    )


def remove_attribute(
    entity: AvEntity,
    authorization: AvAuthorization,
    index: AvIndex = NULL_INDEX,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Removes an attribute `attribute` at `index` from `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    index : AvIndex
        Index to insert the attribute into
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Remove last attribute from `entity`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(4), authorization=authorization)
    >>> attributes.remove_attribute(entity=entity, authorization=authorization)


    >>> import avesterra.attributes as attributes # Remove attribute at `index` 2 from `entity`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(4), authorization=authorization)
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.ENTITY, value=AvValue.encode_integer(4), authorization=authorization)
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.ATTRIBUTION, value=AvValue.encode_integer(4), authorization=authorization)
    >>> attributes.remove_attribute(entity=entity, index=2, authorization=authorization)

    Raises
    ______
    ApplicationError
        When an attribute of `attribute` is already present

    """
    aspects.remove(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        index=index,
        parameter=parameter,
        authorization=authorization,
    )


def replace_attribute(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Replace attribute at `index` with attribute of `attribute` and `value`; replaces last attribute if `index` == NULL_INDEX

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to use
    index : AvIndex
        Index of the attribute that will be replaced
    value : AvValue
        Value to use
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Replace last attribute on `entity`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(2), authorization=authorization)
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.WIDTH, value=AvValue.encode_integer(3), authorization=authorization)
    >>> attributes.replace_attribute(entity=entity, index=2, attribute=AvAttribute.TERRITORY, value=AvValue.encode_integer(4), authorization=authorization)

    Raises
    ______
    ApplicationError
        When an attribute of `attribute` is already present

    """
    aspects.replace(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        value=value,
        index=index,
        parameter=parameter,
        authorization=authorization,
    )


def find_attribute(
    entity: AvEntity,
    authorization: AvAuthorization,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
) -> AvIndex:
    """Find attribute of value `value` on entity after `index`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    index : AvIndex
        Index where the search will start
    value : AvValue
        Value to search for
    instance : AvInstance
        Instance(Property Table Index) in which the annotation will be inserted
    authorization : AvAuthorization
        An authorization that is able to read from `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Replace last attribute on `entity`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(2), authorization=authorization)
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.WIDTH, value=AvValue.encode_integer(3), authorization=authorization)
    >>> print(attributes.find_attribute(entity=entity, index=2, value=AvValue.encode_integer(2), authorization=authorization))
    2

    >>> import avesterra.attributes as attributes # Replace last attribute on `entity`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(2), authorization=authorization)
    >>> attributes.insert_attribute(entity=entity, attribute=AvAttribute.WIDTH, value=AvValue.encode_integer(3), authorization=authorization)
    >>> print(attributes.find_attribute(entity=entity, value=AvValue.encode_integer(0), authorization=authorization))
    0

    """
    return aspects.find(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        value=value,
        index=index,
        authorization=authorization,
    )


def include_attribute(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    parameter: AvParameter = NULL_PARAMETER,
    value: AvValue = NULL_VALUE,
) -> None:
    """Include attribute `attribute` of value `value` on `entity`; will overwrite `attribute` if already present

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to include
    value : AvValue
        Value to include
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Include new attribute
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.include_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.include_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(2), authorization=authorization)
    >>> attributes.include_attribute(entity=entity, attribute=AvAttribute.WIDTH, value=AvValue.encode_integer(3), authorization=authorization)

    >>> import avesterra.attributes as attributes # Overwrite previously included attribute
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.include_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.include_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(2), authorization=authorization)

    """
    return aspects.include(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        value=value,
        parameter=parameter,
        authorization=authorization,
    )


def exclude_attribute(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Exclude attribute `attribute` from `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to include
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Include new attribute
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.include_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.exclude_attribute(entity=entity, attribute=AvAttribute.WEIGHT, authorization=authorization)

    """
    return aspects.exclude(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        parameter=parameter,
        authorization=authorization,
    )


def set_attribute(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Set attribute `attribute` with `value` on `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to set
    value : AvValue
        Value to set
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Set attribute
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)

    >>> import avesterra.attributes as attributes # Overwrite attribute with new value
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(2), authorization=authorization)

    """
    return aspects.set(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        value=value,
        parameter=parameter,
        authorization=authorization,
    )


def get_attribute(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
) -> AvValue:
    """Get value of attribute `attribute` on `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to set
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Get attribute
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.get_attribute(entity=entity, attribute=AvAttribute.HEIGHT, authorization=authorization).decode_integer())
    1

    >>> import avesterra.attributes as attributes # Get non-existent attribute
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.get_attribute(entity=entity, attribute=AvAttribute.WIDTH, authorization=authorization))
    {"NULL": ""}

    """
    return aspects.get(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        authorization=authorization,
    )


def clear_attribute(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Clear value of attribute `attribute` on `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to set
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Clear attribute `attribute` value
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.clear_attribute(entity=entity, attribute=AvAttribute.HEIGHT, authorization=authorization)
    >>> print(attributes.get_attribute(entity=entity, attribute=AvAttribute.WIDTH, authorization=authorization))
    {"NULL": ""}

    """
    aspects.clear(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        parameter=parameter,
        authorization=authorization,
    )


def attribute_count(
    entity: AvEntity,
    authorization: AvAuthorization,
) -> AvCount:
    """Get number of attributes on `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Get attribute count on `entity`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.attribute_count(entity=entity, authorization=authorization))
    1

    >>> import avesterra.attributes as attributes # Get attribute count on `entity` with no attributes
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> print(attributes.attribute_count(entity=entity, authorization=authorization))
    0

    """
    return aspects.count(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        authorization=authorization,
    )


def attribute_member(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
) -> bool:
    """Check if attribute `attribute` exists on `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to check for
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Check if `attribute` exists on `entity`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.attribute_member(entity=entity, attribute=AvAttribute.HEIGHT, authorization=authorization))
    True

    >>> import avesterra.attributes as attributes # Check if non-existent `attribute` exists on `entity`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.attribute_member(entity=entity, attribute=AvAttribute.HEAT, authorization=authorization))
    False

    >>> import avesterra.attributes as attributes # Check if `attribute` exists on `entity` with no attributes
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> print(attributes.attribute_member(entity=entity, attribute=AvAttribute.HEIGHT, authorization=authorization))
    False

    """
    return aspects.member(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        authorization=authorization,
    )


def attribute_name(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    index: AvIndex = NULL_INDEX,
) -> AvName:
    """Return attribute name(NULL_ATTRIBUTE, LOCATION_ATTRIBUTE, etc.) at `attribute` or `index` on `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to get name of
    index : AvIndex
        Index to get name of
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Get name of `attribute`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.attribute_name(entity=entity, attribute=AvAttribute.HEIGHT, authorization=authorization))
    ATTRIBUTE_HEIGHT

    >>> import avesterra.attributes as attributes # Get name of attribute at `index`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.ATTRIBUTE, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.attribute_name(entity=entity, index=1, authorization=authorization))
    ATTRIBUTE_ATTRIBUTE

    """
    return aspects.name(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        index=index,
        authorization=authorization,
    )


def attribute_key(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    index: AvIndex = NULL_INDEX,
) -> AvKey:
    """Return attribute key(NULL_ATTRIBUTE, LOCATION_ATTRIBUTE, etc.) at `attribute` or `index` on `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to get key of
    index : AvIndex
        Index to get key of
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Get name of `attribute`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.attribute_key(entity=entity, attribute=AvAttribute.HEIGHT, authorization=authorization))
    ATTRIBUTE_HEIGHT

    >>> import avesterra.attributes as attributes # Get name of attribute at `index`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.ATTRIBUTE, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.attribute_name(entity=entity, index=1, authorization=authorization))
    ATTRIBUTE_ATTRIBUTE

    """
    return aspects.key(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        index=index,
        authorization=authorization,
    )


def attribute_value(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    index: AvIndex = NULL_INDEX,
) -> AvValue:
    """Return value of attribute `attribute` or `index` on `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to get key of
    index : AvIndex
        Index to get key of
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Get value of attribute at `attribute`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.attribute_value(entity=entity, attribute=AvAttribute.HEIGHT, authorization=authorization).decode_integer())
    1

    >>> import avesterra.attributes as attributes # Get name of attribute at `index`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> print(attributes.attribute_value(entity=entity, index=1, authorization=authorization))
    1

    Raises
    ______
    ApplicationError
        When an attribute of `attribute` is not present on `entity`

    """
    return aspects.value(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        index=index,
        authorization=authorization,
    )


def attribute_index(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
) -> AvIndex:
    """Return index of attribute `attribute` on `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute to get key of
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Get index of attribute at `attribute`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.WIDTH, value=AvValue.encode_integer(2), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(3), authorization=authorization)
    >>> print(attributes.attribute_index(entity=entity, attribute=AvAttribute.WIDTH, authorization=authorization))
    2

    >>> import avesterra.attributes as attributes # Get index of attribute at `index`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.WIDTH, value=AvValue.encode_integer(2), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(3), authorization=authorization)
    >>> print(attributes.attribute_index(entity=entity, attribute=AvAttribute.LOCATION, authorization=authorization))
    0

    """
    return aspects.index(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        attribute=attribute,
        authorization=authorization,
    )


def sort_attributes(
    entity: AvEntity,
    authorization: AvAuthorization,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Sort attributes on `entity` by ordinal value in Taxonomy

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Sort attributes by ordinal value in Taxonomy
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.WIDTH, value=AvValue.encode_integer(2), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(3), authorization=authorization)
    >>> attributes.sort_attributes(entity=entity, authorization=authorization)

    """
    aspects.sort(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        parameter=parameter,
        authorization=authorization,
    )


def purge_attributes(
    entity: AvEntity,
    authorization: AvAuthorization,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Purge all attributes on `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Purge all attributes on `entity`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.WIDTH, value=AvValue.encode_integer(2), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(3), authorization=authorization)
    >>> attributes.purge_attributes(entity=entity, authorization=authorization)
    >>> print(attributes.attribute_count(entity=entity, authorization=authorization))
    0

    """
    aspects.purge(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        parameter=parameter,
        authorization=authorization,
    )


def retrieve_attributes(
    entity: AvEntity,
    authorization: AvAuthorization,
) -> AvInterchange:
    """Retrieve attreibutes of `entity` in AvInterchange format

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.attributes as attributes # Sort attributes by ordinal value in Taxonomy
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attributes
    >>> authorization: AvAuthorization
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.HEIGHT, value=AvValue.encode_integer(1), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.WIDTH, value=AvValue.encode_integer(2), authorization=authorization)
    >>> attributes.set_attribute(entity=entity, attribute=AvAttribute.WEIGHT, value=AvValue.encode_integer(3), authorization=authorization)
    >>> print(attributes.retrieve_attributes(entity=entity, authorization=authorization))
    {"Attributes":[["HEIGHT_ATTRIBUTE",{"INTEGER":"1"},[]],["WIDTH_ATTRIBUTE",{"INTEGER":"2"},[]],["WEIGHT_ATTRIBUTE",{"INTEGER":"3"},[]]]}
    """
    return aspects.retrieve(
        aspect=AvAspect.ATTRIBUTE,
        entity=entity,
        authorization=authorization,
    )
