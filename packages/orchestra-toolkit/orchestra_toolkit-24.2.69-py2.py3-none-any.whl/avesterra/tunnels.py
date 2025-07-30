""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.predefined import tunnel_outlet
from avesterra.avial import *

AvTunnel = AvEntity
AvPortal = AvEntity


def create_tunnel(
    name: AvName = NULL_NAME,
    portal: AvPortal = NULL_ENTITY,
    server: AvEntity = NULL_ENTITY,
    outlet: AvEntity = NULL_ENTITY,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvTunnel:
    adapter_outlet = outlet if outlet != NULL_ENTITY else tunnel_outlet
    return invoke_entity(
        entity=adapter_outlet,
        method=AvMethod.CREATE,
        name=name,
        context=AvContext.AVESTERRA,
        category=AvCategory.TUNNEL,
        klass=AvClass.TUNNEL,
        value=AvValue.encode_authorization(authority),
        auxiliary=portal,
        ancillary=server,
        authorization=authorization,
    ).decode_entity()


def delete_tunnel(
    tunnel: AvTunnel, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    invoke_entity(
        entity=tunnel,
        method=AvMethod.DELETE,
        authorization=authorization,
    )


def open_portal(
    portal: AvPortal,
    name: AvName = NULL_NAME,
    server: AvEntity = NULL_ENTITY,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        name=name,
        auxiliary=portal,
        parameter=PORTAL_PARAMETER,
        authority=authority,
        authorization=authorization,
    )


def close_portal(
    portal: AvPortal,
    server: AvEntity = NULL_ENTITY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        auxiliary=portal,
        parameter=UNPORTAL_PARAMETER,
        authorization=authorization,
    )

def parse_portals(server_model: Dict) -> Dict[str, str]:
    attributes = server_model["Attributes"]
    portal_info: Dict[str, Tuple[bool, int]] = {}
    for attribute in attributes:
        if 'PORTAL_ATTRIBUTE' in attribute:
            for name, entity_str, _ in attribute[2]:
                portal_info[entity_str] = name
    return portal_info
