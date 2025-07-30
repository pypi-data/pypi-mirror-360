""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avial import *
from avesterra.predefined import general_outlet

AvGeneral = AvEntity


def create_general(
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    context: AvContext = NULL_CONTEXT,
    category: AvCategory = NULL_CATEGORY,
    klass: AvClass = NULL_CLASS,
    mode: AvMode = AvMode.NULL,
    outlet: AvEntity = NULL_ENTITY,
    server: AvEntity = NULL_ENTITY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvGeneral:
    adapter = general_outlet if outlet == NULL_ENTITY else outlet
    return invoke_entity(
        entity=adapter,
        method=AvMethod.CREATE,
        name=name,
        key=key,
        context=context,
        category=category,
        klass=klass,
        mode=mode,
        ancillary=server,
        authorization=authorization,
    ).decode_entity()


def delete_general(
    general: AvGeneral, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    invoke_entity(entity=general, method=AvMethod.DELETE, authorization=authorization)
