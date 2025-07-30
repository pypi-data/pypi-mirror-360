""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""
from avesterra.avial import *


class Routing(IntEnum):
    NULL = NULL_PARAMETER
    LOGICAL = LOGICAL_PARAMETER
    PHYSICAL = PHYSICAL_PARAMETER
    VIRTUAL = VIRTUAL_PARAMETER


def route_host(
    server: AvEntity,
    host: AvEntity,
    authorization: AvAuthorization,
    address: AvAddress = NULL_ADDRESS,
    trusted: bool = False,
):
    return invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=HOST_PARAMETER,
        name="TRUSTED" if trusted else "",
        key=str(host),
        value=AvValue.encode_string(
            str(address) if address is not NULL_ADDRESS else ""
        ),
        authorization=authorization,
    )


def route_network(
    server: AvEntity,
    network: AvEntity,
    authorization: AvAuthorization,
    address: AvAddress = NULL_ADDRESS,
    trusted: bool = False,
):
    return invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=NETWORK_PARAMETER,
        name="TRUSTED" if trusted else "",
        key=str(network),
        value=AvValue.encode_string(
            str(address) if address is not NULL_ADDRESS else ""
        ),
        authorization=authorization,
    )


def include_host(
    server: AvEntity,
    host_entity: AvEntity,
    authorization: AvAuthorization,
    address: AvAddress = NULL_ADDRESS,
    trusted: bool = False,
):
    if not address:
        raise ValueError("Argument `address` cannot be NULL when including a host")

    route_host(
        server=server,
        address=address,
        host=host_entity,
        trusted=trusted,
        authorization=authorization,
    )


def exclude_host(server: AvEntity, host: AvEntity, authorization: AvAuthorization):
    route_host(server=server, host=host, address=0, authorization=authorization)


def include_network(
    server: AvEntity,
    network: AvEntity,
    address: AvAddress,
    authorization: AvAuthorization,
    trusted: bool = False,
):
    if not address:
        raise ValueError("Argument `address` cannot be NULL when including a network")

    route_network(
        server=server,
        address=address,
        network=network,
        trusted=trusted,
        authorization=authorization,
    )


def exclude_network(
    server: AvEntity, network: AvEntity, authorization: AvAuthorization
):
    route_network(
        server=server,
        network=network,
        authorization=authorization,
    )


def enable_routing(
    server: AvEntity,
    local: AvEntity,
    authorization: AvAuthorization,
    routing: Routing = Routing.NULL,
    gateway: AvEntity = NULL_ENTITY,
):
    if not isinstance(routing, Routing):
        raise TypeError("Argument `routing` must be an instance of Routing")

    # If routing is NULL, then don't change routing,
    # only allow the change of the routing type
    if routing != Routing.NULL:
        # Turn on routing
        invoke_entity(
            entity=server,
            method=AvMethod.AVESTERRA,
            parameter=AvParameter(routing.value),
            authorization=authorization,
        )

    # If no gateway was specified, assume that host_entity is its own gateway
    if gateway == NULL_ENTITY:
        gateway = local

    # Configure routing
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=CONFIGURE_PARAMETER,
        key=str(local),
        value=AvValue.encode_entity(gateway),
        authorization=authorization,
    )

def parse_networks(server_model: Dict) -> Dict[str, Tuple[bool, int]]:
    attributes = server_model["Attributes"]
    network_info: Dict[str, Tuple[bool, int]] = {}
    for attribute in attributes:
        if 'NETWORK_ATTRIBUTE' in attribute:
            for trusted, entity_str, num_address_str in attribute[2]:
                network_info[entity_str] = (trusted == "TRUSTED", int(num_address_str))
    return network_info

def parse_hosts(server_model: Dict) -> Dict[str, Tuple[bool, int]]:
    attributes = server_model["Attributes"]
    host_info: Dict[str, Tuple[bool, int]] = {}
    for attribute in attributes:
        if 'HOST_ATTRIBUTE' in attribute:
            for trusted, entity_str, num_address_str in attribute[2]:
                host_info[entity_str] = (trusted == "TRUSTED", int(num_address_str))
    return host_info


