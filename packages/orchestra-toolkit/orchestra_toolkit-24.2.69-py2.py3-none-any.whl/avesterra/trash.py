""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avial import *
from avesterra.predefined import trash_outlet
from avesterra.taxonomy import AvCategory, AvClass
import avesterra.properties as properties

AvTrash = AvEntity


def create_trash(
    authorization: AvAuthorization,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    outlet: AvEntity = NULL_ENTITY,
    server: AvEntity = NULL_ENTITY,
) -> AvTrash:
    return create_entity(
        server=server,
        name=name,
        key=key,
        category=AvCategory.AVESTERRA,
        klass=AvClass.REGISTRY,
        outlet=(trash_outlet if outlet == NULL_ENTITY else outlet),
        authorization=authorization,
    )


def delete_trash(trash: AvTrash, authorization: AvAuthorization):
    # Empty trash before deleting
    empty_trash(trash=trash, authorization=authorization)
    delete_entity(entity=trash, authorization=authorization)


def empty_trash(trash: AvTrash, authorization: AvAuthorization):
    # Get Number of items in trash
    trash_count = properties.property_count(entity=trash, authorization=authorization)

    for i in range(trash_count):
        entity = properties.property_value(
            entity=trash, index=1, authorization=authorization
        ).decode_entity()
        properties.remove_property(
            entity=trash,
            index=1,
            parameter=DEFERRAL_PARAMETER,
            authorization=authorization,
        )

        # Prevent deleting trash entity if it is in its own trash
        if entity != trash:
            if entity_references(entity=entity, authorization=authorization) == 0:
                try:
                    purge_entity(entity=entity, authorization=authorization)
                except Exception as e:
                    print(
                        f"Warning: could not purge entity {entity} found in trash {trash}"
                    )
            delete_entity(entity=entity, authorization=authorization)
    save_entity(entity=trash, authorization=authorization)
