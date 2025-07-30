""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from __future__ import annotations
from avesterra import object_outlet, AvValue, AvMode
from avesterra.avesterra import AvEntity, AvAuthorization
from avesterra.taxonomy import AvAttribute, AvCategory, AvClass, AvContext
from oop.entity import Entity
import avesterra.avial as av
import avesterra.objects as objects


class Object(Entity):
    @staticmethod
    def create(
        authorization: AvAuthorization,
        name: str = "",
        key: str = "",
        context: AvContext = AvContext.NULL,
        klass: AvClass = AvClass.NULL,
        category: AvCategory = AvCategory.NULL,
        outlet: AvEntity = object_outlet,
    ):
        obj = super(Object, Object).create(
            authorization=authorization,
            name=name,
            key=key,
            context=context,
            klass=klass,
            category=category,
            outlet=outlet,
        )

        return obj

    def fact(self, attribute: AvAttribute):
        return self.data.facts[attribute]

    def fact_exists(self, attribute: AvAttribute) -> bool:
        for fact in self.data.facts:
            if fact.attribute == attribute:
                return True
        return False
