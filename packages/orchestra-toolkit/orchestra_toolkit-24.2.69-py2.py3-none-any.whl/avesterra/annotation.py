""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""


import avesterra.aspects as aspects
from avesterra.avial import *


def insert_annotation(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Insert an annotation into a property table

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the to be inserted annotation
    key : AvKey
        Key in which the annotation will be attatched to
    value : AvValue
        Value of the to be inserted annotation
    index : AvIndex
        Index in the annotation list that the annotation will be inserted into
    instance : AvInstance
        Instance(Property Table Index) in which the annotation will be inserted
    parameter : AvParameter
        Defer saving changes to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`.

    Examples
    ________

    >>> import avesterra.annotation as annotation # Insert annotation at key
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.insert_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I am going to be inserted in the property table on `key`!"), authorization=authorization)


    >>> import avesterra.annotation as annotation # Insert 3 annotations at key; the last insertion goes between the first and second inserted annotations
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTION, index=1, value=AvValue.encode_text("I am first!"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.TERRITORY, index=2, value=AvValue.encode_text("I am second!"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTE, index=2, value=AvValue.encode_text("I am going to become second!"), authorization=authorization)


    >>> import avesterra.annotation as annotation # Insert 3 annotations; one on each property!
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> annotation.insert_annotation(entity=entity, instance=1, attribute=AvAttribute.ATTRIBUTION, value=AvValue.encode_text("I am first!"), authorization=authorization) # Insert at instance(Property Index) 1
    >>> annotation.insert_annotation(entity=entity, instance=2, attribute=AvAttribute.TERRITORY, value=AvValue.encode_text("I am second!"), authorization=authorization) # Insert at instance(Property Index) 2
    >>> annotation.insert_annotation(entity=entity, instance=3, attribute=AvAttribute.ATTRIBUTE, value=AvValue.encode_text("I am going to become second!"), authorization=authorization) # Insert at instance(Property Index) 3


    Raises
    ______
    ApplicationError
        When property of key/instance doesn't exist in property table

    """
    aspects.insert(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        value=value,
        index=index,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def remove_annotation(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Remove an annotation at `index` of from annotation list at `key`/`instance`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of the property table of which the annotation will be removed
    index : AvIndex
        Index in the annotation list to remove
    instance : AvInstance
        Instance(Property Table Index) in which the annotation will be removed
    parameter : AvParameter
        Defer saving changes to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`.

    Examples
    ________

    >>> import avesterra.annotation as annotation # Remove last annotation in annotation list at property `example_key`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> annotation.insert_annotation(entity=entity, attribute=AvAttribute.TO, key="example_key", value=AvValue.encode_text("I am safe"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, attribute=AvAttribute.FRAME, key="example_key", value=AvValue.encode_text("I am not safe"), authorization=authorization)
    >>> annotation.remove_annotation(entity=entity, key="example_key", authorization=authorization)

    >>> import avesterra.annotation as annotation # Remove first annotation in annotation list in property table at key `example_key`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> annotation.insert_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTE, key="example_key", value=AvValue.encode_text("I am safe"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key="example_key", value=AvValue.encode_text("I am not safe"), authorization=authorization)
    >>> annotation.remove_annotation(entity=entity, index=1, authorization=authorization)

    >>> import avesterra.annotation as annotation # Remove annotation at index 2 in annotation list in property table at key `example_key`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> annotation.insert_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key="example_key", value=AvValue.encode_text("I am safe"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTE, key="example_key", value=AvValue.encode_text("I am not safe"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, attribute=AvAttribute.TO, key="example_key", value=AvValue.encode_text("I am safe as well"), authorization=authorization)
    >>> annotation.remove_annotation(entity=entity, index=2, authorization=authorization)


    Raises
    ______
    ApplicationError
        When property of key/instance doesn't exist in property table

    """
    aspects.remove(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        key=key,
        index=index,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def replace_annotation(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Replace an annotation in a property table

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the annotation that will be replaced
    key : AvKey
        Key of the property that will have its annotation replaced
    value : AvValue
        Value of the new annotation
    index : AvIndex
        Index in the annotation list to replace
    instance : AvInstance
        Instance(Property Table Index) in which the annotation will be replaced
    parameter : AvParameter
        Defer saving changes to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`.

    Examples
    ________

    >>> import avesterra.annotation as annotation # Replace annotation in annotation list in property table at key `example_key`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.insert_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I am going to be replaced in the future...sadly"), authorization=authorization)
    >>> annotation.replace_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I am the epic replacement!"), authorization=authorization)

    >>> import avesterra.annotation as annotation # Replace 2nd annotation in annotation list in property table at key `example_key`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.insert_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTE, key=key, value=AvValue.encode_text("I am here"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I am going to be replaced in the future...sadly"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, attribute=AvAttribute.TERRITORY, key=key, value=AvValue.encode_text("I am am here...physically"), authorization=authorization)
    >>> annotation.replace_annotation(entity=entity, attribute=AvAttribute.HEIGHT, key=key, index=2, value=AvValue.encode_text("I am the epic replacement!"), authorization=authorization)


    Raises
    ______
    ApplicationError
        When property of key/instance doesn't exist in property table

    """
    aspects.replace(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        value=value,
        index=index,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def find_annotation(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    """Find the index of the annotation which has `value` at the property of `key` or `instance` in the property table

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key where the annotation search will take place
    value : AvValue
        Value to lookup
    index : AvIndex
        Index in the annotation list to begin the search; front-to-back
    instance : AvInstance
        Instance(Property Table Index) in which the annotation search will take place
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Lookup existent annotation
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.TERRITORY, value=AvValue.encode_text("I am not gonna get looked up"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTION, value=AvValue.encode_text("I am gonna get looked up"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTE, value=AvValue.encode_text("I am also not gonna get looked up"), authorization=authorization)
    >>> annotation.find_annotation(entity=entity, key=key, value=AvValue.encode_text("I am gonna get looked up"), authorization=authorization)
    2

    >>> import avesterra.annotation as annotation # Lookup non-existent annotation
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.TERRITORY, value=AvValue.encode_text("I am not gonna get looked up"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTION, value=AvValue.encode_text("I am gonna get looked up"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTE, value=AvValue.encode_text("I am also not gonna get looked up"), authorization=authorization)
    >>> annotation.find_annotation(entity=entity, key=key, value=AvValue.encode_text("I don't know where I am"), authorization=authorization)
    0

    >>> import avesterra.annotation as annotation # Lookup existent annotation after `index`, which results in not found
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.TERRITORY, value=AvValue.encode_text("I exist"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTION, value=AvValue.encode_text("I am gonna get looked up"), authorization=authorization)
    >>> annotation.insert_annotation(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTE, value=AvValue.encode_text("I am also not gonna get looked up"), authorization=authorization)
    >>> annotation.find_annotation(entity=entity, key=key, index=2, value=AvValue.encode_text("I exist"), authorization=authorization)
    0

    Raises
    ______
    ApplicationError
        When property of key/instance doesn't exist in property table

    """
    return aspects.find(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        key=key,
        value=value,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def include_annotation(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Include an annotation at in annotation list at property of `key` or `instance`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the annotation to be included
    key : AvKey
        Key of the property that the annotation will be included
    value : AvValue
        Value to be included as an annotation
    instance : AvInstance
        Instance(Property Table Index) in which the annotation will be included
    parameter : AvParameter
        Defer saving changes to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Include annotation in property table on property at `key`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.include_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)

    >>> import avesterra.annotation as annotation # Include annotation in property table on property at `instance`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> annotation.include_annotation(entity=entity, attribute=attribute, instance=1, value=AvValue.encode_text("I have been included"), authorization=authorization)

    >>> import avesterra.annotation as annotation # Include "over" previously set annotation
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.include_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I am gonna get included, but will also be replaced..."), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I am gonna be included as a replacement!"), authorization=authorization)

    Raises
    ______
    ApplicationError
        When property of key/instance doesn't exist in property table

    """
    aspects.include(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        value=value,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def exclude_annotation(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Exclude an annotation from the target property table at key

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the annotation to be excluded
    key : AvKey
        Key of the property that the annotation will be excluded
    instance : AvInstance
        Instance(Property Table Index) in which the annotation will be excluded
    parameter : AvParameter
        Defer saving changes to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Include annotation in property table on record at key
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.include_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.exclude_annotation(entity=entity, attribute=attribute, key=key, authorization=authorization)

    Raises
    ______
    ApplicationError
        When property of key/instance doesn't exist in property table

    """
    aspects.exclude(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def set_annotation(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Set the value of an annotation in annotation list at property of `key`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the annotation to be set
    key : AvKey
        Key of the property that the annotation will be set in
    value : AvValue
        Value that will be used to set the annotation
    parameter : AvParameter
        Defer saving changes to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Set annotation in property table on property of `key`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.include_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.set_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I have been set!"), authorization=authorization)

    Raises
    ______
    ApplicationError
        When property of key/instance doesn't exist in property table

    """
    aspects.set(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        value=value,
        parameter=parameter,
        authorization=authorization,
    )


def get_annotation(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Get the value of an annotation at property of `key`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the annotation to be returned
    key : AvKey
        Key of the property that the annotation value will be returned from
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Get an existent annotation
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.include_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> print(annotation.get_annotation(entity=entity, attribute=attribute, key=key, authorization=authorization).decode_text())
    I have been included

    >>> import avesterra.annotation as annotation # Attempt to get a non-existent annotation
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.include_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> print(annotation.get_annotation(entity=entity, attribute=AvAttribute.HEIGHT, key=key, authorization=authorization))
    {"NULL": ""}

    >>> import avesterra.annotation as annotation # Attempt to get an annotation from a non-existent key
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> print(annotation.get_annotation(entity=entity, attribute=AvAttribute.HEIGHT, key="I really don't exist", authorization=authorization))
    {"NULL": ""}

    """
    return aspects.get(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        authorization=authorization,
    )


def clear_annotation(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Clears the value of an annotation on the property at `key`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the annotation which will have its value cleared
    key : AvKey
        Key of the property that the annotation value will be returned from
    parameter : AvParameter
        Defer saving changes to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Clear the value of an annotation
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> attribute: AvAttribute = AvAttribute.EXAMPLE
    >>> key: AvKey = "example_key"
    >>> annotation.include_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.clear_annotation(entity=entity, attribute=attribute, key=key, authorization=authorization)
    >>> print(annotation.get_annotation(entity=entity, attribute=attribute, key=key, authorization=authorization))
    {"NULL": ""}

    """
    aspects.clear(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        parameter=parameter,
        authorization=authorization,
    )


def annotation_count(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvCount:
    """Count the number of annotations on the property at `key` or `instance`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of the property that the annotation count will be returned from
    instance : AvInstance
        Instance(Property Table Index) in which the annotation count will be returned from
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Get count of included annotations on property at `key`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.WIDTH, key=key, value=AvValue.encode_text("I have been included too"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.HEIGHT, key=key, value=AvValue.encode_text("I have been included as well"), authorization=authorization)
    >>> print(annotation.annotation_count(entity=entity, key=key, authorization=authorization))
    3

    >>> import avesterra.annotation as annotation # Get count of annotations, when none have been included
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> print(annotation.annotation_count(entity=entity, key=key, authorization=authorization))
    0

    Raises
    ______
    ApplicationError
        When property of key/instance doesn't exist in property table

    """
    return aspects.count(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        key=key,
        instance=instance,
        authorization=authorization,
    )


def annotation_member(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvBoolean:
    """Check if an annotation of `attribute` has been set on property at `key` or `instance`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        The attribute of the annotation that will be checked
    key : AvKey
        Key of the property that the annotation member check will be executed on
    instance : AvInstance
        Instance(Property Table Index) in which the annotation member check will be executed on
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Check if an annotation of `attribute` has been set at the target property table at key
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> annotation.include_annotation(entity=entity, attribute=attribute, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> print(annotation.annotation_member(entity=entity, key=key, attribute=attribute, authorization=authorization))
    True

    >>> import avesterra.annotation as annotation # Check if an annotation of `attribute` has been set at the target property table at key
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> print(annotation.annotation_member(entity=entity, key=key, attribute=AvAttribute.HEAT, authorization=authorization))
    False

    Raises
    ______
    ApplicationError
        When property of key/instance doesn't exist in property table

    """
    return aspects.member(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        instance=instance,
        authorization=authorization,
    )


def annotation_name(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvName:
    """Returns the name of the parent property of annotation of `attribute` or `index`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the target annotation
    key : AvKey
        Key of the property that the property name will be returned
    index : AvIndex
        Index of the annotation in the annotation list whose parent property name wll be returned
    instance : AvInstance
        Instance(Property Table Index) in which the property name will be returned
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Get property name via key
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization
    >>> print(annotation.annotation_name(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTION, authorization=authorization))
    example_name

    >>> import avesterra.annotation as annotation # Get property name via instance
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization
    >>> print(annotation.annotation_name(entity=entity, instance=1, attribute=AvAttribute.ATTRIBUTION, authorization=authorization))
    example_name


    Raises
    ______
    ApplicationError
        When property of key/instance doesn't exist in property table

    """
    return aspects.name(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def annotation_key(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvKey:
    """Returns the key of property at instance

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the target annotation
    index : AvIndex
        Index of the annotation in the annotation list whose parent property key wll be returned
    instance : AvInstance
        Instance(Property Table Index) in which the property key will be returned
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Get property key via instance
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> print(annotation.annotation_key(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTION, authorization=authorization))
    example_name

    Raises
    ______
    ApplicationError
        When property of instance doesn't exist in property table

    """
    return aspects.key(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def annotation_value(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Returns value of annotation `attribute` or `index` at property of `key` or `instance`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the target annotation
    key : AvKey
        Key of property in which the annotation value will be returned
    index : AvIndex
        Index of the annotation in the annotation list whose value will be returned
    instance : AvInstance
        Instance(Property Table Index) in which the annotation value will be returned
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Get annotation value via key
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> print(annotation.annotation_value(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTION, authorization=authorization))
    {"TEXT": "I have been included"}

    >>> import avesterra.annotation as annotation # Get annotation value via instance
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> print(annotation.annotation_value(entity=entity, instance=1, attribute=AvAttribute.ATTRIBUTION, authorization=authorization))
    {"TEXT": "I have been included"}

    Raises
    ______
    ApplicationError
        When property doesn't exist or annotation doesn't exist

    """
    return aspects.value(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def annotation_index(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    """Returns the index of annotation `attribute` in annotation list at property of `key` or `instance`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    attribute : AvAttribute
        Attribute of the target annotation
    key : AvKey
        Key of property in which the annotation index will be returned
    instance : AvInstance
        Instance(Property Table Index) in which the annotation index will be returned
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Get annotation index
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTE, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.HEIGHT, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> print(annotation.annotation_index(entity=entity, key=key, attribute=AvAttribute.ATTRIBUTE, authorization=authorization))
    2

    >>> import avesterra.annotation as annotation # Get non-existent annotation index
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTE, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.HEIGHT, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> print(annotation.annotation_index(entity=entity, key=key, attribute=AvAttribute.WIDTH, authorization=authorization))
    0

    Raises
    ______
    ApplicationError
        When property doesn't exist or annotation doesn't exist

    """
    return aspects.index(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        attribute=attribute,
        key=key,
        instance=instance,
        authorization=authorization,
    )


def annotation_attribute(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvAttribute:
    """Returns attribute of annotation at `index` in annotation list of property of `key` or `instance`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of property in which the annotation index will be returned
    index : AvIndex
        Index of the annotation in the annotation list whose attribute will be returned
    instance : AvInstance
        Instance(Property Table Index) in which the annotation index will be returned
    authorization : AvAuthorization
        An authorization that is able to read from the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Get annotation attribute at index 2 of annotation list of property of `key`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTE, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.HEIGHT, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> print(annotation.annotation_attribute(entity=entity, key=key, index=2, authorization=authorization).name)
    ATTRIBUTE


    Raises
    ______
    ApplicationError
        When property doesn't exist or annotation doesn't exist

    """
    return aspects.attribute(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        key=key,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def sort_annotation(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Sorts annotations by value in annotation list at property of `key`

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of property whose annotation list will be sorted
    instance : AvInstance
        Instance(Property Table Index) of property whose annotation list will be sorted
    parameter : AvParameter
        Defer saving changes to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write from the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Sort annotation list of property of `key`
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTE, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.HEIGHT, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.sort_annotation(entity=entity, key=key, authorization=authorization)

    """
    aspects.sort(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        key=key,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def purge_annotation(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Purges all annotations at key; if key is NULL_KEY, then all annotations will be purged on property table

    Parameters
    __________
    entity : AvEntity
        Target entity euid
    key : AvKey
        Key of property in which the annotations will be purged
    instance : AvInstance
        Instance(Property Table Index) in which the annotations will be purged
    parameter : AvParameter
        Defer saving changes to disk if set to anything but NULL_PARAMETER
    authorization : AvAuthorization
        An authorization that is able to write to the `entity`

    Examples
    ________

    >>> import avesterra.annotation as annotation # Get annotation index
    >>> entity: AvEntity
    >>> authorization: AvAuthorization
    >>> key: AvKey = "example_key"
    >>> name: AvName = "example_name"
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTION, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.ATTRIBUTE, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.include_annotation(entity=entity, attribute=AvAttribute.HEIGHT, key=key, value=AvValue.encode_text("I have been included"), authorization=authorization)
    >>> annotation.purge_annotation(entity=entity, key=key, authorization=authorization)
    >>> print(annotation.annotation_count(entity=entity, key=key, authorization=authorization))
    0

    Raises
    ______
    ApplicationError
        When property doesn't exist

    """
    aspects.purge(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        key=key,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def retrieve_annotation(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInterchange:
    """Not supported...returns empty interchange"""

    return aspects.retrieve(
        entity=entity,
        aspect=AvAspect.ANNOTATION,
        key=key,
        instance=instance,
        authorization=authorization,
    )
