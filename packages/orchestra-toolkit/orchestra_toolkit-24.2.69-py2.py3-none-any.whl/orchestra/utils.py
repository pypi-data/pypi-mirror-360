""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avial import AvTime
import avesterra.avial as avial

def get_entity_update_time(
    entity: avial.AvEntity, auth: avial.AvAuthorization
) -> avial.AvTime:
    try:
        return avial.entity_element(
            entity=entity, index=1, authorization=auth
        ).decode_time()
    except avial.EntityError as ae:
        return avial.entity_timestamp(entity=entity, authorization=auth)


def set_entity_update_time(
    entity: avial.AvEntity, auth: avial.AvAuthorization
) -> avial.AvTime:
    output: AvTime = AvTime.utcnow()
    try:
        avial.replace_element(
            entity=entity,
            value=avial.AvValue.encode_time(output),
            index=1,
            authorization=auth,
        )
    except avial.EntityError as ee:
        avial.insert_element(
            entity=entity,
            value=avial.AvValue.encode_time(output),
            index=1,
            authorization=auth,
        )
    return output
