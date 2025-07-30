"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import avesterra as av
from avesterra.avial import *
from avesterra.avesterra import AvEntity, NULL_ENTITY, AvAuthorization
from avesterra.predefined import space_outlet
from avesterra.taxonomy import (
    AvMode,
    AvContext,
    AvCategory,
    AvClass,
    AxState,
    AxCondition,
    AvMethod,
)

AvSpace = AvEntity

AvSpaceCoordinate = tuple[float, float, float]
AvSpaceLevel = int
AvSpaceVolume = tuple[float, float, float, float, float, float]

NULL_LEVEL = 0
NULL_COORDINATE = 0, 0, 0
NULL_VOLUME = ((0, 0, 0), (0, 0, 0))


def create_space(
    name: str = "",
    key: str = "",
    scale: AvSpaceCoordinate = NULL_COORDINATE,
    mode: AvMode = AvMode(0),
    outlet: AvEntity = NULL_ENTITY,
    server: AvEntity = NULL_ENTITY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvSpace:
    adapter_euid: AvEntity = space_outlet if outlet == NULL_ENTITY else outlet
    return AvValue.decode_entity(
        invoke_entity(
            entity=adapter_euid,
            method=AvMethod.CREATE,
            name=name,
            key=key,
            context=AvContext.AVESTERRA,
            category=AvCategory.AVESTERRA,
            klass=AvClass.SPACE,
            value=AvValue.encode_interchange(json.dumps(scale)),
            mode=mode,
            ancillary=server,
            authorization=authorization,
        )
    )


def delete_space(space: AvSpace, authorization: AvAuthorization):
    delete_entity(entity=space, authorization=authorization)


def include_entity(
    space: AvSpace,
    entity: AvEntity,
    level: AvSpaceLevel,
    coordinate: AvSpaceCoordinate,
    authorization: AvAuthorization,
    name: str = "",
    key: str = "",
    state: AxState = AxState(0),
    condition: AxCondition = AxCondition(0),
    context: AvContext = AvContext(0),
    category: AvCategory = AvCategory(0),
    klass: AvClass = AvClass(0),
):
    invoke_entity(
        entity=space,
        method=AvMethod.INCLUDE,
        context=context,
        category=category,
        klass=klass,
        name=name,
        key=key,
        value=AvValue.encode_interchange(json.dumps(coordinate)),
        state=state,
        condition=condition,
        parameter=level,
        auxiliary=entity,
        authorization=authorization,
    )


# Broken
def exclude_entity(
    space: AvSpace,
    entity: AvEntity,
    level: AvSpaceLevel,
    coordinate: AvSpaceCoordinate,
    authorization: AvAuthorization,
):
    invoke_entity(
        entity=space,
        method=AvMethod.EXCLUDE,
        parameter=level,
        value=AvValue.encode_interchange(json.dumps(coordinate)),
        auxiliary=entity,
        authorization=authorization,
    )


def retrieve_in_space(
    space: AvSpace,
    level: AvSpaceLevel,
    volume: AvSpaceVolume,
    authorization: AvAuthorization,
) -> dict[
    str,
    tuple[
        AvName,
        AvKey,
        AvEntity,
        AxState,
        AxCondition,
        AvContext,
        AvCategory,
        AvClass,
        AvSpaceCoordinate,
    ],
]:
    results = {}

    value = invoke_entity(
        entity=space,
        method=AvMethod.RETRIEVE,
        value=AvValue.encode_interchange(json.dumps(volume)),
        parameter=level,
        authorization=authorization,
    )

    json_obj = json.loads(value.decode_interchange())
    # Dive into properties
    properties = json_obj["Properties"] if "Properties" in json_obj.keys() else []

    for record in properties:
        name = record[0]
        key = record[1]
        entity = AvValue.from_json(record[2]).decode_entity()

        annotations = list(record[3].values())

        state = AxState[AvValue.from_json(annotations[0]).decode_string().split("_")[0]]
        condition = AxCondition(
            int(AvValue.from_json(annotations[1]).decode_string().strip())
        )
        context = AvContext[
            AvValue.from_json(annotations[2]).decode_string().split("_")[0]
        ]
        category = AvCategory[
            AvValue.from_json(annotations[3]).decode_string().split("_")[0]
        ]
        klass = AvClass[AvValue.from_json(annotations[4]).decode_string().split("_")[0]]
        coordinate_list = json.loads(
            AvValue.from_json(annotations[5]).decode_interchange()
        )
        results[str(entity)] = (
            name,
            key,
            entity,
            state,
            condition,
            context,
            category,
            klass,
            coordinate_list,
        )

    return results
