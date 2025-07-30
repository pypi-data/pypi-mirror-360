""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import avesterra.aspects as aspects
from avesterra.avial import *


def insert_feature(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.insert(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def remove_feature(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.remove(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        index=index,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def replace_feature(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.replace(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def find_feature(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    return aspects.find(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        name=name,
        value=value,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def include_feature(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.include(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        parameter=parameter,
        authorization=authorization,
    )


def exclude_feature(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.exclude(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        key=key,
        parameter=parameter,
        authorization=authorization,
    )


def set_feature(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.set(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        parameter=parameter,
        authorization=authorization,
    )


def get_feature(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return aspects.get(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        key=key,
        authorization=authorization,
    )


def clear_feature(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.clear(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        key=key,
        parameter=parameter,
        authorization=authorization,
    )


def feature_count(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvCount:
    return aspects.count(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        instance=instance,
        authorization=authorization,
    )


def feature_member(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvBoolean:
    return aspects.member(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        key=key,
        instance=instance,
        authorization=authorization,
    )


def feature_name(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvName:
    return aspects.name(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        key=key,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def feature_key(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvKey:
    return aspects.key(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def feature_value(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return aspects.value(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        key=key,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def feature_index(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    return aspects.index(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        key=key,
        instance=instance,
        authorization=authorization,
    )


def feature_attribute(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvAttribute:
    return aspects.attribute(
        entity=entity,
        aspect=AvAspect.FEATURE,
        key=key,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def sort_features(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.sort(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def purge_features(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    aspects.purge(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        instance=instance,
        parameter=parameter,
        authorization=authorization,
    )


def retrieve_features(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInterchange:
    return aspects.retrieve(
        entity=entity,
        aspect=AvAspect.FEATURE,
        attribute=attribute,
        instance=instance,
        authorization=authorization,
    )
