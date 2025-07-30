""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import avesterra.aspects as aspects
from avesterra.avial import *


def insert_facet(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.insert(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        value=value,
        index=index,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def remove_facet(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.remove(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        index=index,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def replace_facet(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.replace(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        value=value,
        index=index,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def find_facet(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    return aspects.find(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        value=value,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def include_facet(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.include(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        value=value,
        parameter=parameter,
        authorization=authorization,
    )


def exclude_facet(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.exclude(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        parameter=parameter,
        authorization=authorization,
    )


def set_facet(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.set(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        value=value,
        parameter=parameter,
        authorization=authorization,
    )


def get_facet(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return aspects.get(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        authorization=authorization,
    )


def clear_facet(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.clear(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        parameter=parameter,
        authorization=authorization,
    )


def facet_count(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvCount:
    return aspects.count(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        instance=instance,
        authorization=authorization,
    )


def facet_member(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvBoolean:
    return aspects.member(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        instance=instance,
        authorization=authorization,
    )


def facet_name(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvName:
    return aspects.name(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def facet_key(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvKey:
    return aspects.key(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def facet_value(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return aspects.value(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def facet_index(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    return aspects.index(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        name=name,
        instance=instance,
        authorization=authorization,
    )


def facet_attribute(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvAttribute:
    return aspects.attribute(
        entity=entity,
        aspect=AvAspect.FACET,
        name=name,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def sort_facets(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.sort(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def purge_facets(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.purge(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def retrieve_facets(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInterchange:
    return aspects.retrieve(
        entity=entity,
        aspect=AvAspect.FACET,
        attribute=attribute,
        instance=instance,
        authorization=authorization,
    )
