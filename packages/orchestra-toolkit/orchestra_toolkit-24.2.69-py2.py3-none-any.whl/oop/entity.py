""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from __future__ import annotations
from avesterra import object_outlet, registry_outlet
from avesterra.avial_model import AvialModel
import avesterra.avial as avial
from avesterra.avial import (
    NULL_ENTITY,
    AvEntity,
    AvAuthorization,
)
from avesterra.taxonomy import AvContext, AvClass, AvCategory, AvMethod, AvEvent
import avesterra.objects as objects
import avesterra.registries as registries


class Entity:
    _entity: AvEntity
    _authorization: AvAuthorization
    data: AvialModel

    @staticmethod
    def create(
        authorization: AvAuthorization,
        name: str = "",
        key: str = "",
        context: AvContext = AvContext.NULL,
        klass: AvClass = AvClass.NULL,
        category: AvCategory = AvCategory.NULL,
        outlet: AvEntity = NULL_ENTITY,
    ):
        if outlet == object_outlet:
            entity = objects.create_object(
                name=name,
                key=key,
                context=context,
                klass=klass,
                category=category,
                outlet=outlet,
                authorization=authorization,
            )
        elif outlet == registry_outlet:
            entity = registries.create_registry(
                name=name,
                key=key,
                outlet=outlet,
                authorization=authorization,
            )
        else:
            entity = avial.create_entity(
                name=name,
                key=key,
                context=context,
                klass=klass,
                category=category,
                outlet=outlet,
                authorization=authorization,
            )

        _entity = Entity()
        _entity._entity = entity
        _entity._authorization = authorization

        return _entity

    @staticmethod
    def from_entity(
        entity: AvEntity, authorization: AvAuthorization, retrieve: bool = True
    ):
        _entity = Entity()
        _entity._entity = entity
        _entity._authorization = authorization

        if retrieve:
            _entity.retrieve()

    @staticmethod
    def from_data(
        entity: AvEntity,
        authorization: AvAuthorization,
        data: AvialModel,
        store: bool = False,
    ):
        _entity = Entity()
        _entity._entity = entity
        _entity._authorization = authorization
        _entity.data = data

        if store:
            _entity.store()

    def set_name(self, name: str, cache: bool = False):
        if not cache:
            avial.change_entity(
                entity=self._entity, name=name, authorization=self._authorization
            )
        else:
            self.data.name = name
        return self

    def set_key(self, key: str):
        if not key:
            avial.change_entity(
                entity=self._entity, key=key, authorization=self._authorization
            )
        else:
            self.data.key = key

        return self

    def set_class(self, klass: AvClass):
        avial.change_entity(
            entity=self._entity, klass=klass, authorization=self._authorization
        )
        return self

    def set_category(self, category: AvCategory):
        avial.change_entity(
            entity=self._entity, category=category, authorization=self._authorization
        )
        return self

    # Method stuff
    def connect_outlet(
        self,
        outlet: AvEntity = NULL_ENTITY,
        method: AvMethod = AvMethod.NULL,
        precedence: int = 0,
    ):
        avial.connect_method(
            entity=self._entity,
            outlet=outlet if outlet != NULL_ENTITY else self._entity,  # Self connect
            method=method,
            precedence=precedence,
            authorization=self._authorization,
        )
        return self

    def disconnect_outlet(
        self,
        method: AvMethod = AvMethod.NULL,
        precedence: int = 0,
    ):
        avial.disconnect_method(
            entity=self._entity,
            method=method,
            precedence=precedence,
            authorization=self._authorization,
        )
        return self

    # Subscription stuff
    def subscribe_outlet_to_event(
        self,
        outlet: AvEntity = NULL_ENTITY,
        event: AvEvent = AvEvent.NULL,
        precedence: int = 0,
    ):
        avial.subscribe_event(
            entity=self._entity,
            outlet=outlet if outlet != NULL_ENTITY else self._entity,
            event=event,
            precedence=precedence,
            authorization=self._authorization,
        )

    def unsubscribe_outlet_from_event(
        self,
        outlet: AvEntity = NULL_ENTITY,
        event: AvEvent = AvEvent.NULL,
        precedence: int = 0,
    ):
        avial.unsubscribe_event(
            entity=self._entity,
            outlet=outlet if outlet != NULL_ENTITY else self._entity,
            event=event,
            precedence=precedence,
            authorization=self._authorization,
        )

    def set_authority(
        self, new_authority: AvAuthorization, auth: AvAuthorization | None = None
    ):
        avial.change_entity(
            entity=self._entity,
            authority=new_authority,
            authorization=self._authorization if auth is None else auth,
        )

    def apply_authorization(
        self, authorization: AvAuthorization, auth: AvAuthorization | None = None
    ):
        avial.authorize_entity(
            entity=self._entity,
            authorization=self._authorization if auth is None else auth,
            authority=authorization,
        )

    def remove_authorization(
        self, authorization: AvAuthorization, auth: AvAuthorization | None = None
    ):
        avial.deauthorize_entity(
            entity=self._entity,
            authorization=self._authorization if auth is None else auth,
            authority=authorization,
        )

    def authorized(
        self, authorization: AvAuthorization, auth: AvAuthorization | None = None
    ):
        avial.entity_authorized(
            entity=self._entity,
            authorization=self._authorization if auth is None else auth,
            authority=authorization,
        )

    def activate(self, auth: AvAuthorization | None = None):
        avial.activate_entity(
            outlet=self._entity,
            authorization=self._authorization if auth is None else auth,
        )

    def retrieve(self, auth: AvAuthorization | None = None):
        self.data = AvialModel.from_interchange(
            avial.retrieve_entity(
                entity=self._entity,
                authorization=self._authorization if auth is None else auth,
            )
        )

    def store(self):
        avial.store_entity(
            entity=self._entity,
            authorization=self._authorization,
            value=self.data.to_interchange(),
        )

    def get_entity(self):
        return self._entity

    def get_authorization(self):
        return self._authorization
