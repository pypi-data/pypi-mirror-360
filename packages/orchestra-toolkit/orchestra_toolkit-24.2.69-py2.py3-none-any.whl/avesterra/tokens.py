""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avial import *

AvToken = AvAuthorization


# Avial 4.12: Was called enabled previously
def instate(
    token: AvAuthorization,
    authority: AvAuthorization,
    authorization: AvAuthorization,
    server: AvEntity = NULL_ENTITY,
):
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=INSTATE_PARAMETER,
        value=AvValue.encode(str(token)),
        authority=authority,
        authorization=authorization,
    )


# Avial 4.12: Was called disable previously
def destate(
    token: AvAuthorization,
    authorization: AvAuthorization,
    server: AvEntity = NULL_ENTITY,
):
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=DESTATE_PARAMETER,
        value=AvValue.encode(str(token)),
        authorization=authorization,
    )


def retrieve(
    authorization: AvAuthorization, server: AvEntity = NULL_ENTITY
) -> List[Tuple[AvAuthorization, AvAuthorization]]:
    result = invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=TRUE_PARAMETER,
        authorization=authorization,
    )

    entity_obj: Dict = json.loads(result.decode_interchange())

    attributes = entity_obj["Attributes"]

    # If no tokens are present, then return empty list
    if "TOKEN_ATTRIBUTE" not in attributes.keys():
        return []

    token_maps = attributes["TOKEN_ATTRIBUTE"][0]["Properties"]

    # Build mapping
    token_mapping: List[Tuple[AvAuthorization, AvAuthorization]] = []
    for token_str, empty, auth_str in token_maps:
        token_mapping.append((AvAuthorization(token_str), AvAuthorization(auth_str)))

    # Return mapping
    return token_mapping


def resolve(
    token: AvAuthorization | str,
    authorization: AvAuthorization,
    token_map: List[Tuple[AvAuthorization, AvAuthorization]] | None = None,
):
    if isinstance(token, str):
        token = AvAuthorization(token)

    # If no token map was given, get one from the server
    if token_map is None:
        token_map = retrieve(authorization=authorization)

    # Search for auth that maps to
    # given token
    for map_token, map_auth in token_map:
        if map_token == token:
            return map_auth

    # If token not found, return empty token list
    return []


def display(token_map: List[Tuple[AvAuthorization, AvAuthorization]]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}

    # Build mapping
    for token, auth in token_map:
        mapping[f"{str(token)}"] = str(auth)

    # Print formatted JSON string for easy reading
    print(json.dumps(mapping, indent=1))

    # Return mapping
    return mapping


def couple(
    network: AvEntity,
    token: AvToken,
    authority: AvAuthorization,
    authorization: AvAuthorization,
    server: AvEntity = NULL_ENTITY,
):
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=COUPLE_PARAMETER,
        value=AvValue.encode_avesterra(str(token)),
        auxiliary=network,
        authority=authority,
        authorization=authorization,
    )


def decouple(
    network: AvEntity,
    token: AvToken,
    authorization: AvAuthorization,
    server: AvEntity = NULL_ENTITY,
):
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=DECOUPLE_PARAMETER,
        value=AvValue.encode_avesterra(str(token)),
        auxiliary=network,
        authorization=authorization,
    )


def pair(
    host: AvEntity,
    token: AvToken,
    authority: AvAuthorization,
    authorization: AvAuthorization,
    server: AvEntity = NULL_ENTITY,
):
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=PAIR_PARAMETER,
        value=AvValue.encode_avesterra(str(token)),
        auxiliary=host,
        authority=authority,
        authorization=authorization,
    )


def unpair(
    host: AvEntity,
    token: AvToken,
    authorization: AvAuthorization,
    server: AvEntity = NULL_ENTITY,
):
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=UNPAIR_PARAMETER,
        value=AvValue.encode_avesterra(str(token)),
        auxiliary=host,
        authorization=authorization,
    )


# Avial 4.12
def map(
    token: AvToken,
    mask: AvMask,
    authority: AvAuthorization,
    authorization: AvAuthorization,
    server: AvEntity = NULL_ENTITY,
):
    credential = encode_credential(token, mask)
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=MAP_PARAMETER,
        value=AvValue.encode_avesterra(str(credential)),
        authority=authority,
        authorization=authorization,
    )


# Avial 4.12
def unmap(
    token: AvToken,
    authority: AvAuthorization,
    authorization: AvAuthorization,
    server: AvEntity = NULL_ENTITY,
):
    token = encode_credential(token, AvMask())
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=UNMAP_PARAMETER,
        value=AvValue.encode_avesterra(str(token)),
        authority=authority,
        authorization=authorization,
    )
