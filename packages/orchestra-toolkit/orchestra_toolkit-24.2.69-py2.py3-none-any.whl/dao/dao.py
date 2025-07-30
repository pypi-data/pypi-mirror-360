""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from __future__ import annotations
import json
import multiprocessing
import random
import string
import traceback
from abc import abstractmethod
from enum import IntEnum
from queue import Queue
from threading import Thread, Lock
from typing import List, Dict, Tuple
from treelib import Tree
import avesterra.facets as facets
import avesterra.factors as factors
import avesterra.facts as facts
import avesterra.features as features
import avesterra.objects as objects
import avesterra.predefined as predefined
import avesterra.registries as registries
from avesterra.avesterra import (
    AvAuthorization,
    AvEntity,
    EntityError,
    AuthorizationError,
)
from avesterra.avial import (
    NULL_ENTITY,
    NULL_NAME,
    NULL_KEY,
    NULL_CONTEXT,
    NULL_CLASS,
    NULL_CATEGORY,
    NULL_AUTHORIZATION,
    create_entity,
    change_entity,
    purge_data,
    retrieve_entity,
    AvValue,
    NULL_VALUE,
    AvEncodable,
    purge_entity,
    AvKey,
    AvName,
)
from avesterra.taxonomy import (
    AvContext,
    AvClass,
    AvCategory,
    AvState,
    AvAttribute,
    AvTag,
)
from orchestra.utils import set_entity_update_time
import avesterra.avial as av


class DAOOperationType(IntEnum):
    SAVE = (1,)
    LOAD = (2,)
    RETRIEVE = 3


class DAOJob:
    task_count: int
    task_count_lock: Lock

    job_id: str

    exceptions: Dict[str, str]
    job_access_lock: Lock

    def __init__(self, job_id: str):
        self.job_id = job_id

        self.task_count = 0

        self.task_count_lock = Lock()
        self.job_access_lock = Lock()

        self.exceptions = {}

    def increment_by(self, delta: int):
        self.task_count_lock.acquire()

        self.task_count += delta

        self.task_count_lock.release()

    def append_traceback(self, exception: Exception):
        # Save Exception/Traceback to results
        self.exceptions[str(exception)] = traceback.format_exc()

    def decrement(self):
        self.task_count_lock.acquire()

        self.task_count -= 1

        self.task_count_lock.release()


class AvialModel:
    object: DAOObject

    def __init__(self, object: DAOObject):
        assert isinstance(object, DAOObject)
        self.object = object

    def retrieve(self):
        self.object = self.object.retrieve()
        return self

    def save(self):
        self.object = self.object.save()
        return self

    def tree(self) -> Tree:
        return self.object.tree()

    def entity(self) -> AvEntity:
        return self.object.get_entity()


class DAOAvialModelNode:
    _dao: DAOAvialApplicator

    def __init__(self, dao: DAOAvialApplicator):
        self._dao = dao

    @abstractmethod
    def _apply(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        pass

    @abstractmethod
    def _fetch(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        pass

    @abstractmethod
    def _retrieve(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        pass

    @abstractmethod
    def _instantiate(self, auth: AvAuthorization) -> None:
        pass

    @abstractmethod
    def _has_changed(self) -> bool:
        pass

    @abstractmethod
    def _set_changed(self, changed: bool = True) -> None:
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def retrieve(self):
        pass

    @abstractmethod
    def back(self):
        pass

    @abstractmethod
    def _tree(self, tree: Tree, ident: str, parent: str = None) -> Tree:
        pass

    def tree(self, tree: Tree = None, parent: str = None) -> Tree:
        if tree is None:
            # Create root tree
            tree = Tree()

        # Generate random id
        ident: str = "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(0, 16)]
        )

        # Implementers choice
        self._tree(tree, ident, parent)

        return tree


class DAOAvialApplicator:
    auth: AvAuthorization
    worker_count: int

    dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]]

    job_mapping: Dict[str, DAOJob]

    workers: List[Thread]

    class Worker:
        auth: AvAuthorization
        job_mapping: Dict[str, DAOJob]

        def __init__(self, auth: AvAuthorization, job_mapping: Dict[str, DAOJob]):
            self.auth = auth
            self.job_mapping = job_mapping

        def start(
            self, dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]]
        ):
            while True:
                request = dao_queue.get()

                if request is None:
                    break
                else:
                    job_id, avial_node, avial_node_type = request
                    try:
                        if avial_node_type == DAOOperationType.SAVE:
                            avial_node._apply(
                                auth=self.auth,
                                dao_queue=dao_queue,
                                job_id=job_id,
                                job_mapping=self.job_mapping,
                            )
                        elif avial_node_type == DAOOperationType.LOAD:
                            avial_node._fetch(
                                auth=self.auth,
                                dao_queue=dao_queue,
                                job_id=job_id,
                                job_mapping=self.job_mapping,
                            )
                        elif avial_node_type == DAOOperationType.RETRIEVE:
                            avial_node._retrieve(
                                auth=self.auth,
                                dao_queue=dao_queue,
                                job_id=job_id,
                                job_mapping=self.job_mapping,
                            )
                    except Exception as e:
                        print(f"TASK APPLICATION ERROR: {traceback.format_exc()}")

                        # Append traceback/exception to results
                        self.job_mapping[job_id].append_traceback(e)

                    finally:
                        # Decrement the number of jobs being worked on
                        self.job_mapping[job_id].decrement()

                        # Unlock double-locked blocked thread
                        if self.job_mapping[job_id].task_count == 0:
                            # Unlock blocked thread
                            self.job_mapping[job_id].job_access_lock.release()

            return 0

    def __init__(self, auth: AvAuthorization, worker_count: int, dao_queue: Queue):
        self.auth = auth
        self.worker_count = worker_count
        self._dao_queue = dao_queue

        self.workers = []
        self.job_mapping = {}

        # Create and start workers
        for i in range(0, self.worker_count):
            # Create worker
            worker: DAOAvialApplicator.Worker = DAOAvialApplicator.Worker(
                auth=self.auth, job_mapping=self.job_mapping
            )

            # Create worker
            worker_thread: Thread = Thread(target=worker.start, args=(self._dao_queue,))

            # Add worker process to pool
            self.workers.append(worker_thread)

            # Start worker process
            worker_thread.start()

    def stop(self):
        # Submit poison pill to all workers
        for i in range(0, self.worker_count):
            self._dao_queue.put(None)

        # Wait for all workers to return
        # before exiting, to prevent zombification
        for i in range(0, self.worker_count):
            self.workers[i].join()

        # Gracefully terminate
        return 0

    def save(self, avial_node: DAOAvialModelNode):
        self.run(avial_node=avial_node, avial_node_type=DAOOperationType.SAVE)

    def load(self, avial_node: DAOAvialModelNode):
        self.run(avial_node=avial_node, avial_node_type=DAOOperationType.LOAD)

    def retrieve(self, avial_node: DAOAvialModelNode):
        self.run(avial_node=avial_node, avial_node_type=DAOOperationType.RETRIEVE)

    def run(
        self, avial_node: DAOAvialModelNode, avial_node_type: DAOOperationType
    ) -> multiprocessing.Lock:
        # Generate random string for job mapping
        job_id: str = "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(0, 32)]
        )

        # Setup mapping for job
        self.job_mapping[job_id] = DAOJob(job_id=job_id)

        # Bring task count ot 1
        self.job_mapping[job_id].increment_by(1)

        # Acquire job access lock
        self.job_mapping[job_id].job_access_lock.acquire()

        # Submit job to queue
        self._dao_queue.put((job_id, avial_node, avial_node_type))

        # If avial_node is entity, then set the last_update
        # timestamp on the entity
        if isinstance(avial_node, DAOEntity):
            # Set update time
            set_entity_update_time(entity=avial_node.get_entity(), auth=self.auth)

        # Acquire job access lock again to become deadlocked
        # until the DAO resolves all tasks that are generated from
        # the given job
        self.job_mapping[job_id].job_access_lock.acquire()

        # Get Exceptions
        if len(self.job_mapping[job_id].exceptions.keys()) > 0:
            exceptions_str: str = ""

            i = 1

            # Append Exceptions to an Exception
            for exception_trace in self.job_mapping[job_id].exceptions.values():
                exceptions_str += f"<=============================================# EXCEPTION {i} - START #=============================================>\n"
                exceptions_str += exception_trace
                exceptions_str += f"<=============================================# EXCEPTION {i} - END #=============================================>\n"

                i += 1

            raise Exception(exceptions_str)

        # Delete job from job_mapping table
        del self.job_mapping[job_id]


class DAOEntity(DAOAvialModelNode):
    _entity: AvEntity

    _name: str
    _key: str
    _context: AvContext
    _klass: AvClass
    _category: AvCategory
    _state: AvState
    _authority: AvAuthorization

    _outlet: AvEntity

    _changed: bool

    # connections     : List[]
    # subscriptions   : List[]

    def __init__(
        self,
        dao: DAOAvialApplicator,
        entity: AvEntity = NULL_ENTITY,
        name: str = NULL_NAME,
        key: str = NULL_KEY,
        context: AvContext = NULL_CONTEXT,
        klass: AvClass = NULL_CLASS,
        category: AvCategory = NULL_CATEGORY,
        authority: AvAuthorization = NULL_AUTHORIZATION,
        outlet: AvEntity = NULL_ENTITY,
    ):
        super().__init__(dao)

        self._name = name
        self._key = (
            name.lower().replace(" ", "_")
            if (key is None or key == "") and name is not None and name != ""
            else key
        )  # key if key is not None and key != "" else
        self._context = context
        self._klass = klass
        self._category = category
        self._entity = entity
        self._authority = authority
        self._outlet = outlet
        self._changed = False

    def _instantiate(self, auth: AvAuthorization):
        if self._entity == NULL_ENTITY:
            entity: AvEntity
            if self._outlet == predefined.object_outlet:
                # Create Object
                entity = objects.create_object(
                    name=self._name,
                    key=self._key,
                    context=self._context,
                    klass=self._klass,
                    category=self._category,
                    authorization=auth,
                )
            elif self._outlet == predefined.registry_outlet:
                # Create registry
                entity = registries.create_registry(
                    name=self._name, key=self._key, authorization=auth
                )
            else:
                # Create "normal" entity
                entity = create_entity(
                    name=self._name,
                    key=self._key,
                    context=self._context,
                    klass=self._klass,
                    category=self._category,
                    authorization=auth,
                )
            self._entity = entity

    def get_entity(self) -> AvEntity:
        return self._entity

    def set_name(self, name: AvName) -> None:
        if not isinstance(name, str):
            raise ValueError(
                f"Error: Argument `name` must be of type str; found type {type(name)} instead"
            )
        elif name == "":
            raise ValueError(f"Error: Argument `name` cannot be an empty string")
        elif len(name) > 254:
            raise ValueError(
                f"Error: Argument `name` cannot be a string whose length is greater than 254 characters"
            )
        self._set_changed()
        self._name = name

    def get_name(self) -> AvName:
        return self._name

    def set_key(self, key: AvKey) -> None:
        if not isinstance(key, str):
            raise ValueError(
                f"Error: Argument `key` must be of type str; found type {type(key)} instead"
            )
        elif key == "":
            raise ValueError(f"Error: Argument `key` cannot be an empty string")
        elif len(key) > 254:
            raise ValueError(
                f"Error: Argument `key` cannot be a string whose length is greater than 254 characters"
            )
        self._set_changed()
        self._key = key

    def get_key(self) -> AvKey:
        return self._key

    def set_context(self, context: AvContext) -> None:
        if not isinstance(context, AvContext):
            raise ValueError(
                f"Error: Argument `context` must be of type AvContext; found type {type(context)} instead"
            )
        self._set_changed()
        self._context = context

    def get_context(self) -> AvContext:
        return self._context

    def set_klass(self, klass: AvClass) -> None:
        if not isinstance(klass, AvClass):
            raise ValueError(
                f"Error: Argument `klass` must be of type AvContext; found type {type(klass)} instead"
            )
        self._set_changed()
        self._klass = klass

    def get_klass(self) -> AvClass:
        return self._klass

    def set_category(self, category: AvCategory) -> None:
        if not isinstance(category, AvCategory):
            raise ValueError(
                f"Error: Argument `category` must be of type AvCategory; found type {type(category)} instead"
            )
        self._set_changed()
        self._category = category

    def get_category(self) -> AvCategory:
        return self._category

    def set_authority(self, authority: AvAuthorization) -> None:
        self._set_changed()
        self._authority = authority

    def get_authority(self) -> AvAuthorization:
        return self._authority

    def _apply(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        entity_created: bool = False

        # If entity wasn't specified, then create a new one
        if self._entity == NULL_ENTITY:
            self._instantiate(auth=auth)
            entity_created = True

        if self._changed and entity_created == False:
            # If authority needs to change, or the entity wasn't freshly created
            # then execute change_entity
            if self._authority != auth or entity_created == False:
                # Apply changes to entity
                change_entity(
                    entity=self._entity,
                    authorization=auth,
                    name=self._name,
                    key=self._key,
                    context=self._context,
                    klass=self._klass,
                    category=self._category,
                    authority=self._authority,
                )

    def _fetch(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        pass

    def _retrieve(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        self._key = av.entity_key(entity=self._entity, authorization=self._authority)
        self._name = av.entity_name(entity=self._entity, authorization=self._authority)
        self._context = av.entity_context(
            entity=self._entity, authorization=self._authority
        )
        self._klass = av.entity_class(
            entity=self._entity, authorization=self._authority
        )
        self._category = av.entity_category(
            entity=self._entity, authorization=self._authority
        )

    def _has_changed(self) -> bool:
        return self._changed

    def _set_changed(self, changed: bool = True) -> None:
        self._changed = changed

    def save(self) -> DAOEntity:
        self._dao.save(self)
        return self

    def load(self) -> DAOEntity:
        self._dao.load(self)
        return self

    def retrieve(self) -> DAOEntity:
        self._dao.retrieve(self)
        return self

    def back(self) -> DAOEntity:
        return self

    def _tree(self, tree: Tree, ident: str, parent: str = None):
        tree.create_node(tag=str(self.get_entity()), identifier=ident, parent=parent)
        return tree


class DAOObject(DAOEntity, DAOAvialModelNode):
    _facts: Dict[str, DAOFact]

    entity_data: Dict

    _purge: bool

    def __init__(
        self,
        dao: DAOAvialApplicator,
        entity: AvEntity = NULL_ENTITY,
        name: str = NULL_NAME,
        key: str = NULL_KEY,
        context: AvContext = NULL_CONTEXT,
        klass: AvClass = NULL_CLASS,
        category: AvCategory = NULL_CATEGORY,
        authority: AvAuthorization = NULL_AUTHORIZATION,
    ):
        super().__init__(
            dao=dao,
            entity=entity,
            name=name,
            key=key,
            context=context,
            klass=klass,
            category=category,
            authority=authority,
            outlet=predefined.object_outlet,
        )

        self._purge = False
        self._facts = {}
        self.entity_data = {}

    def fact_exists(self, attribute: AvAttribute) -> bool:
        return attribute.name in self._facts.keys()

    def facts(self) -> List[DAOFact]:
        return list(self._facts.values())

    def fact(self, attribute: AvAttribute) -> DAOFact:
        if not isinstance(attribute, AvAttribute):
            raise ValueError(
                f"Error: Argument `attribute` must be of type AvAttribute; found type {type(attribute)} instead"
            )

        if attribute.name not in self._facts.keys():
            self._facts[attribute.name] = DAOFact(
                dao=self._dao, obj=self, attribute=attribute
            )
        return self._facts[attribute.name]

    def back(self) -> DAOObject:
        return self

    def purge(self) -> DAOObject:
        self._purge = True
        return self

    def _instantiate(self, auth: AvAuthorization):
        super()._instantiate(auth=auth)

    def _apply(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        # Call entity _apply first
        super()._apply(
            auth=auth, dao_queue=dao_queue, job_id=job_id, job_mapping=job_mapping
        )

        if self._purge and self.get_entity() != NULL_ENTITY:
            purge_data(entity=self.get_entity(), authorization=auth)

        self._instantiate(auth=auth)

        # Increment job id task count by n
        job_mapping[job_id].increment_by(len(self._facts))

        # Put Facts into DAO queue
        for fact_key in self._facts.keys():
            dao_queue.put((job_id, self._facts[fact_key], DAOOperationType.SAVE))

    def _fetch(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        # Perform entity _fetch
        super()._fetch(
            auth=auth, dao_queue=dao_queue, job_id=job_id, job_mapping=job_mapping
        )

        if self.get_entity() == NULL_ENTITY:
            raise Exception(
                f"Error: Attempted to fetch fields of the null entity({str(self.get_entity())})"
            )

        # Increment job id task count by n
        job_mapping[job_id].increment_by(len(self._facts))

        # Put Facts into DAO queue
        for fact_key in self._facts.keys():
            dao_queue.put((job_id, self._facts[fact_key], DAOOperationType.LOAD))

    def _retrieve(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ) -> DAOObject:
        # Call entity _retrieve first
        super()._retrieve(
            auth=auth, dao_queue=dao_queue, job_id=job_id, job_mapping=job_mapping
        )

        if self.get_entity() == NULL_ENTITY:
            raise Exception(
                f"Error: Attempted to retrieve the null entity({str(self.get_entity())})"
            )

        # JSON string
        object_json_string = retrieve_entity(
            entity=self.get_entity(), authorization=auth
        ).decode_interchange()

        object_json_string = object_json_string

        try:
            object_json = json.loads(object_json_string)
        except Exception as e:
            raise Exception(
                f"Error: Failed to parse retrieved JSON for {self.get_entity()}: {e}"
            )

        # Retrieve avial object data
        self.entity_data = object_json["Facts"] if "Facts" in object_json.keys() else []

        # Populate Facts
        for (
            attribute_str,
            value_json,
            facets,
            features,
            frames,
            fields,
        ) in self.entity_data:
            # Parse Attribute name
            attribute: AvAttribute = AvAttribute[attribute_str.split("_")[0]]

            # Create Fact from attribute and value
            self._facts[str(attribute.name)] = DAOFact(
                dao=self._dao,
                obj=self,
                attribute=attribute,
                value=AvValue.from_json(value_json),
                facets_data=facets,
                features_data=features,
            )

        # Increment job id task count by n
        job_mapping[job_id].increment_by(len(self._facts))

        # Put Facts into DAO queue
        for fact_key in self._facts.keys():
            dao_queue.put((job_id, self._facts[fact_key], DAOOperationType.RETRIEVE))

    def _has_changed(self) -> bool:
        return self._changed

    def _set_changed(self, changed: bool = True) -> None:
        self._changed = changed

    def save(self) -> DAOObject:
        self._dao.save(self)
        return self

    def load(self) -> DAOObject:
        self._dao.load(self)
        return self

    def retrieve(self) -> DAOObject:
        self._dao.retrieve(self)
        return self

    def _tree(self, tree: Tree, ident: str, parent: str = None):
        super()._tree(tree, ident, parent)

        # Facts are children
        for fact in self._facts.values():
            fact.tree(tree, ident)
        return tree


class DAOFact(DAOAvialModelNode):
    _object: DAOObject
    _attribute: AvAttribute
    value: AvValue

    _facets: Dict[str, DAOFacet]
    _features: Dict[str, DAOFeature]

    _purge: bool

    _purge_facets: bool
    _purge_features: bool
    _purge_table: bool

    _fetch_value: bool

    _facets_data: Dict
    _features_data: Dict

    _changed: bool

    def __init__(
        self,
        dao: DAOAvialApplicator,
        obj: DAOObject,
        attribute: AvAttribute,
        value: AvValue = None,
        facets_data: Dict = None,
        features_data: Dict = None,
        fields_data: Dict = None,
        frames_data: Dict = None,
    ):
        super().__init__(dao)

        if not isinstance(attribute, AvAttribute):
            raise ValueError(
                f"Error: Argument `attribute` must be of type AvAttribute; found type {type(attribute)} instead"
            )

        self._object = obj
        self._attribute = attribute

        self._facets = {}
        self._features = {}

        self.value = value

        self._purge = False
        self._purge_facets = False
        self._purge_features = False
        self._purge_table = False

        self._fetch_value = False

        self._changed = False

        self._facets_data = facets_data if facets_data is not None else {}
        self._features_data = features_data if features_data is not None else {}

    def object(self) -> DAOObject:
        return self._object

    def attribute(self) -> AvAttribute:
        return self._attribute

    def back(self) -> DAOObject:
        return self._object

    def facet_exists(self, facet: str):
        return facet in self._facets.keys()

    def feature_exists(self, key: str):
        return key in self._features.keys()

    def include(self, value: AvEncodable | AvValue) -> DAOFact:
        if not isinstance(value, AvValue):
            if not isinstance(value, AvEncodable):
                raise ValueError(
                    f"Error: Argument `value` must be of type AvEncodable; found type {type(value)} instead"
                )
            value = AvValue.encode(value)
        self._set_changed()
        self.value = value
        return self

    def exclude(self) -> DAOFact:
        self._set_changed()
        self.value = None
        return self

    def clear(self) -> DAOFact:
        self._set_changed()
        self.value = NULL_VALUE
        return self

    def purge(self) -> DAOFact:
        self._set_changed()

        # Purge attribute clears all of these,
        # hence there is no need to purge
        # each individually
        self._purge_facets = True
        self._purge_features = True
        self._purge_table = True

        # Purge data
        self._facets = {}
        self._features = {}

        return self

    def facet(self, name: str) -> DAOFacet:
        if not isinstance(name, str):
            raise ValueError(
                f"Error: Argument `name` must be of type str; found type {type(name)} instead"
            )
        elif name == "":
            raise ValueError(f"Error: Argument `name` cannot be an empty string")
        elif len(name) > 254:
            raise ValueError(
                f"Error: Argument `name` cannot be a string whose length is greater than 254 characters"
            )

        if name not in self._facets.keys():
            self._facets[name] = DAOFacet(
                dao=self._dao, object=self._object, fact=self, name=name
            )

        return self._facets[name]

    def facets(self) -> List[DAOFacet]:
        return list(self._facets.values())

    def feature(self, key: str, name: str = "") -> DAOFeature:
        if not isinstance(name, str):
            raise ValueError(
                f"Error: Argument `name` must be of type str; found type {type(name)} instead"
            )
        elif len(name) > 254:
            raise ValueError(
                f"Error: Argument `name` cannot be a string whose length is greater than 254 characters"
            )

        if not isinstance(key, str):
            raise ValueError(
                f"Error: Argument `key` must be of type str; found type {type(key)} instead"
            )
        elif key == "":
            raise ValueError(f"Error: Argument `key` cannot be an empty string")
        elif len(key) > 254:
            raise ValueError(
                f"Error: Argument `key` cannot be a string whose length is greater than 254 characters"
            )

        if key not in self._features.keys():
            self._features[key] = DAOFeature(
                dao=self._dao, object=self._object, fact=self, name=name, key=key
            )
        return self._features[key]

    def features(self) -> List[DAOFeature]:
        return list(self._features.values())

    def table(self):
        pass

    def _instantiate(self, auth: AvAuthorization):
        # Do not overwrite a "Real Value" with a NULL value
        # Only allow None
        if self.value is not None or (
            self.value is None
            and facts.get_fact(
                entity=self._object.get_entity(),
                attribute=self._attribute,
                authorization=auth,
            )
            == NULL_VALUE
        ):
            try:
                facts.include_fact(
                    entity=self._object.get_entity(),
                    attribute=self._attribute,
                    value=self.value
                    if self.value is not None
                    else NULL_VALUE,  # None is not a valid value, NULL_VALUE is a good substitute
                    authorization=auth,
                )
            except EntityError as ee:
                raise Exception(f"Entity {self._object.get_entity()} not found")

    def _apply(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        # Purge facets on fact if set
        if self._purge_facets:
            facets.purge_facets(
                entity=self._object.get_entity(),
                attribute=self._attribute,
                authorization=auth,
            )
            self._purge_facets = False

        # Purge features on fact if set
        if self._purge_features:
            features.purge_features(
                entity=self._object.get_entity(),
                attribute=self._attribute,
                authorization=auth,
            )
            self._purge_features = False

        if self._purge_table:
            self._purge_table = False

        if self._has_changed():
            if self.value is not None:
                # Only set Fact value if self.value is not None
                self._instantiate(auth=auth)
            else:
                # If value is None and state has changed,
                # then assume exclusion
                facts.exclude_fact(
                    entity=self._object.get_entity(),
                    attribute=self._attribute,
                    authorization=auth,
                )
            self._set_changed(False)

        # Increment job id task count by n
        job_mapping[job_id].increment_by(len(self._facets) + len(self._features))

        # Add facets to DAO queue
        for facet_key in self._facets.keys():
            dao_queue.put((job_id, self._facets[facet_key], DAOOperationType.SAVE))

        # Add features to DAO queue
        for feature_key in self._features.keys():
            dao_queue.put((job_id, self._features[feature_key], DAOOperationType.SAVE))

    def _fetch(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        if self._fetch_value:
            self.value = facts.get_fact(
                entity=self._object.get_entity(),
                attribute=self._attribute,
                authorization=auth,
            )

        # Increment job id task count by n
        job_mapping[job_id].increment_by(len(self._facets) + len(self._features))

        # Add facets to DAO queue
        for facet_key in self._facets.keys():
            dao_queue.put((job_id, self._facets[facet_key], DAOOperationType.LOAD))

        # Add features to DAO queue
        for feature_key in self._features.keys():
            dao_queue.put((job_id, self._features[feature_key], DAOOperationType.LOAD))

    def _retrieve(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        # Iterate over json facets
        for facet_str, facet_value_json, factors_data in self._facets_data:
            # Create Facet from facet str and parsed value
            self._facets[facet_str] = DAOFacet(
                dao=self._dao,
                object=self.object(),
                fact=self,
                name=facet_str,
                value=AvValue.from_json(facet_value_json),
                factors_data=factors_data,
            )

        # Iterate over json features
        for name, key, feature_value_json in self._features_data:
            # Create Feature from name, key, and parsed value
            self._features[key] = DAOFeature(
                dao=self._dao,
                object=self.object(),
                fact=self,
                name=name,
                key=key,
                value=AvValue.from_json(feature_value_json),
            )

        # Increment job id task count by n
        job_mapping[job_id].increment_by(len(self._facets) + len(self._features))

        # Add facets to DAO queue
        for facet_key in self._facets.keys():
            dao_queue.put((job_id, self._facets[facet_key], DAOOperationType.RETRIEVE))

        # Add features to DAO queue
        for feature_key in self._features.keys():
            dao_queue.put(
                (job_id, self._features[feature_key], DAOOperationType.RETRIEVE)
            )

    def _has_changed(self) -> bool:
        return self._changed

    def _set_changed(self, changed: bool = True) -> None:
        self._changed = changed

    def save(self) -> DAOObject:
        self._dao.save(self._object)
        return self._object

    def load(self) -> DAOObject:
        self._dao.load(self._object)
        return self._object

    def retrieve(self) -> DAOObject:
        self._dao.retrieve(self._object)
        return self._object

    def fetch(self, fetch_value: bool = True) -> DAOFact:
        self._fetch_value = fetch_value
        return self

    def _tree(self, tree: Tree, ident: str, parent: str = None):
        # Create node
        tree.create_node(
            f"[{self._attribute.name}] => "
            + "{ "
            + f"'{self.value.tag().name if self.value is not None else AvTag.NULL.name}'"
            + " : "
            + f"'{str(self.value.decode()) if self.value is not None else str(NULL_VALUE)}'"
            + " }",
            ident,
            parent,
        )

        # Facts are children
        for facet in self._facets.values():
            facet.tree(tree, ident)

        # Facts are children
        for feature in self._features.values():
            feature.tree(tree, ident)

        return tree


class DAOFacet(DAOAvialModelNode):
    _object: DAOObject
    _fact: DAOFact
    _name: str

    _factors: Dict[str, DAOFactor]

    value: AvValue

    _purge: bool

    _purge_factors: bool

    _fetch_value: bool

    _changed: bool

    _factors_data: Dict

    def __init__(
        self,
        dao: DAOAvialApplicator,
        object: DAOObject,
        fact: DAOFact,
        name: str,
        value: AvValue = None,
        factors_data: Dict = None,
    ):
        super().__init__(dao)

        if not isinstance(name, str):
            raise ValueError(
                f"Error: Argument `name` must be of type str; found type {type(name)} instead"
            )
        elif name == "":
            raise ValueError(f"Error: Argument `name` cannot be an empty string")
        elif len(name) > 254:
            raise ValueError(
                f"Error: Argument `name` cannot be a string whose length is greater than 254 characters"
            )

        self._object = object

        self._fact = fact
        self._name = name

        self._factors = {}

        self.value = value

        self._purge = False
        self._purge_factors = False
        self._fetch_value = False
        self._changed = False

        self._factors_data = factors_data if factors_data is not None else {}

    def object(self) -> DAOObject:
        return self._object

    def fact(self) -> DAOFact:
        return self._fact

    def name(self) -> str:
        return self._name

    def factor_exists(self, factor: str) -> bool:
        return factor in self._factors.keys()

    def factor(self, key: str) -> DAOFactor:
        if not isinstance(key, str):
            raise ValueError(
                f"Error: Argument `key` must be of type str; found type {type(key)} instead"
            )
        elif key == "":
            raise ValueError(f"Error: Argument `key` cannot be an empty string")
        elif len(key) > 254:
            raise ValueError(
                f"Error: Argument `key` cannot be a string whose length is greater than 254 characters"
            )

        if key not in self._factors.keys():
            self._factors[key] = DAOFactor(
                dao=self._dao,
                object=self.object(),
                fact=self.fact(),
                facet=self,
                key=key,
            )
        return self._factors[key]

    def factors(self) -> List[DAOFactor]:
        return list(self._factors.values())

    def back(self) -> DAOFact:
        return self._fact

    def include(self, value: AvEncodable | AvValue) -> DAOFacet:
        if not isinstance(value, AvValue):
            if not isinstance(value, AvEncodable):
                raise ValueError(
                    f"Error: Argument `value` must be of type AvEncodable; found type {type(value)} instead"
                )
            value = AvValue.encode(value)
        self._set_changed()
        self.value = value
        return self

    def exclude(self):
        self._set_changed()
        self.value = None

    def clear(self) -> DAOFacet:
        self._set_changed()
        self.value = NULL_VALUE
        return self

    def purge(self) -> DAOFacet:
        self._set_changed()
        self._purge = True

        # Purge attribute clears all of these,
        # hence there is no need to purge
        # each individually
        self._purge_factors = False

        self._factors = {}

        return self

    def _instantiate(self, auth: AvAuthorization):
        # Do not overwrite a "Real Value" with a NULL value
        # Only allow None
        if self.value is not None or (
            self.value is None
            and facets.get_facet(
                entity=self._object.get_entity(),
                attribute=self._fact.attribute(),
                name=self._name,
                authorization=auth,
            )
            == NULL_VALUE
        ):
            try:
                facets.include_facet(
                    entity=self._object.get_entity(),
                    attribute=self._fact.attribute(),
                    name=self._name,
                    value=self.value
                    if self.value is not None
                    else NULL_VALUE,  # None is not a valid value, NULL_VALUE is a good substitute
                    authorization=auth,
                )
            except EntityError as ee:
                raise Exception(f"Entity {self._object.get_entity()} not found")
            except Exception as e:
                error_str: str = traceback.format_exc()
                if "Server reported AUTHORIZATION error" in error_str:
                    raise AuthorizationError(
                        f"Not authorized to include facet of name {self.name()} on Fact {self._fact.attribute().name} on entity {self._object.get_entity()}"
                    )
                elif "not found" in error_str:
                    # Attempt to instantiate parent fact
                    self._fact._instantiate(auth=auth)

                    # Try facet include again
                    facets.include_facet(
                        entity=self._object.get_entity(),
                        attribute=self._fact.attribute(),
                        name=self._name,
                        value=self.value
                        if self.value is not None
                        else NULL_VALUE,  # None is not a valid value, NULL_VALUE is a good substitute
                        authorization=auth,
                    )
                else:
                    raise e

    def _apply(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        if self._has_changed():
            if self.value is not None:
                # Only set Facet value if self.value is not None
                self._instantiate(auth=auth)
            else:
                # If value is None and state has changed,
                # then assume exclusion
                facets.exclude_facet(
                    entity=self._object.get_entity(),
                    attribute=self._fact.attribute(),
                    name=self._name,
                    authorization=auth,
                )
            self._set_changed(False)

        if self._purge_factors:
            factors.purge_factors(
                entity=self._object.get_entity(),
                attribute=self._fact.attribute(),
                name=self._name,
                authorization=auth,
            )
            self._purge_factors = False

        # Increment job id task count by n
        job_mapping[job_id].increment_by(len(self._factors))

        # Add factors to DAO queue
        for factor_key in self._factors.keys():
            dao_queue.put((job_id, self._factors[factor_key], DAOOperationType.SAVE))

    def _fetch(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        if self._fetch_value:
            self.value = facets.get_facet(
                entity=self._object.get_entity(),
                attribute=self._fact.attribute(),
                name=self._name,
                authorization=auth,
            )
        # Increment job id task count by n
        job_mapping[job_id].increment_by(len(self._factors))

        # Add factors to DAO queue
        for factor_key in self._factors.keys():
            dao_queue.put((job_id, self._factors[factor_key], DAOOperationType.LOAD))

    def _retrieve(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        # Iterate over json factors
        for key, factor_value_json in self._factors_data:
            # Create Feature from name, key, and parsed value
            self._factors[key] = DAOFactor(
                dao=self._dao,
                object=self.object(),
                fact=self.fact(),
                facet=self,
                key=key,
                value=AvValue.from_json(factor_value_json),
            )
        # Increment job id task count by n
        job_mapping[job_id].increment_by(len(self._factors))

        # Add factors to DAO queue
        for factor_key in self._factors.keys():
            dao_queue.put(
                (job_id, self._factors[factor_key], DAOOperationType.RETRIEVE)
            )

    def _has_changed(self) -> bool:
        return self._changed

    def _set_changed(self, changed: bool = True) -> None:
        self._changed = changed

    def save(self) -> DAOObject:
        self._dao.save(self._object)
        return self._object

    def load(self) -> DAOObject:
        self._dao.load(self._object)
        return self._object

    def retrieve(self) -> DAOObject:
        self._dao.retrieve(self._object)
        return self._object

    def fetch(self, fetch_value: bool = True) -> DAOFacet:
        self._fetch_value = fetch_value
        return self

    def _tree(self, tree: Tree, ident: str, parent: str = None):
        # Create node
        tree.create_node(
            f"({self._name}) => "
            + "{ "
            + f"'{self.value.tag().name if self.value is not None else AvTag.NULL.name}'"
            + " : "
            + f"'{str(self.value.decode()) if self.value is not None else str(NULL_VALUE)}'"
            + " }",
            ident,
            parent,
        )

        # Facts are children
        for factor in self._factors.values():
            factor.tree(tree, ident)

        return tree


class DAOFactor(DAOAvialModelNode):
    _object: DAOObject
    _fact: DAOFact
    _facet: DAOFacet
    _key: str

    value: AvValue

    _fetch_value: bool

    _changed: bool

    _data: Dict

    def __init__(
        self,
        object: DAOObject,
        fact: DAOFact,
        facet: DAOFacet,
        key: str,
        dao: DAOAvialApplicator,
        value: AvValue = None,
    ):
        super().__init__(dao)

        if not isinstance(key, str):
            raise ValueError(
                f"Error: Argument `key` must be of type str; found type {type(key)} instead"
            )
        elif key == "":
            raise ValueError(f"Error: Argument `key` cannot be an empty string")
        elif len(key) > 254:
            raise ValueError(
                f"Error: Argument `key` cannot be a string whose length is greater than 254 characters"
            )

        self._object = object
        self._fact = fact
        self._facet = facet
        self._key = key

        self.value = value

        self._fetch_value = False

        self._changed = False

    def object(self) -> DAOObject:
        return self._object

    def fact(self) -> DAOFact:
        return self._fact

    def facet(self) -> DAOFacet:
        return self._facet

    def key(self) -> str:
        return self._key

    def back(self) -> DAOFacet:
        return self._facet

    def include(self, value: AvEncodable | AvValue) -> DAOFactor:
        if not isinstance(value, AvValue):
            if not isinstance(value, AvEncodable):
                raise ValueError(
                    f"Error: Argument `value` must be of type AvEncodable; found type {type(value)} instead"
                )
            value = AvValue.encode(value)
        self._set_changed()
        self.value = value
        return self

    def exclude(self) -> DAOFactor:
        self._set_changed()
        self.value = None
        return self

    def clear(self) -> DAOFactor:
        self._set_changed()
        self.value = NULL_VALUE
        return self

    def _instantiate(self, auth: AvAuthorization):
        try:
            factors.include_factor(
                entity=self._object.get_entity(),
                attribute=self._fact.attribute(),
                name=self._facet.name(),
                key=self._key,
                value=self.value,
                authorization=auth,
            )
        except EntityError as ee:
            raise Exception(f"Entity {self._object.get_entity()} not found")
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to include facet of name {self._facet.name()} on Fact {self._fact.attribute().name} on entity {self._object.get_entity()}"
                )
            elif "not found" in error_str:
                # Attempt to instantiate parent facet(facet cannot be set without fact)
                self._facet._instantiate(auth=auth)

                # Try factor include again
                factors.include_factor(
                    entity=self._object.get_entity(),
                    attribute=self._fact.attribute(),
                    name=self._facet.name(),
                    key=self._key,
                    value=self.value
                    if self.value is not None
                    else NULL_VALUE,  # None is not a valid value, NULL_VALUE is a good substitute
                    authorization=auth,
                )
            else:
                raise e

    def _apply(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        if self._has_changed():
            if self.value is not None:
                # Only set Factor value if self.value is not None
                self._instantiate(auth=auth)
            else:
                # If value is None and state has changed,
                # then assume exclusion
                factors.exclude_factor(
                    entity=self._object.get_entity(),
                    attribute=self._fact.attribute(),
                    name=self._facet.name(),
                    key=self._key,
                    authorization=auth,
                )
            self._set_changed(False)

    def _fetch(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        if self._fetch_value:
            self.value = factors.get_factor(
                entity=self._object.get_entity(),
                attribute=self._fact.attribute(),
                name=self._facet.name(),
                key=self._key,
                authorization=auth,
            )

    def _retrieve(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        pass

    def _has_changed(self) -> bool:
        return self._changed

    def _set_changed(self, changed: bool = True) -> None:
        self._changed = changed

    def save(self) -> DAOObject:
        self._dao.save(self._object)
        return self._object

    def load(self) -> DAOObject:
        self._dao.load(self._object)
        return self._object

    def retrieve(self) -> DAOObject:
        self._dao.retrieve(self._object)
        return self._object

    def fetch(self, fetch_value: bool = True) -> DAOFactor:
        self._fetch_value = fetch_value
        return self

    def _tree(self, tree: Tree, ident: str, parent: str = None):
        # Create node
        tree.create_node(
            f"{{{self._key}}} => "
            + "{ "
            + f"'{self.value.tag().name if self.value is not None else AvTag.NULL.name}'"
            + " : "
            + f"'{str(self.value.decode()) if self.value is not None else str(NULL_VALUE)}'"
            + " }",
            ident,
            parent,
        )
        return tree


class DAOFeature(DAOAvialModelNode):
    _object: DAOObject
    _fact: DAOFact
    _key: str
    _name: str

    _fetch_value: bool

    value: AvValue

    _changed: bool

    def __init__(
        self,
        object: DAOObject,
        fact: DAOFact,
        key: str,
        dao: DAOAvialApplicator,
        value: AvValue = None,
        name: str = "",
    ):
        super().__init__(dao)

        if not isinstance(key, str):
            raise ValueError(
                f"Error: Argument `key` must be of type str; found type {type(key)} instead"
            )
        elif key == "":
            raise ValueError(f"Error: Argument `key` cannot be an empty string")
        elif len(key) > 254:
            raise ValueError(
                f"Error: Argument `key` cannot be a string whose length is greater than 254 characters"
            )

        if not isinstance(name, str):
            raise ValueError(
                f"Error: Argument `name` must be of type str; found type {type(name)} instead"
            )
        elif len(name) > 254:
            raise ValueError(
                f"Error: Argument `name` cannot be a string whose length is greater than 254 characters"
            )

        self._object = object
        self._fact = fact
        self._name = name
        self._key = key

        self._fetch_value = False

        self.value = value

        self._changed = False

    def object(self) -> DAOObject:
        return self._object

    def fact(self) -> DAOFact:
        return self._fact

    def back(self) -> DAOFact:
        return self._fact

    def include(self, value: AvEncodable | AvValue) -> DAOFeature:
        if not isinstance(value, AvValue):
            if not isinstance(value, AvEncodable):
                raise ValueError(
                    f"Error: Argument `value` must be of type AvEncodable; found type {type(value)} instead"
                )
            value = AvValue.encode(value)
        self._set_changed()
        self.value = value
        return self

    def exclude(self) -> DAOFeature:
        self._set_changed()
        self.value = None
        return self

    def clear(self) -> DAOFeature:
        self._set_changed()
        self.value = NULL_VALUE
        return self

    def _instantiate(self, auth: AvAuthorization):
        # Do not overwrite a "Real Value" with a NULL value
        # Only allow None
        if self.value is not None or (
            self.value is None
            and features.get_feature(
                entity=self._object.get_entity(),
                attribute=self._fact.attribute(),
                key=self._key,
                authorization=auth,
            )
            == NULL_VALUE
        ):
            try:
                features.include_feature(
                    entity=self._object.get_entity(),
                    attribute=self._fact.attribute(),
                    name=self._name,
                    key=self._key,
                    value=self.value
                    if self.value is not None
                    else NULL_VALUE,  # None is not a valid value, NULL_VALUE is a good substitute
                    authorization=auth,
                )
            except EntityError as ee:
                raise Exception(f"Entity {self._object.get_entity()} not found")
            except Exception as e:
                error_str: str = traceback.format_exc()
                if "Server reported AUTHORIZATION error" in error_str:
                    raise AuthorizationError(
                        f"Not authorized to include feature of key {self._key} and name {self._name} on Fact {self._fact.attribute().name} on entity {self._object.get_entity()}"
                    )
                elif "not found" in error_str:
                    # Attempt to instantiate parent fact
                    self._fact._instantiate(auth=auth)

                    # Try facet include again
                    features.include_feature(
                        entity=self._object.get_entity(),
                        attribute=self._fact.attribute(),
                        name=self._name,
                        key=self._key,
                        value=self.value
                        if self.value is not None
                        else NULL_VALUE,  # None is not a valid value, NULL_VALUE is a good substitute
                        authorization=auth,
                    )
                else:
                    raise e

    def _apply(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        if self._has_changed():
            if self.value is not None:
                # Only set Feature value if self.value is not None
                self._instantiate(auth=auth)
            else:
                # If value is None and state has changed,
                # then assume exclusion
                features.exclude_feature(
                    entity=self._object.get_entity(),
                    attribute=self._fact.attribute(),
                    key=self._key,
                    authorization=auth,
                )
            self._set_changed(False)

    def _fetch(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        if self._fetch_value:
            self.value = features.get_feature(
                entity=self._object.get_entity(),
                attribute=self._fact.attribute(),
                key=self._key,
                authorization=auth,
            )

    def _retrieve(
        self,
        auth: AvAuthorization,
        dao_queue: Queue[Tuple[str, DAOAvialModelNode, DAOOperationType]],
        job_id: str,
        job_mapping: Dict[str, DAOJob],
    ):
        pass

    def _has_changed(self) -> bool:
        return self._changed

    def _set_changed(self, changed: bool = True) -> None:
        self._changed = changed

    def save(self) -> DAOObject:
        self._dao.save(self._object)
        return self._object

    def load(self) -> DAOObject:
        self._dao.load(self._object)
        return self._object

    def retrieve(self) -> DAOObject:
        self._dao.retrieve(self._object)
        return self._object

    def fetch(self, fetch_value: bool = True):
        self._fetch_value = fetch_value
        return self

    def name(self):
        return self._name

    def key(self):
        return self._key

    def _tree(self, tree: Tree, ident: str, parent: str = None):
        # Create node
        tree.create_node(
            f"<{self._name}, {self._key}> => "
            + "{ "
            + f"'{self.value.tag().name if self.value is not None else AvTag.NULL.name}'"
            + " : "
            + f"'{str(self.value.decode()) if self.value is not None else str(NULL_VALUE)}'"
            + " }",
            ident,
            parent,
        )

        return tree
