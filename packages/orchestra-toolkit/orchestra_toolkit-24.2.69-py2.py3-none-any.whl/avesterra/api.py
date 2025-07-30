""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import ipaddress
from ipaddress import IPv4Address, IPv6Address
import avesterra.hgtp as hgtp
from avesterra.avesterra import *
from avesterra.parameters import FALSE_PARAMETER, TRUE_PARAMETER
from avesterra.taxonomy import *
from typing import Tuple, Callable

# AvesTerra null constants:
NULL_ENTITY = AvEntity(0, 0, 0)
NULL_AUTHORIZATION = AvAuthorization(int=0)
NULL_BYTES = b""
NULL_INSTANCE = 0
NULL_OFFSET = 0
NULL_NAME = b""
NULL_KEY = b""
NULL_PARAMETER = 0
NULL_RESULTANT = 0
NULL_PRECEDENCE = 0
NULL_INDEX = 0
NULL_COUNT = 0
NULL_MODE = 0
NULL_TIME = 0
NULL_TIMEOUT = 0
NULL_RESULT = ""
NULL_DATA = b""
NULL_ASPECT = 0
NULL_CONTEXT = 0
NULL_CATEGORY = 0
NULL_CLASS = 0
NULL_ATTRIBUTE = 0
NULL_METHOD = 0
NULL_EVENT = 0
NULL_STATE = 0
NULL_CONDITION = 0
NULL_TAG = 0

socket_max = 16


######################
# Session Operations #
######################


def initialize(
    server: str = "",
    directory: str = "",
    socket_count: int = 16,
    max_timeout: int = 360,
) -> None:
    global socket_max
    socket_max = socket_count
    hgtp.initialize(
        server=server,
        directory=directory,
        socket_count=socket_count,
        max_timeout=max_timeout,
    )


def finalize() -> None:
    hgtp.finalize()


def max_async_connections() -> int:
    return socket_max


#####################
# Entity operations #
#####################


# Avial 4.7: Create entity now routable, by supplying the `server` argument
def create(
    outlet: AvEntity = NULL_ENTITY,
    server: AvEntity = NULL_ENTITY,
    name: bytes = NULL_NAME,
    key: bytes = NULL_KEY,
    context: int = NULL_CONTEXT,
    category: int = NULL_CATEGORY,
    klass: int = NULL_CLASS,
    method: int = NULL_METHOD,
    attribute: int = NULL_ATTRIBUTE,
    event: int = NULL_EVENT,
    precedence: int = NULL_PRECEDENCE,
    timeout: int = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvEntity:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.CREATE
    frame.entity = server
    frame.outlet = outlet
    frame.name_count = len(name)
    frame.name = name
    frame.key_count = len(key)
    frame.key = key
    frame.context_code = context
    frame.category_code = category
    frame.class_code = klass
    frame.method_code = method
    frame.attribute_code = attribute
    frame.event_code = event
    frame.precedence = precedence
    frame.timeout = timeout
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.entity


# Avial 4.7: Delete entity now has a timeout
def delete(
    entity: AvEntity,
    timeout: int,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvEntity:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.DELETE
    frame.entity = entity
    frame.timeout = timeout
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.entity


def invoke(
    entity: AvEntity = NULL_ENTITY,
    auxiliary: AvEntity = NULL_ENTITY,
    ancillary: AvEntity = NULL_ENTITY,
    method: int = NULL_METHOD,
    attribute: int = NULL_ATTRIBUTE,
    instance: int = NULL_INSTANCE,
    offset: int = NULL_OFFSET,
    name: bytes = NULL_NAME,
    key: bytes = NULL_KEY,
    bytes: bytes = NULL_BYTES,
    parameter: int = NULL_PARAMETER,
    resultant: int = NULL_RESULTANT,
    index: int = NULL_INDEX,
    count: int = NULL_COUNT,
    aspect: int = NULL_ASPECT,
    context: int = NULL_CONTEXT,
    category: int = NULL_CATEGORY,
    klass: int = NULL_CLASS,
    event: int = NULL_EVENT,
    mode: int = NULL_MODE,
    state: int = NULL_STATE,
    condition: int = NULL_CONDITION,
    precedence: int = NULL_PRECEDENCE,
    tag: int = NULL_TAG,
    time: int = NULL_TIME,
    timeout: int = NULL_TIMEOUT,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> Tuple[int, bytes]:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.INVOKE
    frame.entity = entity
    frame.auxiliary = auxiliary
    frame.ancillary = ancillary
    frame.method_code = method
    frame.attribute_code = attribute
    frame.instance = instance
    frame.offset = offset
    frame.name_count = len(name)
    frame.name = name
    frame.key_count = len(key)
    frame.key = key
    frame.load_bytes(bytes)
    frame.parameter = parameter
    frame.resultant = resultant
    frame.index = index
    frame.count = count
    frame.aspect_code = aspect
    frame.context_code = context
    frame.category_code = category
    frame.class_code = klass
    frame.event_code = event
    frame.mode_code = mode
    frame.state_code = state
    frame.condition_code = condition
    frame.precedence = precedence
    frame.tag_code = tag
    frame.time = time
    frame.timeout = timeout
    frame.authority = authority
    frame.authorization = authorization

    response = hgtp.post(frame=frame)
    return response.tag_code, response._bytes


def inquire(
    entity: AvEntity = NULL_ENTITY,
    auxiliary: AvEntity = NULL_ENTITY,
    ancillary: AvEntity = NULL_ENTITY,
    attribute: int = NULL_ATTRIBUTE,
    instance: int = NULL_INSTANCE,
    offset: int = NULL_OFFSET,
    name: bytes = NULL_NAME,
    key: bytes = NULL_KEY,
    bytes: bytes = NULL_BYTES,
    parameter: int = NULL_PARAMETER,
    resultant: int = NULL_RESULTANT,
    index: int = NULL_INDEX,
    count: int = NULL_COUNT,
    aspect: int = NULL_ASPECT,
    context: int = NULL_CONTEXT,
    category: int = NULL_CATEGORY,
    klass: int = NULL_CLASS,
    event: int = NULL_EVENT,
    mode: int = NULL_MODE,
    state: int = NULL_STATE,
    condition: int = NULL_CONDITION,
    precedence: int = NULL_PRECEDENCE,
    tag: int = NULL_TAG,
    time: int = NULL_TIME,
    timeout: int = NULL_TIMEOUT,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> Tuple[int, bytes]:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.INQUIRE
    frame.entity = entity
    frame.auxiliary = auxiliary
    frame.ancillary = ancillary
    frame.attribute_code = attribute
    frame.instance = instance
    frame.offset = offset
    frame.name_count = len(name)
    frame.name = name
    frame.key_count = len(key)
    frame.key = key
    frame.load_bytes(bytes=bytes)
    frame.condition_code = condition
    frame.parameter = parameter
    frame.resultant = resultant
    frame.index = index
    frame.count = count
    frame.aspect_code = aspect
    frame.context_code = context
    frame.category_code = category
    frame.class_code = klass
    frame.event_code = event
    frame.mode_code = mode
    frame.state_code = state
    frame.precedence = precedence
    frame.tag_code = tag
    frame.time = time
    frame.timeout = timeout
    frame.authority = authority
    frame.authorization = authorization

    response = hgtp.post(frame=frame)
    return response.tag_code, response._bytes


def reference(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REFERENCE
    frame.entity = entity
    frame.authorization = authorization
    hgtp.post(frame=frame)


def dereference(entity: AvEntity, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.DEREFERENCE
    frame.entity = entity
    frame.authorization = authorization
    hgtp.post(frame=frame)


def redirect(
    server: AvEntity,
    from_entity: AvEntity = NULL_ENTITY,
    to_entity: AvEntity = NULL_ENTITY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REDIRECT
    frame.entity = server
    frame.auxiliary = from_entity
    frame.ancillary = to_entity
    frame.authorization = authorization
    hgtp.post(frame=frame)


def change(
    entity: AvEntity,
    name: bytes = NULL_NAME,
    key: bytes = NULL_KEY,
    context: int = NULL_CONTEXT,
    category: int = NULL_CATEGORY,
    klass: int = NULL_CLASS,
    state: int = NULL_STATE,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.CHANGE
    frame.entity = entity
    frame.name_count = len(name)
    frame.name = name
    frame.key_count = len(key)
    frame.key = key
    frame.context_code = context
    frame.category_code = category
    frame.class_code = klass
    frame.state_code = state
    frame.authority = authority
    frame.authorization = authorization
    hgtp.post(frame=frame)


def fetch(
    entity: AvEntity,
    name: bytes = NULL_NAME,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> Tuple[int, bytes]:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.FETCH
    frame.entity = entity
    frame.name_count = len(name)
    frame.name = name
    frame.authorization = authorization
    result = hgtp.post(frame=frame)
    return result.tag_code, result._bytes


#########################
# Attachment Operations #
#########################


def attach(
    entity: AvEntity,
    outlet: AvEntity,
    attribute: int = NULL_ATTRIBUTE,
    precedence: int = NULL_PRECEDENCE,
    timeout: int = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.ATTACH
    frame.entity = entity
    frame.outlet = outlet
    frame.attribute_code = attribute
    frame.precedence = precedence
    frame.authorization = authorization
    frame.timeout = timeout
    hgtp.post(frame=frame)


def detach(
    entity: AvEntity,
    attribute: int = NULL_ATTRIBUTE,
    precedence: int = NULL_PRECEDENCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.DETACH
    frame.entity = entity
    frame.attribute_code = attribute
    frame.precedence = precedence
    frame.authorization = authorization
    hgtp.post(frame=frame)


def attached(
    entity: AvEntity,
    attribute: int = NULL_ATTRIBUTE,
    precedence: int = NULL_PRECEDENCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.ATTACHED
    frame.entity = entity
    frame.attribute_code = attribute
    frame.precedence = precedence
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def attachments(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.ATTACHMENTS
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def attachment(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> Tuple[AvEntity, int, int, int]:
    """Return attachment details (outlet, attribute, precedence, and expiration)?"""
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.ATTACHMENT
    frame.entity = entity
    frame.index = index
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return (
        response.outlet,
        response.attribute_code,
        response.precedence,
        response.time,
    )


#########################
# Connection Operations #
#########################


def connect(
    entity: AvEntity,
    outlet: AvEntity,
    method: int = NULL_METHOD,
    precedence: int = NULL_PRECEDENCE,
    timeout: int = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.CONNECT
    frame.entity = entity
    frame.outlet = outlet
    frame.method_code = method
    frame.timeout = timeout
    frame.precedence = precedence
    frame.authorization = authorization
    hgtp.post(frame=frame)


def disconnect(
    entity: AvEntity,
    method: int = NULL_METHOD,
    precedence: int = NULL_PRECEDENCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.DISCONNECT
    frame.entity = entity
    frame.method_code = method
    frame.precedence = precedence
    frame.authorization = authorization
    hgtp.post(frame=frame)


def connected(
    entity: AvEntity,
    method: int = NULL_METHOD,
    precedence: int = NULL_PRECEDENCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.CONNECTED
    frame.entity = entity
    frame.method_code = method
    frame.precedence = precedence
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def connections(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.CONNECTIONS
    frame.authorization = authorization
    frame.entity = entity
    response = hgtp.post(frame=frame)
    return response.count


def connection(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> Tuple[AvEntity, int, int, int]:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.CONNECTION
    frame.entity = entity
    frame.index = index
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return (
        response.outlet,
        response.method_code,
        response.precedence,
        response.time,
    )


######################
# Element Operations #
######################


def insert(
    entity: AvEntity,
    tag: int = NULL_TAG,
    bytes: bytes = NULL_BYTES,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Insert a value into an entity"""
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.INSERT
    frame.entity = entity
    frame.index = index
    frame.tag_code = tag
    frame.load_bytes(bytes=bytes)
    frame.authorization = authorization
    hgtp.post(frame=frame)


def remove(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Remove a value from an entity"""
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REMOVE
    frame.entity = entity
    frame.index = index
    frame.authorization = authorization
    hgtp.post(frame=frame)


def replace(
    entity: AvEntity,
    tag: int = NULL_TAG,
    bytes: bytes = NULL_BYTES,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Replace a value in an entity"""
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPLACE
    frame.entity = entity
    frame.index = index
    frame.tag_code = tag
    frame.load_bytes(bytes=bytes)
    frame.authorization = authorization
    hgtp.post(frame=frame)


def erase(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Erase values in an entity"""
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.ERASE
    frame.entity = entity
    frame.authorization = authorization
    hgtp.post(frame=frame)


def find(
    entity: AvEntity,
    tag: int = NULL_TAG,
    bytes: bytes = NULL_BYTES,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> int:
    """Replace a value in an entity"""
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.FIND
    frame.entity = entity
    frame.index = index
    frame.tag_code = tag
    frame.load_bytes(bytes=bytes)
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.index


def element(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> Tuple[int, bytes]:
    """Return element of an entity?"""
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.ELEMENT
    frame.entity = entity
    frame.index = index
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.tag_code, response._bytes


def length(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Number of elements in entity?"""
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.LENGTH
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


####################
# Event Operations #
####################


def publish(
    entity: AvEntity,
    auxiliary: AvEntity = NULL_ENTITY,
    ancillary: AvEntity = NULL_ENTITY,
    method: int = NULL_METHOD,
    attribute: int = NULL_ATTRIBUTE,
    instance: int = NULL_INSTANCE,
    offset: int = NULL_OFFSET,
    name: bytes = NULL_NAME,
    key: bytes = NULL_KEY,
    bytes: bytes = NULL_BYTES,
    parameter: int = NULL_PARAMETER,
    resultant: int = NULL_RESULTANT,
    index: int = NULL_INDEX,
    count: int = NULL_COUNT,
    aspect: int = NULL_ASPECT,
    context: int = NULL_CONTEXT,
    category: int = NULL_CATEGORY,
    klass: int = NULL_CLASS,
    event: int = NULL_EVENT,
    mode: int = NULL_MODE,
    state: int = NULL_STATE,
    condition: int = NULL_CONDITION,
    precedence: int = NULL_PRECEDENCE,
    tag: int = NULL_TAG,
    time: int = NULL_TIME,
    timeout: int = NULL_TIMEOUT,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.PUBLISH
    frame.entity = entity
    frame.auxiliary = auxiliary
    frame.ancillary = ancillary
    frame.method_code = method
    frame.attribute_code = attribute
    frame.instance = instance
    frame.offset = offset
    frame.name_count = len(name)
    frame.name = name
    frame.key_count = len(key)
    frame.key = key
    frame.load_bytes(bytes=bytes)
    frame.parameter = parameter
    frame.condition_code = condition
    frame.resultant = resultant
    frame.index = index
    frame.count = count
    frame.aspect_code = aspect
    frame.context_code = context
    frame.category_code = category
    frame.class_code = klass
    frame.event_code = event
    frame.mode_code = mode
    frame.state_code = state
    frame.precedence = precedence
    frame.tag_code = tag
    frame.time = time
    frame.timeout = timeout
    frame.authority = authority
    frame.authorization = authorization
    hgtp.post(frame=frame)


def subscribe(
    entity: AvEntity,
    outlet: AvEntity,
    event: int = NULL_EVENT,
    precedence: int = NULL_PRECEDENCE,
    timeout: int = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.SUBSCRIBE
    frame.entity = entity
    frame.outlet = outlet
    frame.event_code = event
    frame.precedence = precedence
    frame.timeout = timeout
    frame.authorization = authorization
    hgtp.post(frame=frame)


def unsubscribe(
    entity: AvEntity,
    outlet: AvEntity,
    event: int = NULL_EVENT,
    precedence: int = NULL_PRECEDENCE,
    timeout: int = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.UNSUBSCRIBE
    frame.entity = entity
    frame.outlet = outlet
    frame.event_code = event
    frame.precedence = precedence
    frame.timeout = timeout
    frame.authorization = authorization
    hgtp.post(frame=frame)


def flush(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Unsubscribe outlet from event."""
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.FLUSH
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


def wait(
    outlet: AvEntity,
    callback: Callable,
    timeout: int = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.WAIT
    frame.outlet = outlet
    frame.timeout = timeout
    frame.parameter = FALSE_PARAMETER
    frame.authorization = authorization

    channel = hgtp.borrow_socket()
    while True:
        hgtp.send(channel, frame)
        response = hgtp.recv(channel)

        # This is a ugly hack to filter out keepalive frames
        # Need to clarify with J asap how can we more cleanly filter them out
        if response.outlet != outlet and response.outlet == NULL_ENTITY:
            continue
        else:
            break

    hgtp.return_socket(channel)

    callback(
        entity=response.entity,
        outlet=response.outlet,
        auxiliary=response.auxiliary,
        ancillary=response.ancillary,
        method=response.method_code,
        attribute=response.attribute_code,
        aspect=response.aspect_code,
        context=response.context_code,
        category=response.category_code,
        klass=response.class_code,
        event=response.event_code,
        mode=response.mode_code,
        state=response.state_code,
        condition=response.condition_code,
        precedence=response.precedence,
        tag=response.tag_code,
        bytes=response._bytes,
        name=response.name,
        key=response.key,
        index=response.index,
        count=response.count,
        instance=response.instance,
        offset=response.offset,
        parameter=response.parameter,
        resultant=response.resultant,
        time=response.time,
        timeout=response.timeout,
        authority=response.authority,
        authorization=response.authorization,
    )


def wait_sustained(
    outlet: AvEntity,
    callback: Callable[..., bool],
    timeout: int = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.WAIT
    frame.outlet = outlet
    frame.timeout = timeout
    frame.parameter = TRUE_PARAMETER
    frame.authorization = authorization

    socket = hgtp.borrow_socket()
    hgtp.send(socket, frame)

    keepgoing = True
    while keepgoing:
        response = hgtp.recv(socket)
        # This is a ugly hack to filter out keepalive frames
        # Need to clarify with J asap how can we more cleanly filter them out
        if response.outlet != outlet and response.outlet == NULL_ENTITY:
            continue

        keepgoing = callback(
            entity=response.entity,
            outlet=response.outlet,
            auxiliary=response.auxiliary,
            ancillary=response.ancillary,
            method=response.method_code,
            attribute=response.attribute_code,
            aspect=response.aspect_code,
            context=response.context_code,
            category=response.category_code,
            klass=response.class_code,
            event=response.event_code,
            mode=response.mode_code,
            state=response.state_code,
            condition=response.condition_code,
            precedence=response.precedence,
            tag=response.tag_code,
            bytes=response._bytes,
            name=response.name,
            key=response.key,
            index=response.index,
            count=response.count,
            instance=response.instance,
            offset=response.offset,
            parameter=response.parameter,
            resultant=response.resultant,
            time=response.time,
            timeout=response.timeout,
            authority=response.authority,
            authorization=response.authorization,
        )
    if hgtp._socket_pool:
        hgtp._socket_pool.discard_socket(socket)


def subscribed(
    entity: AvEntity,
    event: int = NULL_EVENT,
    precedence: int = NULL_PRECEDENCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.SUBSCRIBED
    frame.entity = entity
    frame.event_code = event
    frame.precedence = precedence
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def subscription(
    outlet: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> Tuple[AvEntity, int, int, int]:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.SUBSCRIPTION
    frame.entity = outlet
    frame.index = index
    frame.authorization = authorization
    response = hgtp.post(frame=frame)

    return response.outlet, response.event_code, response.precedence, response.time


#####################
# Outlet Operations #
#####################


def activate(outlet: AvEntity, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.ACTIVATE
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


def deactivate(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.DEACTIVATE
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


# Avial 4.7: Added parameter to call, to support sustained adapts
def adapt(
    outlet: AvEntity,
    timeout: int,
    parameter: int,
    callback: Callable[[hgtp.HGTPFrame], tuple[AvTag, bytes]],
    authorization: AvAuthorization,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.ADAPT
    frame.outlet = outlet
    frame.timeout = timeout
    frame.parameter = parameter
    frame.authorization = authorization
    channel = hgtp.borrow_socket(dont_send_bye=True)
    hgtp.send(channel, frame)
    response = hgtp.recv(channel)

    try:
        tag, bytes = callback(response)

        frame.tag_code = int(tag)
        frame.load_bytes(bytes)
        hgtp.send(channel, frame)
    except Exception as error:
        frame = hgtp.HGTPFrame()
        frame.error_code = hgtp.HGTPException.ADAPTER
        frame.tag_code = AvTag.EXCEPTION
        frame.load_bytes(str(error).encode("utf-8")[:255])
        hgtp.send(channel, frame)

    hgtp.return_socket(channel)


def sync(outlet: AvEntity, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.SYNC
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


def lock(outlet: AvEntity, timeout: int, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.LOCK
    frame.outlet = outlet
    frame.timeout = timeout
    frame.authorization = authorization
    hgtp.post(frame=frame)


def unlock(outlet: AvEntity, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.UNLOCK
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


def arm(outlet: AvEntity, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.ARM
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


def disarm(outlet: AvEntity, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.DISARM
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


def schedule(
    outlet: AvEntity, count: int, event: int, authorization: AvAuthorization
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.SCHEDULE
    frame.outlet = outlet
    frame.count = count
    frame.event_code = event
    frame.authorization = authorization
    hgtp.post(frame=frame)


def start(outlet: AvEntity, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.START
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


def stop(outlet: AvEntity, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.STOP
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


def reset(outlet: AvEntity, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.RESET
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


def execute(
    outlet: AvEntity,
    entity: AvEntity,
    context: int,
    timeout: int,
    authorization: AvAuthorization,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.EXECUTE
    frame.outlet = outlet
    frame.entity = entity
    frame.context_code = context
    frame.timeout = timeout
    frame.authorization = authorization
    hgtp.post(frame=frame)


def halt(outlet: AvEntity, authorization: AvAuthorization) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.HALT
    frame.outlet = outlet
    frame.authorization = authorization
    hgtp.post(frame=frame)


############################
# Authorization Operations #
############################


def authorize(
    entity: AvEntity,
    parameter: int,
    authority: AvAuthorization,
    authorization: AvAuthorization,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.AUTHORIZE
    frame.entity = entity
    frame.parameter = parameter
    frame.authority = authority
    frame.authorization = authorization
    hgtp.post(frame=frame)


def deauthorize(
    entity: AvEntity, authority: AvAuthorization, authorization: AvAuthorization
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.DEAUTHORIZE
    frame.entity = entity
    frame.authority = authority
    frame.authorization = authorization
    hgtp.post(frame=frame)


def authorized(
    entity: AvEntity, authority: AvAuthorization, authorization: AvAuthorization
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.AUTHORIZED
    frame.entity = entity
    frame.authority = authority
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def authorization(
    entity: AvEntity, index: int, authorization: AvAuthorization
) -> AvAuthorization:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.AUTHORIZATION
    frame.entity = entity
    frame.index = index
    frame.authorization = authorization

    response = hgtp.post(frame=frame)

    return response.authorization


def authority(
    entity: AvEntity, authority: AvAuthorization, authorization: AvAuthorization
) -> AvAuthorization:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.AUTHORITY
    frame.entity = entity
    frame.authority = authority
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.authority


##################
# Entity hgtp.Reports #
##################


def name(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bytes:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.NAME
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.name


def key(entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION) -> bytes:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.KEY
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)

    return response.key


def context(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.CONTEXT
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.context_code


def category(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.CATEGORY
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.category_code


def klass(entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.CLASS
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.class_code


def state(entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.STATE
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.state_code


def elements(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.ELEMENTS
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def extinct(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.EXTINCT
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def available(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.AVAILABLE
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def activated(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.ACTIVATED
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def locked(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.LOCKED
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def armed(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.ARMED
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def active(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.ACTIVE
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def busy(entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.ACTIVE
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.resultant == 1


def references(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.REFERENCES
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def authorizations(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.AUTHORIZATIONS
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def conditions(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.CONDITIONS
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def subscriptions(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.SUBSCRIPTIONS
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def timer(entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.TIMER
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def elapsed(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.ELAPSED
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count == 1


def blocking(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.BLOCKING
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def pending(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.PENDING
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def waiting(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.WAITING
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def invoking(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.INVOKING
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def adapting(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.ADAPTING
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.count


def server(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvEntity:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.SERVER
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.entity


def redirection(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvEntity:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.REDIRECTION
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.entity


def rendezvous(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> str:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.RENDEZVOUS
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response._bytes.decode()


def timestamp(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.TIMESTAMP
    frame.entity = entity
    frame.authorization = authorization
    response = hgtp.post(frame=frame)
    return response.time


##################
# Server hgtp.Reports #
##################


# Avial 4.7: Local call now routable using server parameter
def local(server: AvEntity = NULL_ENTITY) -> AvEntity:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.entity = server
    frame.report_code = hgtp.Report.LOCAL
    response = hgtp.post(frame=frame)
    return response.entity


# Avial 4.7: Gateway call now routable using server parameter
def server_gateway(server: AvEntity = NULL_ENTITY) -> AvEntity:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.entity = server
    frame.report_code = hgtp.Report.GATEWAY
    response = hgtp.post(frame=frame)
    return response.entity


# Avial 4.7: Version call now routable using server parameter
def version(server: AvEntity = NULL_ENTITY) -> bytes:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.entity = server
    frame.report_code = hgtp.Report.VERSION
    response = hgtp.post(frame=frame)
    return response._bytes


# Avial 4.7: Hostname call now routable using server parameter
def hostname(server: AvEntity = NULL_ENTITY) -> bytes:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.entity = server
    frame.report_code = hgtp.Report.HOSTNAME
    response = hgtp.post(frame=frame)
    return response._bytes


# Avial 4.7: Status call now routable using server parameter
def status(server: AvEntity = NULL_ENTITY) -> bytes:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.STATUS
    frame.entity = server
    response = hgtp.post(frame=frame)
    return response._bytes


# Avial 4.7: Clock call now routable using server parameter
def clock(server: AvEntity = NULL_ENTITY) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.CLOCK
    frame.entity = server
    response = hgtp.post(frame=frame)
    return response.time


# Avial 4.7: Address call now routable using server parameter
def address(server: AvEntity = NULL_ENTITY) -> IPv4Address | IPv6Address:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.ADDRESS
    frame.entity = server
    response = hgtp.post(frame=frame)
    return ipaddress.ip_address(response.resultant)


# Avial 4.7: Internet call now routable using server parameter
def internet(server: AvEntity = NULL_ENTITY) -> Tuple[int, bytes]:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.REPORT
    frame.report_code = hgtp.Report.INTERNET
    frame.entity = server
    response = hgtp.post(frame=frame)
    return response.tag_code, response._bytes


# AvesTerra 6.0
def set(
    entity: AvEntity = NULL_ENTITY,
    condition: int = NULL_CONDITION,
    name: bytes = NULL_NAME,
    tag: int = NULL_TAG,
    bytes: bytes = NULL_BYTES,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.SET
    frame.entity = entity
    frame.condition_code = condition
    frame.name = name
    frame.name_count = len(name)
    frame.tag_code = tag
    frame.load_bytes(bytes=bytes)
    frame.authorization = authorization
    hgtp.post(frame=frame)


# AvesTerra 6.0
def clear(
    entity: AvEntity = NULL_ENTITY,
    condition: int = NULL_CONDITION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.CLEAR
    frame.entity = entity
    frame.condition_code = condition
    frame.authorization = authorization
    hgtp.post(frame=frame)


# AvesTerra 6.0
def test(
    entity: AvEntity = NULL_ENTITY,
    condition: int = NULL_CONDITION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.TEST
    frame.entity = entity
    frame.condition_code = condition
    frame.authorization = authorization
    return hgtp.post(frame=frame).resultant == 1


# AvesTerra 6.0
def condition(
    entity: AvEntity = NULL_ENTITY,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> int:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.CONDITION
    frame.entity = entity
    frame.index = index
    frame.authorization = authorization
    return hgtp.post(frame=frame).condition_code


# AvesTerra 6.0
def label(
    entity: AvEntity = NULL_ENTITY,
    condition: int = NULL_CONDITION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bytes:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.LABEL
    frame.entity = entity
    frame.condition_code = condition
    frame.authorization = authorization
    return hgtp.post(frame=frame).name


# AvesTerra 6.0
def variable(
    entity: AvEntity = NULL_ENTITY,
    condition: int = NULL_CONDITION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> Tuple[int, bytes]:
    frame = hgtp.HGTPFrame()
    frame.command_code = hgtp.Command.VARIABLE
    frame.entity = entity
    frame.condition_code = condition
    frame.authorization = authorization
    return frame.tag_code, frame._bytes
