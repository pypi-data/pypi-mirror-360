""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import avesterra.avial as avial
import avesterra.properties as properties
from avesterra.avial import *
from avesterra.predefined import registry_outlet
import json

AvRegistry = avial.AvEntity


def get_registry_entries(
    registry: AvRegistry, authorization: AvAuthorization
) -> Dict[AvKey, Tuple[AvName, AvKey, avial.AvEntity]]:
    """Retrieve the registry and return entries.

    Parameters
    __________
    registry : AvRegistry
        Entity EUID of the registry from which one wants to retrieve entries.
    authorization : AvAuthorization
        An authorization that is able to read from the given registry.

    Examples
    ________

    >>> import avesterra.registries as registries
    >>> registry: AvRegistry
    >>> authorization: AvAuthorization
    >>> registry_entries = registries.get_registry_entries(registry=registry, authorization=authorization)
    >>> print(registry_entries)
    {'US': ('United States of America', 'us', AvEntity(0,0,193048)),'Taiwan': ('Taiwan', 'tw', AvEntity(0,0,193049)),'France': ('France', 'fr', AvEntity(0,0,193050))}

    Returns
    _______
    Dict[AvKey, Tuple[AvName, AvKey, AvEntity]]
        A Dict of the registry entries

    """
    interchange = retrieve_registry(registry, authorization)
    interchange_obj = json.loads(interchange)

    properties = interchange_obj.get("Properties", [])
    return dict(
        (p[1], (p[0], p[1], AvValue.from_json(p[2]).decode_entity()))
        for p in properties
    )


def create_registry(
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    mode: AvMode = AvMode.NULL,
    outlet: AvEntity = NULL_ENTITY,
    server: AvEntity = NULL_ENTITY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvRegistry:
    """Creates a registry.

    Parameters
    __________
    name : AvName
        Name of the registry to create
    key : AvKey
        Key of the registry to create
    mode : AvMode
        Mode of the registry creation.
    outlet : AvEntity
        Entity EUID of the outlet that one will be connected to created entity; if none is given, then the default Registry Adapter Outlet is used.
    server : AvEntity
        Entity EUID of the server that created the registry will be created on.
    authorization : AvAuthorization
        The authorization used to create the registry; authorization must be on the registry_adapter_outlet.

    Examples
    ________

    >>> import avesterra.registries as registries
    >>> authorization: AvAuthorization
    >>> registry_name: str = "TestRegistry"
    >>> registry_key: str = "test_registry"
    >>> registry = registries.create_registry(name=registry_name, key=registry_key, authorization=authorization)
    >>> registry
    AvEntity(registry.pid, registry.hid, registry.uid)

    Returns
    _______
    AvRegistry
        EUID of the newly created registry

    """
    adapter = registry_outlet if outlet == NULL_ENTITY else outlet
    return invoke_entity(
        entity=adapter,
        method=AvMethod.CREATE,
        name=name,
        key=key,
        context=AvContext.AVESTERRA,
        category=AvCategory.AVESTERRA,
        klass=AvClass.AVESTERRA,
        mode=mode,
        ancillary=server,
        authorization=authorization,
    ).decode_entity()


def delete_registry(
    registry: AvRegistry, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Deletes a registry.

    Parameters
    __________
    registry : AvRegistry
        EUID of the registry to delete.
    authorization : AvAuthorization
        The authorization used to delete the registry; authorization must be on both the registry and the registry_adapter_outlet.

    Examples
    ________

    >>> import avesterra.registries as registries
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> authorization: AvAuthorization
    >>> registries.delete_registry(registry=registry, authorization=authorization)

    """
    invoke_entity(entity=registry, method=AvMethod.DELETE, authorization=authorization)


def register_entity(
    registry: AvRegistry,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    entity: AvEntity = NULL_ENTITY,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Registers an entity in the given registry.

    Parameters
    __________
    registry : AvRegistry
        EUID of the registry in which to register the entity.
    name : AvName
        Name to register the entity under.
    key : AvKey
        Key to register the entity under.
    entity : AvEntity
        Entity to register in the registry.
    parameter : AvParameter
        Parameter to use for the register_entity call.
    authorization : AvAuthorization
        The authorization used to register the entity; authorization must be on both the registry and the registry_adapter_outlet.

    Examples
    ________
    >>> import avesterra.registries as registries
    >>> import avesterra.avial as av
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity = av.create_entity(authorization=authorization)
    >>> authorization: AvAuthorization
    >>> name: str = "Example Entity"
    >>> key: str = "example_entity"
    >>> registries.register_entity(entity=entity, name=name, key=key, authorization=authorization)

    """
    properties.include_property(
        entity=registry,
        name=name,
        key=key,
        value=AvValue.encode(entity),
        parameter=parameter,
        authorization=authorization,
    )


def deregister_entity(
    registry: AvRegistry,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """De-registers an entity from a registry.

    Parameters
    __________
    registry : AvRegistry
        EUID of the registry in which to register the entity.
    key : AvKey
        Key of entity to deregister from the registry.
    authorization : AvAuthorization
        The authorization used to de-register the entity from the registry; authorization must be on both the registry and the registry_adapter_outlet.

    Examples
    ________

    >>> import avesterra.registries as registries
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> authorization: AvAuthorization
    >>> key: str = "example_entity"
    >>> registry: AvRegistry = registries.deregister_entity(registry=registry, key=key, authorization=authorization)

    """
    properties.exclude_property(entity=registry, key=key, authorization=authorization)


def save_registry(
    registry: AvRegistry, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Saves a registry's contents

    Parameters
    __________
    registry : AvRegistry
        Entity EUID of registry to save
    authorization : AvAuthorization
        Authorization to use for the operation; the authorization must be accepted by both the `registry` and Registry Adapter outlet `<x|x|10>`

    Examples
    ________
    >>> import avesterra.registries as registries
    >>> import avesterra.avial as av
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity1: AvEntity = av.create_entity(authorization=authorization)
    >>> entity2: AvEntity = av.create_entity(authorization=authorization)
    >>> registries.register_entity(registry=registry, name="entity1", key="entity1", entity=entity1, authorization=authorization) # Register entity1 in registry
    >>> print(registries.registry_member(registry=registry, key="entity1", authorization=authorization)) # entity1 should now be a member of registry
    True
    >>> registries.save_registry(registry=registry, authorization=authorization) # Save a snapshot of registry
    >>> registries.register_entity(registry=registry, name="entity2", key="entity2", entity=entity2, authorization=authorization) # Register entity2 in registry
    >>> print(registries.registry_member(registry=registry, key="entity2", authorization=authorization)) # entity2 should now be a member of registry
    True
    >>> registries.restore_entity(entity=registry, authorization=authorization) # Restore registry content to previous save point
    >>> print(registries.registry_member(registry=registry, key="entity1", authorization=authorization)) # entity2 should now be a member of registry
    True
    >>> print(registries.registry_member(registry=registry, key="entity2", authorization=authorization)) # entity2 should no longer be a member of registry, because entity2 wasn't a member before save_registry was called
    False

    """
    avial.save_entity(entity=registry, authorization=authorization)


def purge_registry(
    registry: AvRegistry, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Purge a registry's contents

    Parameters
    __________
    registry : AvRegistry
        Entity EUID of registry to purge
    authorization : AvAuthorization
        Authorization to use for the operation; the authorization must be accepted by both the `registry` and Registry Adapter outlet `<x|x|10>`

    Examples
    ________
    >>> import avesterra.registries as registries
    >>> import avesterra.avial as av
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity1: AvEntity = av.create_entity(authorization=authorization)
    >>> registries.register_entity(registry=registry, name="entity1", key="entity1", entity=entity1, authorization=authorization) # Register entity1 in registry
    >>> print(registries.registry_member(registry=registry, key="entity1", authorization=authorization)) # entity1 should now be a member of registry
    True
    >>> registries.purge_registry(registry=registry, authorization=authorization) # Purge registry of all records; doesn't delete registry
    >>> print(registries.registry_member(registry=registry, key="entity1", authorization=authorization)) # entity1 should no longer be a member of registry
    False

    """
    properties.purge_properties(entity=registry, authorization=authorization)


def sort_registry(
    registry: AvRegistry, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Sort a registry's records by key

    Parameters
    __________
    registry : AvRegistry
        Entity EUID of registry to sort
    authorization : AvAuthorization
        Authorization to use for the operation; the authorization must be accepted by both the `registry` and Registry Adapter outlet `<x|x|10>`

    Examples
    ________
    >>> import avesterra.registries as registries
    >>> import avesterra.avial as av
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity1: AvEntity = av.create_entity(authorization=authorization)
    >>> entity2: AvEntity = av.create_entity(authorization=authorization)
    >>> entity3: AvEntity = av.create_entity(authorization=authorization)
    >>> registries.register_entity(registry=registry,name="entity3",key="entity3",entity=entity3,authorization=authorization)  # Register entity3 in registry
    >>> registries.register_entity(registry=registry,name="entity1",key="entity1",entity=entity1,authorization=authorization)  # Register entity1 in registry
    >>> registries.register_entity(registry=registry,name="entity2",key="entity2",entity=entity2,authorization=authorization)  # Register entity2 in registry
    >>> print(json.loads(registries.retrieve_registry(registry=registry, authorization=authorization))) # Retrieve registry contents as a JSON string, before sorting
    {'Properties': [['entity3', 'entity3', {'ENTITY': '<0|0|106881>'}], ['entity1', 'entity1', {'ENTITY': '<0|0|106879>'}], ['entity2', 'entity2', {'ENTITY': '<0|0|106880>'}]]}
    >>> registries.sort_registry(registry=registry, authorization=authorization) # Sort registry by key
    >>> print(json.loads(registries.retrieve_registry(registry=registry, authorization=authorization))) # Retrieve registry contents as a JSON string, after sorting
    {'Properties': [['entity1', 'entity1', {'ENTITY': '<0|0|106875>'}], ['entity2', 'entity2', {'ENTITY': '<0|0|106875>'}], ['entity3', 'entity3', {'ENTITY': '<0|0|106875>'}]]}

    """
    properties.sort_properties(entity=registry, authorization=authorization)


def lookup_registry(
    registry: AvRegistry,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvEntity:
    """Lookup an entity in the given registry using a key

    Parameters
    __________
    registry : AvRegistry
        Entity EUID of registry to perform the lookup in
    key : AvKey
        Key to lookup in the given registry
    authorization : AvAuthorization
        Authorization to use for the operation; the authorization must be accepted by both the `registry` and Registry Adapter outlet `<x|x|10>`

    Examples
    ________
    >>> import avesterra.registries as registries
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity: AvEntity = av.create_entity(authorization=authorization)
    >>> registries.register_entity(registry=registry,name="entity1",key="entity1",entity=entity,authorization=authorization)  # Register entity1 in registry
    >>> assert registries.lookup_registry(registry=registry, key="entity1", authorization=authorization) == entity # Lookup should succeed


    >>> import avesterra.registries as registries
    >>> import avesterra.avial as av
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity: AvEntity = av.create_entity(authorization=authorization)
    >>> assert registries.lookup_registry(registry=registry, key="a_really_non_existent_key", authorization=authorization) == NULL_ENTITY # Lookup should fail

    Raises
    ______
    ApplicationError
        When key is not found in the registry

    Returns
    _______
    AvEntity
        Entity EUID associated with key in the given registry

    """

    val = properties.property_value(
        entity=registry, key=key, authorization=authorization
    )

    if val == avial.NULL_VALUE:
        raise ApplicationError("Key {key} not found in registry {registry}")
    else:
        return val.decode_entity()


def registry_item(
    registry: AvRegistry,
    index: AvIndex = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Return the value registered at index in registry

    Parameters
    __________
    registry : AvRegistry
        Entity EUID of registry to perform the lookup in
    index: AvIndex
        Index of record in registry to return
    authorization : AvAuthorization
        Authorization to use for the operation; the authorization must be accepted by both the `registry` and Registry Adapter outlet `<x|x|10>`

    Examples
    ________

    >>> import avesterra.registries as registries
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity: AvEntity = av.create_entity(authorization=authorization)
    >>> registries.register_entity(registry=registry,name="entity1",key="entity1",entity=entity,authorization=authorization)  # Register entity1 in registry
    >>> print(registries.registry_item(registry=registry, index=1, authorization=authorization).decode_entity() == entity)# Item retrieval should succeed

    >>> import avesterra.registries as registries
    >>> import avesterra.avial as av
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity: AvEntity = av.create_entity(authorization=authorization)
    >>> registries.register_entity(registry=registry,name="entity1",key="entity1",entity=entity,authorization=authorization)  # Register entity1 in registry
    >>> print(registries.registry_item(registry=registry, index=100, authorization=authorization).decode_entity() == entity) # Item retrieval should fail
    False

    Raises
    ______
    ApplicationError
        When no value is present at index in registry

    Returns
    _______
    AvValue
        Value at index in registry

    """
    return properties.property_value(
        entity=registry, index=index, authorization=authorization
    )


def registry_count(
    registry: AvRegistry, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvCount:
    """Return the number of items registered in registry

    Parameters
    __________
    registry : AvRegistry
        Entity EUID of registry to get record count of
    authorization : AvAuthorization
        Authorization to use for the operation; the authorization must be accepted by both the `registry` and Registry Adapter outlet `<x|x|10>`

    Examples
    ________

    >>> import avesterra.registries as registries
    >>> import avesterra.avial as av
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity1: AvEntity = av.create_entity(authorization=authorization)
    >>> entity2: AvEntity = av.create_entity(authorization=authorization)
    >>> entity3: AvEntity = av.create_entity(authorization=authorization)
    >>> registries.register_entity(registry=registry,name="entity1",key="entity1",entity=entity1,authorization=authorization)  # Register entity1 in registry
    >>> registries.register_entity(registry=registry,name="entity3",key="entity3",entity=entity3,authorization=authorization)  # Register entity3 in registry
    >>> registries.register_entity(registry=registry,name="entity2",key="entity2",entity=entity2,authorization=authorization)  # Register entity2 in registry
    >>> print(registries.registry_count(registry=registry, authorization=authorization)) # 3 entities were registered with registry
    3

    Returns
    _______
    AvCount
        Number of records in registry

    """
    return properties.property_count(entity=registry, authorization=authorization)


def registry_member(
    registry: AvRegistry,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvBoolean:
    """Return a boolean indicating whether a key is registered in the registry

    Parameters
    __________
    registry : AvRegistry
        Entity EUID of registry perform key check on
    key : AvKey
        Key to check in the registry
    authorization : AvAuthorization
        Authorization to use for the operation; the authorization must be accepted by both the `registry` and Registry Adapter outlet `<x|x|10>`

    Examples
    ________

    >>> import avesterra.registries as registries
    >>> import avesterra.avial as av
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity1: AvEntity = av.create_entity(authorization=authorization)
    >>> registries.register_entity(registry=registry,name="entity1",key="entity1",entity=entity1,authorization=authorization)  # Register entity1 in registry
    >>> print(registries.registry_member(registry=registry, authorization=authorization))
    True

    >>> import avesterra.registries as registries
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> print(registries.registry_member(registry=registry, authorization=authorization))
    False

    Returns
    _______
    AvBoolean
        True if key is registered in registry, False otherwise

    """
    return properties.property_member(
        entity=registry, key=key, authorization=authorization
    )


def registry_name(
    registry: AvRegistry, key: str, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvName:
    """Return name of record, mapped to key, in registry

    Parameters
    __________
    registry : AvRegistry
        Entity EUID of registry perform record name retrieval on
    key : AvKey
        Key of record to retrieve
    authorization : AvAuthorization
        Authorization to use for the operation; the authorization must be accepted by both the `registry` and Registry Adapter outlet `<x|x|10>`

    Examples
    ________

    >>> import avesterra.registries as registries
    >>> import avesterra.avial as av
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity1: AvEntity = av.create_entity(authorization=authorization)
    >>> registries.register_entity(registry=registry,name="ENTITY1",key="entity1",entity=entity1,authorization=authorization)  # Register entity1 in registry
    >>> print(registries.registry_name(registry=registry, key="entity1", authorization=authorization))
    "ENTITY1"

    Returns
    _______
    AvName
        Name of record, mapped to key, in registry

    """
    return properties.property_name(
        entity=registry, key=key, authorization=authorization
    )


def retrieve_registry(
    registry: AvRegistry, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvInterchange:
    """Retrieve all records of registry, encoded as a JSON string

    Parameters
    __________
    registry : AvRegistry
        Entity EUID of registry perform record name retrieval on
    authorization : AvAuthorization
        Authorization to use for the operation; the authorization must be accepted by both the `registry` and Registry Adapter outlet `<x|x|10>`

    Examples
    ________
    >>> import avesterra.registries as registries
    >>> import avesterra.avial as av
    >>> authorization: AvAuthorization
    >>> registry: AvRegistry = registries.create_registry(authorization=authorization)
    >>> entity1: AvEntity = av.create_entity(authorization=authorization)
    >>> entity2: AvEntity = av.create_entity(authorization=authorization)
    >>> entity3: AvEntity = av.create_entity(authorization=authorization)
    >>> entity4: AvEntity = av.create_entity(authorization=authorization)
    >>> registries.register_entity(registry=registry,name="entity1",key="entity1",entity=entity1,authorization=authorization)  # Register entity1 in registry
    >>> registries.register_entity(registry=registry,name="entity2",key="entity2",entity=entity2,authorization=authorization)  # Register entity2 in registry
    >>> registries.register_entity(registry=registry,name="entity3",key="entity3",entity=entity3,authorization=authorization)  # Register entity3 in registry
    >>> registries.register_entity(registry=registry,name="entity4",key="entity4",entity=entity4,authorization=authorization)  # Register entity3 in registry
    >>> print(registries.retrieve_registry(registry=registry, authorization=authorization))
    {"Properties":[["entity1","entity1",{"ENTITY":"<0|0|106895>"}],["entity2","entity2",{"ENTITY":"<0|0|106896>"}],["entity3","entity3",{"ENTITY":"<0|0|106897>"}],["entity4","entity4",{"ENTITY":"<0|0|106898>"}]]}


    Returns
    _______
    AvInterchange
        All properties in registry as an AvInterchange JSON string

    """
    return properties.retrieve_properties(entity=registry, authorization=authorization)
