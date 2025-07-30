""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avial import *


def insert(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=entity,
        method=AvMethod.INSERT,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        offset=offset,
        parameter=parameter,
        authorization=authorization,
    )


def remove(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=entity,
        method=AvMethod.REMOVE,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        index=index,
        instance=instance,
        offset=offset,
        parameter=parameter,
        authorization=authorization,
    )


def replace(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=entity,
        method=AvMethod.REPLACE,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        offset=offset,
        parameter=parameter,
        authorization=authorization,
    )


def find(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    return AvIndex(
        invoke_entity(
            entity=entity,
            method=AvMethod.FIND,
            aspect=aspect,
            attribute=attribute,
            name=name,
            key=key,
            value=value,
            index=index,
            instance=instance,
            offset=offset,
            authorization=authorization,
        ).decode_integer()
    )


def include(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=entity,
        method=AvMethod.INCLUDE,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        offset=offset,
        parameter=parameter,
        authorization=authorization,
    )


def exclude(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=entity,
        method=AvMethod.EXCLUDE,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        offset=offset,
        parameter=parameter,
        authorization=authorization,
    )


def set(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=entity,
        method=AvMethod.SET,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        offset=offset,
        parameter=parameter,
        authorization=authorization,
    )


def get(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return invoke_entity(
        entity=entity,
        method=AvMethod.GET,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        index=index,
        instance=instance,
        offset=offset,
        authorization=authorization,
    )


def clear(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=entity,
        method=AvMethod.CLEAR,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        offset=offset,
        parameter=parameter,
        authorization=authorization,
    )


def count(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvCount:
    return AvCount(
        invoke_entity(
            entity=entity,
            method=AvMethod.COUNT,
            aspect=aspect,
            attribute=attribute,
            name=name,
            key=key,
            index=index,
            instance=instance,
            offset=offset,
            authorization=authorization,
        ).decode_integer()
    )


def member(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    return bool(
        AvValue.decode(
            invoke_entity(
                entity=entity,
                method=AvMethod.MEMBER,
                aspect=aspect,
                attribute=attribute,
                name=name,
                key=key,
                index=index,
                instance=instance,
                offset=offset,
                authorization=authorization,
            )
        )
    )


def name(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvName:
    return AvName(
        AvValue.decode(
            invoke_entity(
                entity=entity,
                method=AvMethod.NAME,
                aspect=aspect,
                attribute=attribute,
                key=key,
                index=index,
                instance=instance,
                offset=offset,
                authorization=authorization,
            )
        )
    )


def key(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvKey:
    return AvKey(
        AvValue.decode(
            invoke_entity(
                entity=entity,
                method=AvMethod.KEY,
                aspect=aspect,
                attribute=attribute,
                value=value,
                name=name,
                index=index,
                instance=instance,
                offset=offset,
                authorization=authorization,
            )
        )
    )


def value(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return invoke_entity(
        entity=entity,
        method=AvMethod.VALUE,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        index=index,
        instance=instance,
        offset=offset,
        authorization=authorization,
    )


def attribute(
    entity: AvEntity,
    aspect: AvAspect,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvAttribute:
    return AvAttribute(
        AvValue.decode(
            invoke_entity(
                entity=entity,
                method=AvMethod.ATTRIBUTE,
                aspect=aspect,
                name=name,
                key=key,
                value=value,
                index=index,
                instance=instance,
                offset=offset,
                authorization=authorization,
            )
        )
    )


def index(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    return AvAttribute(
        AvValue.decode(
            invoke_entity(
                entity=entity,
                method=AvMethod.INDEX,
                aspect=aspect,
                attribute=attribute,
                name=name,
                key=key,
                value=value,
                instance=instance,
                offset=offset,
                authorization=authorization,
            )
        )
    )


def purge(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=entity,
        method=AvMethod.PURGE,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        index=index,
        instance=instance,
        offset=offset,
        parameter=parameter,
        authorization=authorization,
    )


def sort(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=entity,
        method=AvMethod.SORT,
        aspect=aspect,
        attribute=attribute,
        name=name,
        key=key,
        index=index,
        instance=instance,
        offset=offset,
        parameter=parameter,
        authorization=authorization,
    )


def retrieve(
    entity: AvEntity,
    aspect: AvAspect,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInterchange:
    return AvInterchange(
        AvValue.decode(
            invoke_entity(
                entity=entity,
                method=AvMethod.RETRIEVE,
                aspect=aspect,
                attribute=attribute,
                name=name,
                key=key,
                index=index,
                instance=instance,
                offset=offset,
                authorization=authorization,
            )
        )
    )
