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
import avesterra.factors as factors
from avesterra.avesterra import AvEntity, AvAuthorization, AuthorizationError
from avesterra.avial import AvValue
from avesterra.taxonomy import AvAttribute
import oop.interfaces as interfaces
from oop.factor import Factor


class Facet(interfaces.Facet):
    parent: interfaces.Fact

    entity: AvEntity
    authorization: AvAuthorization
    attribute: AvAttribute
    facet: str

    auto_dep_res: bool

    def __init__(
        self,
        parent: object,
        entity: AvEntity,
        authorization: AvAuthorization,
        attribute: AvAttribute,
        facet: str,
        auto_dep_res: bool = True,
    ):
        self.parent = parent

        self.entity = entity
        self.authorization = authorization
        self.attribute = attribute
        self.facet = facet

        self.auto_dep_res = auto_dep_res

    def set(self, value: AvValue) -> interfaces.Facet:
        try:
            facets.include_facet(
                entity=self.entity,
                attribute=self.attribute,
                name=self.facet,
                value=value,
                authorization=self.authorization,
            )
            return self
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to include facet of name {self.facet} on attribute {self.attribute.name} on entity {self.entity}"
                )
            elif "object not found" in error_str and self.auto_dep_res:
                # Add object if auto_dep_resolution is enabled
                facts.include_fact(
                    entity=self.entity,
                    attribute=self.attribute,
                    value=AvValue.encode(""),
                    authorization=self.authorization,
                )

                # Attempt to re-include facet
                facets.include_facet(
                    entity=self.entity,
                    attribute=self.attribute,
                    name=self.facet,
                    value=value,
                    authorization=self.authorization,
                )
            else:
                raise e

    def remove(self) -> interfaces.Facet:
        try:
            facets.exclude_facet(
                entity=self.entity,
                attribute=self.attribute,
                name=self.facet,
                authorization=self.authorization,
            )
            return self
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to exclude facet of name {self.facet} and attribute {self.attribute.name} from entity {self.entity}"
                )
            else:
                raise e

    def value(self):
        try:
            return facets.get_facet(
                entity=self.entity,
                attribute=self.attribute,
                name=self.facet,
                authorization=self.authorization,
            )
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to get value associated facet of name {self.facet} and attribute {self.attribute.name} from entity {self.entity}"
                )
            else:
                raise e

    def factor(self, factor: str) -> interfaces.Factor:
        return Factor(
            parent=self,
            entity=self.entity,
            authorization=self.authorization,
            attribute=self.attribute,
            facet=self.facet,
            key=factor,
            auto_dep_res=self.auto_dep_res,
        )

    def purge_factors(self):
        factors.purge_factors(
            entity=self.entity,
            attribute=self.attribute,
            name=self.facet,
            authorization=self.authorization,
        )

    def back(self) -> interfaces.Fact:
        return self.parent
