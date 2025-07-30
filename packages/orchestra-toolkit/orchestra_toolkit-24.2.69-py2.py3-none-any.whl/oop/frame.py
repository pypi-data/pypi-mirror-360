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
import avesterra.frames as frames
import avesterra.fields as fields
import oop.interfaces as interfaces
from avesterra.avesterra import AvEntity, AvAuthorization, AuthorizationError
from avesterra.avial import AvValue, NULL_VALUE
from avesterra.taxonomy import AvAttribute


class Frame(interfaces.Frame):
    parent: interfaces.Fact

    entity: AvEntity
    authorization: AvAuthorization
    attribute: AvAttribute
    key: str
    auto_dep_res: bool

    def __init__(
        self,
        parent: interfaces.Fact,
        entity: AvEntity,
        authorization: AvAuthorization,
        attribute: AvAttribute,
        key: str,
        auto_dep_res: bool = True,
    ):
        self.parent = parent

        self.entity = entity
        self.authorization = authorization
        self.attribute = attribute
        self.key = key

        self.auto_dep_res = auto_dep_res

    def include(self) -> Frame:
        try:
            frames.include_frame(
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
                    f"Not authorized to include frame of key {self.key} from fact {self.attribute.name} on object {self.entity}"
                )
            elif "object not found" in error_str and self.auto_dep_res:
                # Add object if auto_dep_resolution is enabled
                facts.include_fact(
                    entity=self.entity,
                    attribute=self.attribute,
                    value=AvValue.encode(""),
                    authorization=self.authorization,
                )

                # Re include frame after adding fact to object
                frames.include_frame(
                    entity=self.entity,
                    attribute=self.attribute,
                    key=self.key,
                    authorization=self.authorization,
                )

            else:
                raise e
        return self

    def exclude(self) -> Frame:
        try:
            frames.exclude_frame(
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
                    f"Not authorized to exclude frame of key {self.key} from object {self.attribute.name} on object {self.entity}"
                )
            else:
                raise e

    def clear(self, name: str = ""):
        frames.clear_frame(
            entity=self.entity,
            attribute=self.attribute,
            key=self.key,
            name=name,
            authorization=self.authorization,
        )

    def set(self, name: str, value: AvValue):
        try:
            frames.set_frame(
                entity=self.entity,
                attribute=self.attribute,
                key=self.key,
                name=name,
                value=value,
                authorization=self.authorization,
            )
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to set frame of {self.key} on field {name} of fact {self.attribute.name} on object {self.entity}"
                )
            elif "object not found" in error_str and self.auto_dep_res:
                # Add object if auto_dep_resolution is enabled
                facts.include_fact(
                    entity=self.entity,
                    attribute=self.attribute,
                    value=AvValue.encode(""),
                    authorization=self.authorization,
                )

                # Include field
                fields.include_field(
                    entity=self.entity,
                    attribute=self.attribute,
                    name=name,
                    value=NULL_VALUE,
                    authorization=self.authorization,
                )

                # Attempt to re-include field value on frame
                frames.set_frame(
                    entity=self.entity,
                    attribute=self.attribute,
                    key=self.key,
                    name=name,
                    value=value,
                    authorization=self.authorization,
                )
            elif "field not found:" in error_str and self.auto_dep_res:
                # Include field
                fields.include_field(
                    entity=self.entity,
                    attribute=self.attribute,
                    name=name,
                    value=NULL_VALUE,
                    authorization=self.authorization,
                )

                # Attempt to re-include field value on frame
                frames.set_frame(
                    entity=self.entity,
                    attribute=self.attribute,
                    key=self.key,
                    name=name,
                    value=value,
                    authorization=self.authorization,
                )

        return self

    def value(self, name: str) -> AvValue:
        try:
            return frames.get_frame(
                entity=self.entity,
                attribute=self.attribute,
                key=self.key,
                name=name,
                authorization=self.authorization,
            )
        except Exception as e:
            error_str: str = traceback.format_exc()
            if "Server reported AUTHORIZATION error" in error_str:
                raise AuthorizationError(
                    f"Not authorized to get frame {self.key} from fact {self.attribute.name} on object {self.entity}"
                )
            else:
                raise e

    def back(self) -> interfaces.Fact:
        return self.parent
