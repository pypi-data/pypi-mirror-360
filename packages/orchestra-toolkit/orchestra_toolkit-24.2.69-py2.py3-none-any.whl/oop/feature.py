""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from __future__ import annotations
import traceback
import avesterra.facts as facts
import avesterra.features as features
from avesterra.avesterra import AvEntity, AvAuthorization, AuthorizationError
from avesterra.avial import AvValue
from avesterra.taxonomy import AvAttribute
import oop.interfaces as interfaces


class Feature(interfaces.Feature):
    parent: interfaces.Fact

    entity: AvEntity
    authorization: AvAuthorization
    attribute: AvAttribute
    name: str
    key: str
    auto_dep_res: bool

    def __init__(
        self,
        parent: interfaces.Fact,
        entity: AvEntity,
        authorization: AvAuthorization,
        attribute: AvAttribute,
        key: str,
        name: str = "",
        auto_dep_res: bool = True,
    ):
        self.parent = parent

        self.entity = entity
        self.authorization = authorization
        self.attribute = attribute
        self.name = name
        self.key = key

        self.auto_dep_res = auto_dep_res

    def set(self, value: AvValue) -> Feature:
        try:
            features.include_feature(
                entity=self.entity,
                attribute=self.attribute,
                name=self.name,
                key=self.key,
                value=value,
                authorization=self.authorization,
            )
            return self
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to include feature of key {self.key} and name {self.name} from object {self.attribute.name} on entity {self.entity}"
                )
            elif "object not found" in error_str and self.auto_dep_res:
                # Add object if auto_dep_resolution is enabled
                facts.include_fact(
                    entity=self.entity,
                    attribute=self.attribute,
                    value=AvValue.encode(""),
                    authorization=self.authorization,
                )
            else:
                raise e

    def remove(self) -> Feature:
        try:
            features.exclude_feature(
                entity=self.entity,
                attribute=self.attribute,
                key=self.key,
                authorization=self.authorization,
            )
            return self
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to exclude feature of key {self.key} and name {self.name} from object {self.attribute.name} on entity {self.entity}"
                )
            else:
                raise e

    def value(self) -> AvValue:
        try:
            return features.get_feature(
                entity=self.entity,
                attribute=self.attribute,
                key=self.key,
                authorization=self.authorization,
            )
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to get feature of key {self.key} and name {self.name} from object {self.attribute.name} on entity {self.entity}"
                )
            else:
                raise e

    def back(self) -> interfaces.Fact:
        return self.parent
