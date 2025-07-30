""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avial import *
from avesterra.taxonomy import (
    AvMethod,
    AvAttribute,
    AvEvent,
    AvAspect,
    AvMode,
    AvCategory,
    AvContext,
    AvClass,
    AvState,
    AxCondition,
)


class Booster:
    count: int
    unbounded: str
    outlet: AvEntity
    name: str
    key: str
    method: AvMethod
    attribute: AvAttribute
    instance: int
    event: AvEvent
    aspect: AvAspect
    mode: AvMode
    auxiliary: AvEntity
    ancillary: AvEntity
    authority: AvAuthorization
    authorization: AvAuthorization

    def __init__(
        self,
        unbounded: str,
        outlet: AvEntity,
        name: str,
        key: str,
        method: AvMethod,
        attribute: AvAttribute,
        instance: int,
        event: AvEvent,
        aspect: AvAspect,
        mode: AvMode,
        auxiliary: AvEntity,
        ancillary: AvEntity,
        authority: AvAuthorization,
        authorization: AvAuthorization,
        count: int = 0,
    ):
        self.count = count
        self.unbounded = unbounded
        self.outlet = outlet
        self.name = name
        self.key = key
        self.method = method
        self.attribute = attribute
        self.instance = instance
        self.event = event
        self.aspect = aspect
        self.mode = mode
        self.auxiliary = auxiliary
        self.ancillary = ancillary
        self.authority = authority
        self.authorization = authorization


def boost_entity(
    entity: AvEntity,
    authorization: AvAuthorization,
    method: AvMethod = NULL_METHOD,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: int = NULL_INSTANCE,
    name: str = NULL_NAME,
    key: str = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    context: AvContext = NULL_CONTEXT,
    category: AvCategory = NULL_CATEGORY,
    klass: AvClass = NULL_CLASS,
    event: AvEvent = NULL_EVENT,
    mode: AvMode = NULL_MODE,
    state: AvState = NULL_STATE,
    condition: AxCondition = NULL_CONDITION,
    auxiliary: AvEntity = NULL_ENTITY,
    ancillary: AvEntity = NULL_ENTITY,
    authority: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    publish_event(
        entity=entity,
        method=method,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        parameter=parameter,
        instance=instance,
        context=context,
        category=category,
        klass=klass,
        event=event,
        mode=mode,
        state=state,
        condition=condition,
        auxiliary=auxiliary,
        ancillary=ancillary,
        authority=authority,
        authorization=authorization,
    )


def boost_import(
    outlet: AvEntity,
    authorization: AvAuthorization,
    value: AvValue = NULL_VALUE,
    registry: AvEntity = NULL_ENTITY,
):
    publish_event(
        entity=outlet,
        event=AvEvent.IMPORT,
        value=value,
        auxiliary=registry,
        authorization=authorization,
    )


def boost_geolocate(outlet: AvEntity, name: AvName = NULL_NAME, key: AvKey = NULL_KEY):
    pass


def boost_load():
    pass


def boost_finalize():
    pass


# PAYLOAD STUFF


def payload_count():
    pass


def payload_value():
    pass


def payload_name():
    pass


def payload_key():
    pass


def payload_alternate():
    pass


def payload_context():
    pass


def payload_class():
    pass


def payload_spaces():
    pass


def decode_payloads():
    pass


# SPACE STUFF?


def space_count():
    pass


def space_entity():
    pass


def space_level():
    pass


def space_coordinate():
    pass
