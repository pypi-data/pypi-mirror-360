""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avial import *


def allow_rule(
    address: AvAddress,
    server: AvEntity = NULL_ENTITY,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=ALLOW_PARAMETER,
        value=AvValue.encode_avesterra(str(address)),
        index=index,
        authorization=authorization,
    )


def deny_rule(
    address: AvAddress,
    server: AvEntity = NULL_ENTITY,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=DENY_PARAMETER,
        value=AvValue.encode_avesterra(str(address)),
        index=index,
        authorization=authorization,
    )


def void_rule(
    server: AvEntity = NULL_ENTITY,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=VOID_PARAMETER,
        index=index,
        authorization=authorization,
    )
