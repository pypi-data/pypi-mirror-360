"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avial import *
from avesterra.taxonomy import AvAttribute, AvAspect
import avesterra.aspects as aspects


def insert_trait(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Insert trait of `key` or `index` on `attribute` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    name : AvName
        Trait name
    key : AvKey
        Trait key
    value : AvValue
        Trait value
    index : AvIndex
        Index, in the trait list, to insert the new trait
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Insert trait at `key`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)

    >>> import avesterra.traits as traits # Insert trait at `index`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="I am a trait", index=1, value=AvValue.encode_text("I am a trait"), authorization=authorization)

    >>> import avesterra.traits as traits # Insert trait at `index` between two previously inserted traits
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="I am trait 1", index=1, value=AvValue.encode_text("I am a trait 1"), authorization=authorization)
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="I am trait 2", index=2, value=AvValue.encode_text("I am a trait 2"), authorization=authorization)
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="I am line cutter trait", index=2, value=AvValue.encode_text("I am line cutter trait"), authorization=authorization)

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity

    """
    aspects.insert(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        offset=NULL_OFFSET,
        parameter=parameter,
        authorization=authorization,
    )


def remove_trait(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Remove trait of `key` or `index` on `attribute` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    name : AvName
        Trait name
    key : AvKey
        Trait key
    index : AvIndex
        Index, in the trait list, to remove
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Remove trait at `key`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.remove_trait(entity=entity, attribute=attribute, authorization=authorization, key="1")

    >>> import avesterra.traits as traits # Remove trait at `index`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.remove_trait(entity=entity, attribute=attribute, authorization=authorization, index=1)

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity

    """
    aspects.remove(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        index=index,
        instance=instance,
        offset=NULL_OFFSET,
        parameter=parameter,
        authorization=authorization,
    )


def replace_trait(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Replace trait of `key` or `name` on `attribute` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    name : AvName
        New trait name
    key : AvKey
        Trait key
    index : AvIndex
        Index, in the trait list, to replace
    value : AvValue
        New value
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Replace trait at `key`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.replace_trait(entity=entity, attribute=attribute, key="1", name="I am the replacement", value=AvValue.encode_text("I am the replacement"), authorization=authorization)

    >>> import avesterra.traits as traits # Replace trait at `index`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.replace_trait(entity=entity, attribute=attribute, index=1, name="I am the replacement", value=AvValue.encode_text("I am the replacement"), authorization=authorization)

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity

    """
    aspects.replace(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        offset=NULL_OFFSET,
        parameter=parameter,
        authorization=authorization,
    )


def find_trait(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
) -> AvIndex:
    """Find trait index of `key` or `name` on `attribute` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    name : AvName
        Trait name
    key : AvKey
        Trait key
    index : AvIndex
        Index, in the trait list, to begin the find operation
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Find trait of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 1", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 2", key="2", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 3", key="3", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.find_trait(entity=entity, attribute=attribute, key="2", authorization=authorization)
    2

    >>> import avesterra.traits as traits # Find trait of `name` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 1", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 2", key="2", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 3", key="3", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.find_trait(entity=entity, attribute=attribute, name="Trait 3", authorization=authorization)
    3

    >>> import avesterra.traits as traits # Find trait of `name` on `attribute` at `entity` after `index`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 1", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 2", key="2", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 3", key="3", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.find_trait(entity=entity, attribute=attribute, index=1, name="Trait 3", authorization=authorization)
    3

    >>> import avesterra.traits as traits # Perform find for non-existent `name` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 1", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 2", key="2", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.insert_trait(entity=entity, attribute=attribute, name="Trait 3", key="3", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.find_trait(entity=entity, attribute=attribute, index=1, name="Trait 4", authorization=authorization)
    0

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity

    """
    return aspects.find(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        index=index,
        instance=instance,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def include_trait(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    parameter: AvParameter = NULL_PARAMETER,
    value: AvValue = NULL_VALUE,
) -> None:
    """Include trait of `key`, `name`, and `value` on `attribute` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    name : AvName
        Trait name
    key : AvKey
        Trait key
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Include trait
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.include_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity

    """
    return aspects.include(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        parameter=parameter,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def exclude_trait(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Exclude trait of `key` on `attribute` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    key : AvKey
        Trait key
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Include trait
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.include_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.exclude_trait(entity=entity, attribute=attribute, key="1", authorization=authorization)

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity

    """
    return aspects.exclude(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        key=key,
        parameter=parameter,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def set_trait(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Set trait of `key`, `name`, and `value` on `attribute` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    key : AvKey
        Trait key
    name : AvName
        Trait name
    value : AvValue
        Trait value
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Include trait
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity

    """
    return aspects.set(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        parameter=parameter,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def get_trait(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
) -> AvValue:
    """Get the value of the trait of `key` on `attribute` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    key : AvKey
        Trait key
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Get trait
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> print(traits.get_trait(entity=entity, attribute=attribute, key="1", authorization=authorization).decode_text())
    1

    >>> import avesterra.traits as traits # Get non-existent trait
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> print(traits.get_trait(entity=entity, attribute=attribute, key="1", authorization=authorization).decode_text())
    {"NULL": ""}

    """
    return aspects.get(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        key=key,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def clear_trait(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    parameter: AvParameter = NULL_PARAMETER,
) -> None:
    """Clear the value of the trait of `key` on `attribute` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    key : AvKey
        Trait key
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Include trait
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.clear_trait(entity=entity, attribute=attribute, key="1", authorization=authorization).decode_text()
    >>> print(traits.get_trait(entity=entity, attribute=attribute, key="1", authorization=authorization))
    {"NULL": ""}

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity

    """
    aspects.clear(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        key=key,
        parameter=parameter,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def trait_member(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
) -> bool:
    """Check for the existence of a trait of `key` on `attribute` at `entity`; true if found, false if not

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    key : AvKey
        Trait key
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Existent trait check of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> print(traits.trait_member(entity=entity, attribute=attribute, key="1", authorization=authorization))
    True

    >>> import avesterra.traits as traits # Non-existent trait check of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> print(traits.trait_member(entity=entity, attribute=attribute, key="1", authorization=authorization))
    False

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity

    """
    return aspects.member(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        key=key,
        instance=instance,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def trait_name(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
) -> AvName:
    """Return the name of the trait of `key` or `index` on `attribute` or `instance` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    key : AvKey
        Trait key
    index : AvIndex
        Trait index
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Get name of trait of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> print(traits.trait_name(entity=entity, attribute=attribute, key="1", authorization=authorization))
    I am a trait

    >>> import avesterra.traits as traits # Get name of trait of `index` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> print(traits.trait_name(entity=entity, attribute=attribute, index=1, authorization=authorization))
    I am a trait

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity or if index/key don't map to the same traits in the trait list

    """
    return aspects.name(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        key=key,
        index=index,
        instance=instance,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def trait_key(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
) -> AvKey:
    """Return the key of the trait of `index` on `attribute` or `instance` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    index : AvIndex
        Trait index
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Get key of trait of `index` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> print(traits.trait_key(entity=entity, attribute=attribute, index=1, authorization=authorization))
    1

    >>> import avesterra.traits as traits # Get key of trait of `index` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am trait 3", key="key_3", value=AvValue.encode_text("I am trait 3"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am trait 1", key="key_1", value=AvValue.encode_text("I am trait 1"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am trait 2", key="key_2", value=AvValue.encode_text("I am trait 2"), authorization=authorization)
    >>> print(traits.trait_key(entity=entity, attribute=attribute, index=2, authorization=authorization))
    key_1

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity or index of trait doesn't exist

    """
    return aspects.key(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        index=index,
        instance=instance,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def trait_value(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
) -> AvValue:
    """Return the value of the trait of `key` or `index` on `attribute` or `instance` at `entity`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    key : AvKey
        Trait key
    index : AvIndex
        Trait index
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Get value of trait of `index` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> print(traits.trait_value(entity=entity, attribute=attribute, key="1", authorization=authorization).decode_text())
    I am a trait

    >>> import avesterra.traits as traits # Get value of trait of `index` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am trait 3", key="key_3", value=AvValue.encode_text("I am trait 3"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am trait 1", key="key_1", value=AvValue.encode_text("I am trait 1"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am trait 2", key="key_2", value=AvValue.encode_text("I am trait 2"), authorization=authorization)
    >>> print(traits.trait_value(entity=entity, attribute=attribute, key="key_1", authorization=authorization).decode_text())
    I am trait 1

    >>> import avesterra.traits as traits # Get value of trait of `index` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am trait 3", key="key_3", value=AvValue.encode_text("I am trait 3"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am trait 1", key="key_1", value=AvValue.encode_text("I am trait 1"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am trait 2", key="key_2", value=AvValue.encode_text("I am trait 2"), authorization=authorization)
    >>> print(traits.trait_value(entity=entity, attribute=attribute, index=1, authorization=authorization).decode_text())
    I am trait 3

    Raises
    ______
    ApplicationError
        When `attribute` doesn't exist on target entity, if index/key don't map to the same traits in the trait list, or if index or key don't exist in trait list

    """
    return aspects.value(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        key=key,
        index=index,
        instance=instance,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def trait_index(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
) -> AvIndex:
    """Return the index of the trait of `key` on `attribute` or `instance` at `entity`; returns 0 if not found!

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Trait attribute
    key : AvKey
        Trait key
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Get index of trait of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait", key="key_1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> print(traits.trait_index(entity=entity, attribute=attribute, key="key_1", authorization=authorization))
    1

    >>> import avesterra.traits as traits # Get index of trait of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait 1", key="key_1", value=AvValue.encode_text("I am a trait 1"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait 2", key="key_2", value=AvValue.encode_text("I am a trait 2"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait 3", key="key_3", value=AvValue.encode_text("I am a trait 3"), authorization=authorization)
    >>> print(traits.trait_index(entity=entity, attribute=attribute, key="key_2", authorization=authorization))
    2

    >>> import avesterra.traits as traits # Get index of a non-existent trait of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> print(traits.trait_index(entity=entity, attribute=attribute, key="1", authorization=authorization))
    0

    Raises
    ______
    ApplicationError
        When `attribute` or `instance` doesn't exist on target entity

    """
    return aspects.index(
        aspect=AvAspect.TRAIT,
        entity=entity,
        attribute=attribute,
        key=key,
        instance=instance,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def trait_attribute(
    entity: AvEntity,
    authorization: AvAuthorization,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
) -> AvAttribute:
    """Return the attribute of any trait at `instance`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Trait key
    index : AvIndex
        Trait index
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.traits as traits # Get attribute of trait of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=attribute, name="I am a trait", key="key_1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> print(traits.trait_attribute(entity=entity, attribute=attribute, key="key_1", authorization=authorization).name)
    WIDTH

    >>> import avesterra.traits as traits # Get attribute of trait of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=AvAttribute.ATTRIBUTION, name="I am a trait 1", key="key_1", value=AvValue.encode_text("I am a trait 1"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=AvAttribute.ATTRIBUTE, name="I am a trait 2", key="key_2", value=AvValue.encode_text("I am a trait 2"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=AvAttribute.ENTITY, name="I am a trait 3", key="key_3", value=AvValue.encode_text("I am a trait 3"), authorization=authorization)
    >>> print(traits.trait_attribute(entity=entity, attribute=attribute, key="key_2", authorization=authorization))
    ATTRIBUTE

    Raises
    ______
    ApplicationError
        When `attribute` or `instance` doesn't exist on target entity or if trait doesn't exist at `key`

    """
    return aspects.attribute(
        aspect=AvAspect.TRAIT,
        entity=entity,
        key=key,
        index=index,
        instance=instance,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def sort_traits(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    parameter: AvParameter = NULL_PARAMETER,
    instance: AvInstance = NULL_INSTANCE,
) -> None:
    """Sort traits of `attribute` or `instance` on `entity` by key!

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute in which the trait operation will take place
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Raises
    ______
    ApplicationError
        When `attribute` or `instance` doesn't exist on target entity

    Examples
    ________

    >>> import avesterra.traits as traits # Get attribute of trait of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=AvAttribute.ATTRIBUTE, name="I am a trait", key="3", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=AvAttribute.ATTRIBUTE, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=AvAttribute.ATTRIBUTE, name="I am a trait", key="2", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.sort_traits(entity=entity, attribute=attribute, authorization=authorization)
    >>> assert traits.trait_name(entity=entity, attribute=AvAttribute.ATTRIBUTE, index=1, authorization=authorization) == "Trait 1" and traits.trait_name(entity=entity, attribute=AvAttribute.ATTRIBUTE, index=2, authorization=authorization) == "Trait 2" and traits.trait_name(entity=entity, attribute=AvAttribute.ATTRIBUTE, index=3, authorization=authorization) == "Trait 3"
    True

    """
    aspects.sort(
        aspect=AvAspect.TRAIT,
        attribute=attribute,
        entity=entity,
        parameter=parameter,
        instance=instance,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def purge_traits(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    parameter: AvParameter = NULL_PARAMETER,
    instance: AvInstance = NULL_INSTANCE,
) -> None:
    """Purge traits on `attribute` or `instance` on `entity`; purges all traits from all attributes if NULL_ATTRIBUTE given

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute in which the trait operation will take place
    instance : AvInstance
        Instance(Index of attribute in Trait context), in which the trait operation will take place
    parameter : AvParameter
        Defer writing to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Raises
    ______
    ApplicationError
        When `attribute` or `instance` doesn't exist on target entity

    Examples
    ________

    >>> import avesterra.traits as traits # Get attribute of trait of `key` on `attribute` at `entity`
    >>> attribute: AvAttribute = AvAttribute.WIDTH
    >>> entity: AvEntity # Assume entity is connected to an outlet that supports attribute operations
    >>> authorization: AvAuthorization
    >>> traits.set_trait(entity=entity, attribute=AvAttribute.ATTRIBUTE, name="I am a trait", key="3", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=AvAttribute.ATTRIBUTE, name="I am a trait", key="1", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.set_trait(entity=entity, attribute=AvAttribute.ATTRIBUTE, name="I am a trait", key="2", value=AvValue.encode_text("I am a trait"), authorization=authorization)
    >>> traits.purge_traits(entity=entity, attribute=attribute, authorization=authorization)

    """
    aspects.purge(
        aspect=AvAspect.TRAIT,
        attribute=attribute,
        entity=entity,
        parameter=parameter,
        instance=instance,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def retrieve_traits(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
) -> AvInterchange:
    """Not supported...returns empty interchange"""
    return aspects.retrieve(
        aspect=AvAspect.TRAIT,
        attribute=attribute,
        entity=entity,
        instance=instance,
        offset=NULL_OFFSET,
        authorization=authorization,
    )


def trait_count(
    entity: AvEntity,
    authorization: AvAuthorization,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
) -> AvCount:
    return aspects.count(
        entity=entity,
        aspect=AvAspect.TRAIT,
        attribute=attribute,
        instance=instance,
        authorization=authorization,
    )
