""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import avesterra.aspects as aspects
from avesterra.avial import *


def insert_property(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Inserts a property into a `entity`'s property table; must provide key, index, or both

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    name : AvName
        Name of the property that will be inserted
    key : AvKey
        Key of the property that will be inserted
    value : AvValue
        Value of the property that will be inserted
    index : AvIndex
        Index in the property table where the new property will be inserted
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Insert property using key
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> properties.insert_property(entity=entity, name=name, key=key, value=AvValue.encode_text("Some example text!"), authorization=authorization) # Inserted at end of property table

    >>> import avesterra.properties as properties # Insert properties using index
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="First example", index=1, value=AvValue.encode_text("Some example text!"), authorization=authorization) # Inserts property at index 1
    >>> properties.insert_property(entity=entity, name="Second example", index=2, value=AvValue.encode_text("Some better example text!"), authorization=authorization) # Inserts property at index 2

    >>> import avesterra.annotation as annotation # Insert property between two previously inserted properties
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="First", key="first_key", value=AvValue.encode_text("Some example text!"), authorization=authorization) # Inserted at end of property table
    >>> properties.insert_property(entity=entity, name="Second", key="first_key", value=AvValue.encode_text("Some better example text!"), authorization=authorization) # Inserted at end of property table
    >>> properties.insert_property(entity=entity, name="Inserted between First and Second", index=2, value=AvValue.encode_text("Some epic example text!"), authorization=authorization) # Inserted between the previous two properties

    Raises
    ______
    ApplicationError
        When a property of a given key already exists in the property table

    """
    aspects.insert(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        name=name,
        key=key,
        value=value,
        index=index,
        parameter=parameter,
        authorization=authorization,
    )


def remove_property(
    entity: AvEntity,
    index: AvIndex = NULL_INDEX,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Remove property at the given index; remove from the end of the property table if NULL_INDEX is given

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    index : AvIndex
        Index of the property that will be removed; if NULL_INDEX, the last property in the property table will be removed
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Remove 2nd property in property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Some example text!"), authorization=authorization) # Inserted at end of property table
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("I am feeling very temporary!"), authorization=authorization) # Inserted at end of property table
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Some even better example text!"), authorization=authorization) # Inserted at end of property table
    >>> properties.remove_property(entity=entity, index=2, authorization=authorization) # Remove property at index 2

    >>> import avesterra.properties as properties # Remove last property in property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Some example text!"), authorization=authorization) # Inserted at end of property table
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Some better example text!"), authorization=authorization) # Inserted at end of property table
    >>> properties.remove_property(entity=entity, authorization=authorization) # Remove last property from property table


    Raises
    ______
    ApplicationError
        If called on an empty property table

    """
    aspects.remove(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        index=index,
        parameter=parameter,
        authorization=authorization,
    )


def replace_property(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Replace property at index in property table

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    name : AvName
        Name of the replacement property
    key : AvKey
        This field has no effect...except that it shouldn't already be present in the property table
    value : AvValue
        Value of the replacement property
    index : AvIndex
        Index of the property that will be removed; if NULL_INDEX, the last property in the property table will be removed
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Remove 2nd property in property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("I am feeling very temporary!"), authorization=authorization) # Inserted at end of property table
    >>> properties.replace_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("I am feeling very temporary!"), authorization=authorization) # Inserted at end of property table

    >>> import avesterra.properties as properties # Remove last property in property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Some example text!"), authorization=authorization) # Inserted at end of property table
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Some better example text!"), authorization=authorization) # Inserted at end of property table
    >>> properties.remove_property(entity=entity, authorization=authorization) # Remove last property from property table


    Raises
    ______
    ApplicationError
        If called on an empty property table

    """
    aspects.replace(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        name=name,
        key=key,
        value=value,
        index=index,
        parameter=parameter,
        authorization=authorization,
    )


def find_property(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    """Find the index of a property, in the property table, searching from `index` -> N; return 0 if no such property is found.
    Both value and name are searched for at the same time, and the index of the first property to match either `name` or `value` will be returned!


    Parameters
    __________
    entity : AvEntity
        Target entity euid
    name : AvName
        Name to find in the property table; secondary search priority
    value : AvValue
        Value to find in the property table; primary search priority
    index : AvIndex
        Index in the property table to begin the search
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Search by name only
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("3"), authorization=authorization)
    >>> print(properties.find_property(entity=entity, name="Name 2", authorization=authorization))
    2

    >>> import avesterra.properties as properties # Search by value only
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("3"), authorization=authorization)
    >>> print(properties.find_property(entity=entity, value=AvValue.encode_text("3"), authorization=authorization))
    3

    >>> import avesterra.properties as properties # Search by name and value; return the first match of either name or value
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("3"), authorization=authorization)
    >>> print(properties.find_property(entity=entity, name="1", value=AvValue.encode_text("3"), authorization=authorization))
    1

    >>> import avesterra.properties as properties # Search for name or value starting at index
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("3"), authorization=authorization)
    >>> print(properties.find_property(entity=entity, name="1", value=AvValue.encode_text("3"), index=2, authorization=authorization))
    3

    """
    return aspects.find(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        name=name,
        value=value,
        index=index,
        authorization=authorization,
    )


# ASKJ the difference between set and include


def include_property(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Include property in property table.

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    name : AvName
        Name of the replacement property
    key : AvKey
        Key to include the proeprty under
    value : AvValue
        Value of the replacement property
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Include property in property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.include_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("I am gonna be included!"), authorization=authorization) # Inserted at end of property table

    """
    aspects.include(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        name=name,
        key=key,
        value=value,
        parameter=parameter,
        authorization=authorization,
    )


def exclude_property(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Exclude property of `key` from property table

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key to exclude the from the property table
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Exclude property from property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.include_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("I am gonna be included!"), authorization=authorization)
    >>> properties.include_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("I think that I may be excluded!"), authorization=authorization)
    >>> properties.include_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("I am flying high!"), authorization=authorization)
    >>> properties.exclude_property(entity=entity, key="key_2", authorization=authorization) # Exclude property of key "key_2" from property table""


    """
    aspects.exclude(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        key=key,
        parameter=parameter,
        authorization=authorization,
    )


def set_property(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Set property in property table; new property created if key nopt alreadt present

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    name : AvName
        Name of the to be set property
    key : AvKey
        Key of the to be set property
    value : AvValue
        Value of the to be set property
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Include property in property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.include_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("I am gonna be included!"), authorization=authorization) # Inserted at end of property table

    """
    aspects.set(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        name=name,
        key=key,
        value=value,
        parameter=parameter,
        authorization=authorization,
    )


def get_property(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Get the value of a property using a key; returns NULL_VALUE if given key doesn't exist in property tables

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of property to get the value of
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Get existent value
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("The value to pull"), authorization=authorization)
    >>> print(properties.get_property(entity=entity, key="key_1", authorization=authorization).decode_text())
    "The value to pull"

    >>> import avesterra.properties as properties # Attempt to get non-existent value
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("The value to pull"), authorization=authorization)
    >>> print(properties.get_property(entity=entity, key="nonexistent", authorization=authorization))
    {"NULL": ""}

    """
    return aspects.get(
        entity=entity, aspect=AvAspect.PROPERTY, key=key, authorization=authorization
    )


def clear_property(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Clear the value of the property if key

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of property to get the value of
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Clear property value
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("A cool value"), authorization=authorization)
    >>> properties.clear_property(entity=entity, key="key_1", authorization=authorization)
    >>> print(properties.get_property(entity=entity, key="key_1", authorization=authorization))
    {"NULL": ""}

    """
    aspects.clear(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        key=key,
        parameter=parameter,
        authorization=authorization,
    )


def property_count(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvCount:
    """Get the number of properties set in the property table

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Get number of properties set in the property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_3", value=AvValue.encode_text("1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_3", value=AvValue.encode_text("2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("3"), authorization=authorization)
    >>> print(properties.property_count(entity=entity, authorization=authorization))
    3

    """
    return aspects.count(
        entity=entity, aspect=AvAspect.PROPERTY, authorization=authorization
    )


def property_member(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvBoolean:
    """Check if a property of `key` exists in the property table; True if exists, False if not

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key to check for
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Check for existent key
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("The value to pull"), authorization=authorization)
    >>> print(properties.property_member(entity=entity, key="key_1", authorization=authorization))
    True

    >>> import avesterra.properties as properties # Check for non-existent key
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> print(properties.property_member(entity=entity, key="non-existent", authorization=authorization))
    False

    """
    return aspects.member(
        entity=entity, aspect=AvAspect.PROPERTY, key=key, authorization=authorization
    )


def property_name(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvName:
    """Get the name of the property at `key` or `index`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of property to get name of
    index : AvIndex
        Index of property to get name of
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Get the name of the property that has key `key_3`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Value 1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Value 2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Value 3"), authorization=authorization)
    >>> print(properties.property_name(entity=entity, key="key_3", authorization=authorization))
    "Name 3"

    >>> import avesterra.properties as properties # Get the name of the 3rd property
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Value 1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Value 2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Value 3"), authorization=authorization)
    >>> print(properties.property_name(entity=entity, index=3, authorization=authorization))
    "Name 3"

    Raises
    ______
    ApplicationError
        If `key` or `index` doesn't exist; is also raised if `key` and `index` are both provided, but they map to different properties

    """
    return aspects.name(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        key=key,
        index=index,
        authorization=authorization,
    )


def property_key(
    entity: AvEntity,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvKey:
    """Get the key of property at `index`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    index : AvIndex
        Index of property to get name of
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Get the key of the 2nd property in property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Value 1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Value 2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Value 3"), authorization=authorization)
    >>> print(properties.property_key(entity=entity, key=2, authorization=authorization))
    "key_2"

    Raises
    ______
    ApplicationError
        If property table doesn't have a property at index `index`

    """
    return aspects.key(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        index=index,
        authorization=authorization,
    )


def property_value(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Return the value of a property at key `key` or index `index`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of property to return value of
    index : AvIndex
        Index of property to return value of
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Return the value of the property that is mapped to key `key_2`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Value 1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Value 2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Value 3"), authorization=authorization)
    >>> print(properties.property_value(entity=entity, key="key_2", authorization=authorization).decode_text())
    "Value 2"

    >>> import avesterra.properties as properties # Return the value of the 3rd property in the property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Value 1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Value 2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Value 3"), authorization=authorization)
    >>> print(properties.property_value(entity=entity, index=3, authorization=authorization).decode_text())
    "Value 3"

    Raises
    ______
    ApplicationError
        If `key` or `index` doesn't exist; is also raised if `key` and `index` are both provided, but they map to different properties

    """
    return aspects.value(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        key=key,
        index=index,
        authorization=authorization,
    )


def property_index(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    """Return the index of the property at key `key`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of property to return index of
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Return the index of the property that is mapped to key `key_2`
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Value 1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Value 2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Value 3"), authorization=authorization)
    >>> print(properties.property_index(entity=entity, key="key_2", authorization=authorization))
    2

    >>> import avesterra.properties as properties # Get the index of a non-existent property
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Value 1"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Value 2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Value 3"), authorization=authorization)
    >>> print(properties.property_index(entity=entity, key="i_dont_exist", authorization=authorization))
    0

    """
    return aspects.index(
        entity=entity, aspect=AvAspect.PROPERTY, key=key, authorization=authorization
    )


def property_attribute(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvAttribute:
    """#ASKJ

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of property to return index of
    index : AvIndex
        Index...something...something...something
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    # TODO

    """
    return aspects.attribute(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        key=key,
        index=index,
        authorization=authorization,
    )


def sort_properties(
    entity: AvEntity,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Sort property table; #ASKJ the sorting order...value...name...key...all the above?

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

    >>> import avesterra.properties as properties # Sort property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Value 2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Value 3"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Value 1"), authorization=authorization)
    >>> properties.sort_properties(entity=entity, authorization=authorization)

    """
    aspects.sort(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        parameter=parameter,
        authorization=authorization,
    )


def purge_properties(
    entity: AvEntity,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Purge all properties from property table

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

    >>> import avesterra.properties as properties # Sort property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Value 2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Value 3"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Value 1"), authorization=authorization)
    >>> properties.purge_properties(entity=entity, authorization=authorization)

    """
    aspects.purge(
        entity=entity,
        aspect=AvAspect.PROPERTY,
        parameter=parameter,
        authorization=authorization,
    )


def retrieve_properties(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvInterchange:
    """Return contents of property table as an Interchange(JSON)

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.properties as properties # Sort property table
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports properties
    >>> authorization: AvAuthorization
    >>> properties.insert_property(entity=entity, name="Name 2", key="key_2", value=AvValue.encode_text("Value 2"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 3", key="key_3", value=AvValue.encode_text("Value 3"), authorization=authorization)
    >>> properties.insert_property(entity=entity, name="Name 1", key="key_1", value=AvValue.encode_text("Value 1"), authorization=authorization)
    >>> print(properties.retrieve_properties(entity=entity, authorization=authorization))
    {"Properties":[["Name 2","key_2",{"TEXT":"Value 2"}],["Name 3","key_3",{"TEXT":"Value 3"}],["Name 1","key_1",{"TEXT":"Value 1"}]]}

    """
    return aspects.retrieve(
        entity=entity, aspect=AvAspect.PROPERTY, authorization=authorization
    )
