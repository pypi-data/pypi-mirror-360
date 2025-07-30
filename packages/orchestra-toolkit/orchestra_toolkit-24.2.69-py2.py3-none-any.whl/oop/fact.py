""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from __future__ import annotations
import traceback
import avesterra.facets as facets
import avesterra.facts as facts
import avesterra.features as features
import oop.interfaces as interfaces
from avesterra.avesterra import AvEntity, AvAuthorization, AuthorizationError
from avesterra.avial import AvValue
from avesterra.taxonomy import AvAttribute
from oop.facet import Facet
from oop.feature import Feature
from oop.table import Table


class Fact(interfaces.Fact):
    parent: interfaces.Object
    entity: AvEntity
    authorization: AvAuthorization
    attribute: AvAttribute

    auto_dep_res: bool

    def __init__(
        self,
        parent: interfaces.Object,
        entity: AvEntity,
        authorization: AvAuthorization,
        attribute: AvAttribute,
        auto_dep_res: bool = True,
    ):
        self.parent = parent

        self.entity = entity
        self.authorization = authorization
        self.attribute = attribute

        self.auto_dep_res = auto_dep_res

    def set(self, value: AvValue) -> interfaces.Fact:
        try:
            facts.include_fact(
                entity=self.entity,
                attribute=self.attribute,
                value=value,
                authorization=self.authorization,
            )
            return self
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to include fact {self.attribute.name} on entity {self.entity}"
                )
            else:
                raise e

    def remove(self) -> interfaces.Fact:
        try:
            facts.exclude_fact(
                entity=self.entity,
                attribute=self.attribute,
                authorization=self.authorization,
            )
            return self
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to exclude fact {self.attribute.name} from entity {self.entity}"
                )
            else:
                raise e

    def value(self):
        try:
            return facts.get_fact(
                entity=self.entity,
                attribute=self.attribute,
                authorization=self.authorization,
            )
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to exclude fact {self.attribute.name} from entity {self.entity}"
                )
            else:
                raise e

    def feature(self, key: str, name: str = "") -> Feature:
        return Feature(
            parent=self,
            entity=self.entity,
            authorization=self.authorization,
            attribute=self.attribute,
            key=key,
            name=name,
            auto_dep_res=self.auto_dep_res,
        )

    def facet(self, name: str = "") -> Facet:
        return Facet(
            parent=self,
            entity=self.entity,
            authorization=self.authorization,
            attribute=self.attribute,
            facet=name,
            auto_dep_res=self.auto_dep_res,
        )

    def table(self) -> Table:
        return Table(
            parent=self,
            entity=self.entity,
            authorization=self.authorization,
            attribute=self.attribute,
            auto_dep_res=self.auto_dep_res,
        )

    def purge_features(self):
        features.purge_features(
            entity=self.entity,
            attribute=self.attribute,
            authorization=self.authorization,
        )

    def purge_facets(self):
        facets.purge_facets(
            entity=self.entity,
            attribute=self.attribute,
            authorization=self.authorization,
        )

    def back(self) -> interfaces.Object:
        return self.parent
