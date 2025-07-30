""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.properties import *
from avesterra.predefined import folder_outlet
import avesterra.properties as properties

AvFolder = AvEntity


def create_folder(
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    mode: AvMode = AvMode.NULL,
    outlet: AvEntity = NULL_ENTITY,
    server: AvEntity = NULL_ENTITY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvFolder:
    adapter = folder_outlet if outlet == NULL_ENTITY else outlet
    value = invoke_entity(
        entity=adapter,
        method=AvMethod.CREATE,
        name=name,
        key=key,
        context=AvContext.AVESTERRA,
        category=AvCategory.AVESTERRA,
        klass=AvClass.FILE,
        mode=mode,
        ancillary=server,
        authorization=authorization,
    )
    return value.decode_entity()


def delete_folder(
    folder: AvFolder, authorization: AvAuthorization = NULL_AUTHORIZATION
):
    invoke_entity(entity=folder, method=AvMethod.DELETE, authorization=authorization)


def insert_folder(
    folder: AvFolder,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    properties.insert_property(
        entity=folder,
        name=name,
        key=key,
        value=value,
        index=index,
        parameter=parameter,
        authorization=authorization,
    )


def remove_folder(
    folder: AvFolder,
    index: AvIndex = NULL_INDEX,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    properties.remove_property(
        entity=folder, index=index, parameter=parameter, authorization=authorization
    )


def replace_folder(
    folder: AvFolder,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    properties.replace_property(
        entity=folder,
        name=name,
        key=key,
        value=value,
        index=index,
        parameter=parameter,
        authorization=authorization,
    )


def find_item(
    folder: AvFolder,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    return properties.find_property(
        entity=folder, value=value, index=index, authorization=authorization
    )


def lookup_item(
    folder: AvFolder,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return properties.property_value(
        entity=folder, key=key, authorization=authorization
    )


def item_count(folder: AvFolder, authorization: AvAuthorization = NULL_AUTHORIZATION):
    return properties.property_count(entity=folder, authorization=authorization)


def item_member(
    folder: AvFolder, key: AvKey, authorization: AvAuthorization = NULL_AUTHORIZATION
):
    return properties.property_member(
        entity=folder, key=key, authorization=authorization
    )


def item_name(
    folder: AvFolder,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvName:
    return properties.property_name(
        entity=folder, index=index, authorization=authorization
    )


def item_key(
    folder: AvFolder,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvKey:
    return properties.property_key(
        entity=folder, index=index, authorization=authorization
    )


def item_value(
    folder: AvFolder,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return properties.property_value(
        entity=folder, index=index, authorization=authorization
    )


def save_folder(folder: AvFolder, authorization: AvAuthorization = NULL_AUTHORIZATION):
    save_entity(entity=folder, authorization=authorization)


def purge_registry(
    folder: AvFolder, authorization: AvAuthorization = NULL_AUTHORIZATION
):
    properties.purge_properties(entity=folder, authorization=authorization)


def sort_registry(
    folder: AvFolder, authorization: AvAuthorization = NULL_AUTHORIZATION
):
    properties.sort_properties(entity=folder, authorization=authorization)
