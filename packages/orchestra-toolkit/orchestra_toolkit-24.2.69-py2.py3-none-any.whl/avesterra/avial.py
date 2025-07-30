""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""
from __future__ import annotations

# ----------------------------------------------------------
# --  Module Name: avesterra.avial                        --
# --  File Name:   avial.py                               --
# --  Authors:     J. Smart & Dave Bridgelend             --
# --  Email:       avesterra@georgetown.edu               --
# --  AvesTerra - Copyright 2022 Georgetown University    --
# --  US Patent No. 9,996,567                             --
# ----------------------------------------------------------
import base64
import dataclasses
import json
import copy
from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from typing import Dict, List, Callable, Tuple
from datetime import datetime, UTC, timedelta
import avesterra.api as api
from avesterra.avesterra import *
from avesterra.hgtp import HGTPFrame
from avesterra.taxonomy import *
from avesterra.parameters import *
import enum

ENCODING = "utf-8"

#################
# Avial Classes #
#################

AvTime = datetime
AvBoolean = bool
AvString = str
AvCount = int
AvIndex = int
AvInstance = int
AvOffset = int
AvName = str
AvKey = str
AvTimeout = int
AvPrecedence = int
AvInterchange = str
AvText = str
AvWeb = str
AvEncodable = str | int | AvTime | datetime | float | bytes | AvEntity | AvAuthorization
AvAddress = int
AvParameter = int

#################
# Null constant #
#################

NULL_TIME = AvTime.fromtimestamp(0, tz=UTC)
NULL_TIMEOUT = 0
NULL_PRECEDENCE = AvPrecedence(0)

NULL_CONTEXT = AvContext.NULL
NULL_CATEGORY = AvCategory.NULL
NULL_CLASS = AvClass.NULL
NULL_METHOD = AvMethod.NULL
NULL_ATTRIBUTE = AvAttribute.NULL
NULL_EVENT = AvEvent.NULL
NULL_MODE = AvMode.NULL
NULL_STATE = AvState.NULL
NULL_CONDITION = AxCondition.NULL


class InvalidTagError(Exception):
    def __init__(self, expected: AvTag, actual: AvTag):
        self.expected = expected
        self.actual = actual

    def __str__(self):
        return f"Wrong tag: expected {self.expected.name}, got {self.actual.name}"


@dataclass
class AvLocutorOpt:
    """
    Used when the distinction between having locutor field present or absent of
    the serialized Json is useful.
    This can be useful to dinstinguish a NULL parameter to a parameter that
    that hasn't (yet) been provided
    """
    entity: AvEntity | None = None
    outlet: AvEntity | None = None
    auxiliary: AvEntity | None = None
    ancillary: AvEntity | None = None
    context: AvContext | None = None
    category: AvCategory | None = None
    klass: AvClass | None = None
    method: AvMethod | None = None
    attribute: AvAttribute | None = None
    instance: AvInstance | None = None
    offset: AvOffset | None = None
    parameter: AvParameter | None = None
    resultant: int | None = None
    count: AvCount | None = None
    index: AvIndex | None = None
    event: AvEvent | None = None
    mode: AvMode | None = None
    state: AvState | None = None
    condition: AxCondition | None = None
    precedence: AvPrecedence | None = None
    time: AvTime | None = None
    timeout: AvTimeout | None = None
    aspect: AvAspect | None = None
    template: AxTemplate | None = None
    scheme: AxScheme | None = None
    name: AvName | None = None
    label: AvString | None = None
    key: AvKey | None = None
    value: AvValue | None = None
    format: AvFormat | None = None
    authority: AvAuthorization | None = None
    authorization: AvAuthorization | None = None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AvLocutorOpt):
            return self.to_dict() == other.to_dict()
        return False

    @staticmethod
    def from_locutor(loc: "AvLocutor", keep_null: bool = False) -> "AvLocutorOpt":
        """
        :param keep_null: Whether to keep any field whose value is NULL. If
                          False, any NULL field will be converted to None
        """
        if not keep_null:
            loc = copy.copy(loc)
            default_loc = AvLocutor()
            for field in dataclasses.fields(loc):
                if getattr(loc, field.name) == getattr(default_loc, field.name):
                    setattr(loc, field.name, None)
        return AvLocutorOpt(**dataclasses.asdict(loc))

    def to_locutor(self) -> "AvLocutor":
        return AvLocutor.from_locutoropt(self)

    @staticmethod
    def from_dict(d: dict) -> AvLocutorOpt:
        loc = AvLocutorOpt()
        # fmt: off
        if "ENTITY" in d: loc.entity = AvEntity.from_str(d["ENTITY"])
        if "OUTLET" in d: loc.outlet = AvEntity.from_str(d["OUTLET"])
        if "AUXILIARY" in d: loc.auxiliary = AvEntity.from_str(d["AUXILIARY"])
        if "ANCILLARY" in d: loc.ancillary = AvEntity.from_str(d["ANCILLARY"])
        if "CONTEXT" in d: loc.context = AvContext[d["CONTEXT"].removesuffix("_CONTEXT")]
        if "CATEGORY" in d: loc.category = AvCategory[d["CATEGORY"].removesuffix("_CATEGORY")]
        if "CLASS" in d: loc.klass = AvClass[d["CLASS"].removesuffix("_CLASS")]
        if "METHOD" in d: loc.method = AvMethod[d["METHOD"].removesuffix("_METHOD")]
        if "ATTRIBUTE" in d: loc.attribute = AvAttribute[d["ATTRIBUTE"].removesuffix("_ATTRIBUTE")]
        if "INSTANCE" in d: loc.instance = int(d["INSTANCE"])
        if "OFFSET" in d: loc.offset = int(d["OFFSET"])
        if "PARAMETER" in d: loc.parameter = int(d["PARAMETER"])
        if "RESULTANT" in d: loc.resultant = int(d["RESULTANT"])
        if "COUNT" in d: loc.count = int(d["COUNT"])
        if "INDEX" in d: loc.index = int(d["INDEX"])
        if "EVENT" in d: loc.event = AvEvent[d["EVENT"].removesuffix("_EVENT")]
        if "MODE" in d: loc.mode = AvMode[d["MODE"].removesuffix("_MODE")]
        if "STATE" in d: loc.state = AvState[d["STATE"].removesuffix("_STATE")]
        if "CONDITION" in d: loc.condition = AxCondition[d["CONDITION"].removesuffix("_CONDITION")]
        if "PRECEDENCE" in d: loc.precedence = int(d["PRECEDENCE"])
        if "TIME" in d: loc.time = AvTime.fromtimestamp(int(d["TIME"]))
        if "TIMEOUT" in d: loc.timeout = int(d["TIMEOUT"])
        if "ASPECT" in d: loc.aspect = AvAspect[d["ASPECT"].removesuffix("_ASPECT")]
        if "TEMPLATE" in d: loc.template = AxTemplate[d["TEMPLATE"].removesuffix("_TEMPLATE")]
        if "SCHEME" in d: loc.scheme = AxScheme[d["SCHEME"].removesuffix("_SCHEME")]
        if "NAME" in d: loc.name = d["NAME"]
        if "LABEL" in d: loc.label = d["LABEL"]
        if "KEY" in d: loc.key = d["KEY"]
        if "VALUE" in d: loc.value = AvValue.from_json({d["VALUE_TAG"].removesuffix("_TAG"): d["VALUE"]})
        if "FORMAT" in d: loc.format = AvFormat[d["FORMAT"].removesuffix("_FORMAT")]
        if "AUTHORITY" in d: loc.authority = AvAuthorization(d["AUTHORITY"])
        if "AUTHORIZATION" in d: loc.authorization = AvAuthorization(d["AUTHORIZATION"])
        # fmt: on
        return loc

    def to_dict(self) -> dict:
        d = {}
        # fmt: off
        if self.entity is not None: d["ENTITY"] = str(self.entity)
        if self.outlet is not None: d["OUTLET"] = str(self.outlet)
        if self.auxiliary is not None: d["AUXILIARY"] = str(self.auxiliary)
        if self.ancillary is not None: d["ANCILLARY"] = str(self.ancillary)
        if self.context is not None: d["CONTEXT"] = self.context.name + "_CONTEXT"
        if self.category is not None: d["CATEGORY"] = self.category.name + "_CATEGORY"
        if self.klass is not None: d["CLASS"] = self.klass.name + "_CLASS"
        if self.method is not None: d["METHOD"] = self.method.name + "_METHOD"
        if self.attribute is not None: d["ATTRIBUTE"] = self.attribute.name + "_ATTRIBUTE"
        if self.instance is not None: d["INSTANCE"] = self.instance
        if self.offset is not None: d["OFFSET"] = self.offset
        if self.parameter is not None: d["PARAMETER"] = self.parameter
        if self.resultant is not None: d["RESULTANT"] = self.resultant
        if self.count is not None: d["COUNT"] = self.count
        if self.index is not None: d["INDEX"] = self.index
        if self.event is not None: d["EVENT"] = self.event.name + "_EVENT"
        if self.mode is not None: d["MODE"] = self.mode.name + "_MODE"
        if self.state is not None: d["STATE"] = self.state.name + "_STATE"
        if self.condition is not None: d["CONDITION"] = self.condition.name + "_CONDITION"
        if self.precedence is not None: d["PRECEDENCE"] = str(self.precedence)
        if self.time is not None: d["TIME"] = self.time.timestamp()
        if self.timeout is not None: d["TIMEOUT"] = self.timeout
        if self.aspect is not None: d["ASPECT"] = self.aspect.name + "_ASPECT"
        if self.template is not None: d["TEMPLATE"] = self.template.name + "_TEMPLATE"
        if self.scheme is not None: d["SCHEME"] = self.scheme.name + "_SCHEME"
        if self.name is not None: d["NAME"] = self.name
        if self.label is not None: d["LABEL"] = self.label
        if self.key is not None: d["KEY"] = self.key
        if self.format is not None: d["FORMAT"] = self.format.name + "_FORMAT"
        if self.authority is not None: d["AUTHORITY"] = str(self.authority)
        if self.authorization is not None: d["AUTHORIZATION"] = str(self.authorization)
        # fmt: on

        if self.value is not None:
            val = self.value.obj()
            d["VALUE_TAG"] = list(val.keys())[0] + "_TAG"
            d["VALUE"] = val[list(val.keys())[0]]

        return d

@dataclass
class AvLocutor:
    """
    Generic data structure that contains all the arguments to an invoke call
    (more or less).  
    If you need to have each argument be optional, use AvLocutorOpt instead
    """
    entity: AvEntity = NULL_ENTITY
    outlet: AvEntity = NULL_ENTITY
    auxiliary: AvEntity = NULL_ENTITY
    ancillary: AvEntity = NULL_ENTITY
    context: AvContext = AvContext.NULL
    category: AvCategory = AvCategory.NULL
    klass: AvClass = AvClass.NULL
    method: AvMethod = AvMethod.NULL
    attribute: AvAttribute = AvAttribute.NULL
    instance: AvInstance = NULL_INSTANCE
    offset: AvOffset = NULL_OFFSET
    parameter: AvParameter = NULL_PARAMETER
    resultant: int = 0
    count: AvCount = NULL_COUNT
    index: AvIndex = NULL_INDEX
    event: AvEvent = AvEvent.NULL
    mode: AvMode = AvMode.NULL
    state: AvState = AvState.NULL
    condition: AxCondition = AxCondition.NULL
    precedence: AvPrecedence = NULL_PRECEDENCE
    time: AvTime = AvTime.fromtimestamp(0, tz=UTC)
    timeout: AvTimeout = NULL_TIMEOUT
    aspect: AvAspect = AvAspect.NULL
    template: AxTemplate = AxTemplate.NULL
    scheme: AxScheme = AxScheme.NULL
    name: AvName = NULL_NAME
    label: AvString = ""
    key: AvKey = NULL_KEY
    value: AvValue = field(default_factory=lambda: NULL_VALUE)
    format: AvFormat = AvFormat.NULL
    authority: AvAuthorization = NULL_AUTHORIZATION
    authorization: AvAuthorization = NULL_AUTHORIZATION

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AvLocutor):
            return self.to_dict() == other.to_dict()
        return False

    @staticmethod
    def from_locutoropt(loc: AvLocutorOpt) -> AvLocutor:
        d = dataclasses.asdict(loc)
        d = {k:v for k,v in d.items() if v is not None}
        return AvLocutor(**d)

    @staticmethod
    def from_dict(d: dict) -> AvLocutor:
        return AvLocutorOpt.from_dict(d).to_locutor()

    def to_locutoropt(self, keep_null: bool = False) -> AvLocutorOpt:
        """
        :param keep_null: Whether to keep any field whose value is NULL. If
                          False, any NULL field will be converted to None
        """
        return AvLocutorOpt.from_locutor(self, keep_null)

    def to_dict(self) -> dict:
        return self.to_locutoropt(False).to_dict()


#################
# Value classes #
#################


class AvValue:
    def __init__(self, tag: AvTag, bytes: bytes):
        self._tag = tag
        self._bytes = bytes

    def __repr__(self) -> str:
        return f'AvValue({self._tag}, "{self._bytes.decode(ENCODING)}")'

    def obj(self) -> Dict:
        return {self._tag.name: self._bytes.decode(ENCODING)}

    @staticmethod
    def from_json(value_json: Dict[str, str]) -> AvValue:
        # Get tag
        tag: AvTag = AvTag[list(value_json.keys())[0]]

        # Get value string
        value_str: str = list(value_json.values())[0]

        if tag == AvTag.AVESTERRA:
            return AvValue.encode_avesterra(value_str)
        if tag == AvTag.NULL:
            return AvValue.encode_null(value_str)
        elif tag == AvTag.STRING:
            return AvValue.encode_string(value_str)
        elif tag == AvTag.CHARACTER:
            return AvValue.encode_character(value_str)
        elif tag == AvTag.TEXT:
            return AvValue.encode_text(value_str)
        elif tag == AvTag.INTERCHANGE:
            return AvValue.encode_interchange(value_str)
        elif tag == AvTag.WEB:
            return AvValue.encode_web(value_str)
        elif tag == AvTag.BOOLEAN:
            return AvValue.encode_boolean(True if value_str == "TRUE" else False)
        elif tag == AvTag.AUTHORIZATION:
            return AvValue.encode_authorization(AvAuthorization(value_str))
        elif tag == AvTag.INTEGER:
            return AvValue.encode_integer(int(value_str))
        elif tag == AvTag.FLOAT:
            return AvValue.encode_float(float(value_str))
        elif tag == AvTag.ENTITY:
            return AvValue.encode_entity(AvEntity.from_str(value_str))
        elif tag == AvTag.TIME:
            return AvValue.encode_time(
                AvTime.fromtimestamp(int(value_str), tz=UTC).replace(microsecond=0)
            )
        elif tag == AvTag.DURATION:
            return AvValue.encode_duration(float(value_str))
        elif tag == AvTag.EXCEPTION:
            exception_dict = json.loads(value_str)
            err = exception_dict["ERROR"].removesuffix("_ERROR")
            msg = exception_dict["MESSAGE"]
            return AvValue.encode_exception(err=AvError[err], msg=msg)
        elif tag == AvTag.VARIABLE:
            value_map = json.loads(value_str)
            [key, val] = list(value_map.items())[0]
            return AvValue.encode_variable(key, AvValue.from_json(val))
        elif tag == AvTag.AGGREGATE:
            values_map = {}
            for key, value in json.loads(value_str).items():
                values_map[key] = AvValue.from_json(value)
            return AvValue.encode_aggregate(values_map)
        elif tag == AvTag.ARRAY:
            value_list: List[AvValue] = []
            for value in json.loads(value_str):
                value_list.append(AvValue.from_json(value))
            return AvValue.encode_array(value_list)
        elif tag == AvTag.DATA:
            return AvValue.encode_data(base64.b16decode(value_str))
        elif tag == AvTag.OPERATOR:
            value_str = value_str.removesuffix("_OPERATOR")
            return AvValue.encode_operator(AvOperator[value_str])
        elif tag == AvTag.FUNCTION:
            return AvValue.encode_function(AvEntity.from_str(value_str))
        elif tag == AvTag.LOCUTOR:
            return AvValue.encode_locutor(AvLocutor.from_dict(json.loads(value_str)))
        else:
            raise ValueError(f"Unknown TAG given: {tag}")

    def __str__(self):
        if self._tag == AvTag.DATA:
            bytes_str = base64.b16encode(self._bytes).decode(ENCODING)
        else:
            bytes_str = self._bytes.decode(ENCODING)
        return "{" + f'"{self.tag().name}": "{bytes_str}' + '"}'

    def __eq__(self, other) -> bool:
        if not isinstance(other, AvValue):
            return False

        """Are they equal?"""
        try:
            return self._tag == other._tag and self._bytes == other._bytes
        except AttributeError:
            return False

    @staticmethod
    def encode(object) -> AvValue:
        """Create a AvValue instance from the type of the object."""
        if isinstance(object, AvValue):
            return AvValue(object._tag, object._bytes)
        if isinstance(object, AvLocutor):
            return AvValue.encode_locutor(object)
        if isinstance(object, AvOperator):
            return AvValue.encode_operator(object)
        elif isinstance(object, AvAuthorization):
            return AvValue(AvTag.AUTHORIZATION, str(object).encode(ENCODING))
        elif isinstance(object, bool):
            return AvValue(AvTag.BOOLEAN, b"TRUE" if object else b"FALSE")
        elif isinstance(
            object, str
        ):  # all strings currently encoded as AvTEXT because python strings are UTF-8 encoded by default
            return AvValue(AvTag.TEXT, object.encode(ENCODING))
        elif isinstance(object, AvText):  # Not enabled until AvText not equal str
            return AvValue(AvTag.TEXT, object.encode(ENCODING))
        elif isinstance(object, AvString):  # Not enabled until AvString not equal str
            return AvValue(AvTag.STRING, object.encode(ENCODING))
        elif isinstance(object, AvWeb):  # Not enabled until AvWeb not equal str
            return AvValue(AvTag.WEB, object.encode(ENCODING))
        elif isinstance(object, int):
            # the seemingly unnecessary int() is to deal with enums
            return AvValue(AvTag.INTEGER, str(int(object)).encode(ENCODING))
        elif isinstance(object, float):
            return AvValue(AvTag.FLOAT, str(object).encode(ENCODING))
        elif isinstance(object, AvEntity):
            return AvValue(AvTag.ENTITY, str(object).encode(ENCODING))
        elif isinstance(object, AvTime) or isinstance(object, datetime):
            return AvValue(AvTag.TIME, str(int(object.timestamp())).encode(ENCODING))
        elif isinstance(object, AvInterchange):
            return AvValue(AvTag.INTERCHANGE, object.encode(ENCODING))
        elif isinstance(object, bytes):
            return AvValue.encode_data(object)
        elif isinstance(object, BaseException) or isinstance(object, Exception):
            return AvValue.encode_exception(AvError.THROW, str(object))
        else:
            raise ValueError(
                f"Object of type {type(object)} is currently unsupported for conversion, into an AvValue, in this binding"
            )

    @staticmethod
    def encode_null(data: str = "") -> AvValue:
        """Create an AvValue of tag `AvTag.NULL`."""
        return AvValue(AvTag.NULL, data.encode(ENCODING))

    @staticmethod
    def encode_avesterra(data: str = "") -> AvValue:
        """Create an AvValue of tag `AvTag.AVESTERRA`."""
        return AvValue(AvTag.AVESTERRA, data.encode(ENCODING))

    @staticmethod
    def encode_boolean(data: bool) -> AvValue:
        """Create an AvValue of tag `AvTag.BOOLEAN`."""
        return AvValue(AvTag.BOOLEAN, b"TRUE" if data else b"FALSE")

    @staticmethod
    def encode_character(data: str) -> AvValue:
        """Create an AvValue of tag `AvTag.CHARACTER`."""
        return AvValue(AvTag.CHARACTER, data.encode(ENCODING))

    @staticmethod
    def encode_string(data: str) -> AvValue:
        """Create an AvValue of tag `AvTag.STRING`."""
        return AvValue(AvTag.STRING, data.encode(ENCODING))

    @staticmethod
    def encode_text(data: str) -> AvValue:
        """Create an AvValue of tag `AvTag.TEXT`."""
        return AvValue(AvTag.TEXT, data.encode(ENCODING))

    @staticmethod
    def encode_integer(data: int) -> AvValue:
        """Create an AvValue of tag `AvTag.INTEGER`."""
        return AvValue(AvTag.INTEGER, str(data).encode(ENCODING))

    @staticmethod
    def encode_float(data: float) -> AvValue:
        """Create an AvValue of tag `AvTag.FLOAT`."""
        return AvValue(AvTag.FLOAT, str(data).encode(ENCODING))

    @staticmethod
    def encode_entity(data: AvEntity) -> AvValue:
        """Create an AvValue of tag `AvTag.ENTITY`."""
        return AvValue(AvTag.ENTITY, str(data).encode(ENCODING))

    @staticmethod
    def encode_time(data: AvTime | datetime) -> AvValue:
        """Create an AvValue of tag `AvTag.TIME`."""
        return AvValue(AvTag.TIME, str(int(data.timestamp())).encode(ENCODING))

    @staticmethod
    def encode_web(data: str) -> AvValue:
        """Create an AvValue of tag `AvTag.WEB`."""
        return AvValue(AvTag.WEB, data.encode(ENCODING))

    @staticmethod
    def encode_interchange(data: AvInterchange) -> AvValue:
        """Create an AvValue of tag `AvTag.INTERCHANGE`."""
        return AvValue(AvTag.INTERCHANGE, data.encode(ENCODING))

    @staticmethod
    def encode_data(data: bytes) -> AvValue:
        """Create an AvValue of tag `AvTag.DATA`."""
        return AvValue(AvTag.DATA, base64.b16encode(data))

    @staticmethod
    def encode_exception(err: AvError, msg: str) -> AvValue:
        """Create an AvValue of tag `AvTag.EXCEPTION`."""
        data = {"ERROR": err.name + "_ERROR", "MESSAGE": msg}
        return AvValue(AvTag.EXCEPTION, json.dumps(data).encode(ENCODING))

    @staticmethod
    def encode_operator(data: AvOperator) -> AvValue:
        """Create an AvValue of tag `AvTag.OPERATOR`."""
        return AvValue(AvTag.OPERATOR, (data.name + "_OPERATOR").encode(ENCODING))

    @staticmethod
    def encode_function(data: AvEntity) -> AvValue:
        """Create an AvValue of tag `AvTag.FUNCTION`."""
        return AvValue(AvTag.FUNCTION, str(data).encode(ENCODING))

    # TODO: Measurement

    @staticmethod
    def encode_locutor(data: AvLocutor) -> AvValue:
        """Create an AvValue of tag `AvTag.LOCUTOR`."""
        return AvValue(AvTag.LOCUTOR, json.dumps(data.to_dict()).encode(ENCODING))

    @staticmethod
    def encode_locutoropt(data: AvLocutorOpt) -> AvValue:
        """
        Create an AvValue of tag `AvTag.LOCUTOR` with distinction between
        missing fields and NULL fields.
        """
        return AvValue(AvTag.LOCUTOR, json.dumps(data.to_dict()).encode(ENCODING))

    @staticmethod
    def encode_authorization(data: AvAuthorization) -> AvValue:
        """Create an AvValue of tag `AvTag.AUTHORIZATION`."""
        return AvValue(AvTag.AUTHORIZATION, str(data).encode(ENCODING))

    @staticmethod
    def encode_duration(data: float) -> AvValue:
        """Create an AvValue of tag `AvTag.DURATION`."""
        return AvValue(AvTag.DURATION, str(data).encode(ENCODING))

    @staticmethod
    def encode_variable(key: str, data: AvValue) -> AvValue:
        """Create an AvValue of tag `AvTag.INTERCHANGE`."""
        return AvValue(AvTag.VARIABLE, json.dumps({key: data.obj()}).encode(ENCODING))

    @staticmethod
    def encode_array(data: List[AvValue]) -> AvValue:
        """Create an AvValue of tag `AvTag.ARRAY`."""
        values = []
        for value in data:
            values.append(value.obj())
        return AvValue(AvTag.ARRAY, json.dumps(values).encode(ENCODING))

    @staticmethod
    def encode_aggregate(data: Dict[str, AvValue]) -> AvValue:
        """Create an AvValue of tag `AvTag.AGGREGATE`."""
        values = {}
        for key, value in data.items():
            values[key] = value.obj()
        return AvValue(AvTag.AGGREGATE, json.dumps(values).encode(ENCODING))

    def decode(self):
        if self._tag == AvTag.NULL:
            return self.decode_null()
        elif self._tag == AvTag.STRING:
            return self.decode_string()
        elif self._tag == AvTag.TEXT:
            return self.decode_text()
        elif self._tag == AvTag.INTERCHANGE:
            return self.decode_interchange()
        elif self._tag == AvTag.WEB:
            return self.decode_web()
        elif self._tag == AvTag.BOOLEAN:
            return self.decode_boolean()
        elif self._tag == AvTag.LOCUTOR:
            return self.decode_locutor()
        elif self._tag == AvTag.AUTHORIZATION:
            return self.decode_authorization()
        elif self._tag == AvTag.INTEGER:
            return self.decode_integer()
        elif self._tag == AvTag.FLOAT:
            return self.decode_float()
        elif self._tag == AvTag.ENTITY:
            return self.decode_entity()
        elif self._tag == AvTag.TIME:
            return self.decode_time()
        elif self._tag == AvTag.DURATION:
            return self.decode_duration()
        elif self._tag == AvTag.DATA:
            return self.decode_data()
        elif self._tag == AvTag.CHARACTER.value:
            return self.decode_character()
        elif self._tag == AvTag.VARIABLE:
            return self.decode_variable()
        elif self._tag == AvTag.ARRAY:
            return self.decode_array()
        elif self._tag == AvTag.AGGREGATE:
            return self.decode_aggregate()
        elif self._tag == AvTag.OPERATOR:
            return self.decode_operator()
        elif self._tag == AvTag.FUNCTION:
            return self.decode_function()
        elif self._tag == AvTag.EXCEPTION.value:
            return Exception(json.loads(self._bytes.decode(ENCODING))["MESSAGE"])
        else:
            raise ValueError(
                f"Error: AvValue Tag type {self._tag.name} not supported for decoding"
            )

    def decode_null(self) -> str:
        """
        decode the value as a null value.
        If the tag is not null, raise a InvalidTagError.
        """
        if self._tag == AvTag.NULL.value:
            return self._bytes.decode(ENCODING)
        else:
            raise InvalidTagError(AvTag.NULL, self._tag)

    def decode_avesterra(self) -> str:
        """
        decode the value as an avesterra value.
        If the tag is not avesterra, raise a InvalidTagError.
        """
        if self._tag == AvTag.AVESTERRA.value:
            return self._bytes.decode(ENCODING)
        else:
            raise InvalidTagError(AvTag.AVESTERRA, self._tag)

    def decode_boolean(self) -> bool:
        """
        decode the value as a boolean.
        If the tag is not boolean, raise a InvalidTagError.
        """
        if self._tag == AvTag.BOOLEAN.value:
            return True if self._bytes == b"TRUE" else False
        else:
            raise InvalidTagError(AvTag.BOOLEAN, self._tag)

    def decode_character(self) -> str:
        """
        decode the value as a character.
        If the tag is not character, raise a InvalidTagError.
        """
        if self._tag == AvTag.CHARACTER.value:
            return self._bytes.decode(ENCODING)
        else:
            raise InvalidTagError(AvTag.CHARACTER, self._tag)

    def decode_string(self) -> str:
        """
        decode the value as a string.
        If the tag is not string, raise a InvalidTagError.
        """
        if self._tag == AvTag.STRING.value:
            return self._bytes.decode(ENCODING)
        else:
            raise InvalidTagError(AvTag.STRING, self._tag)

    def decode_text(self) -> str:
        """
        decode the value as a text.
        If the tag is not text, raise a InvalidTagError.
        """
        if self._tag == AvTag.TEXT.value:
            return self._bytes.decode(ENCODING)
        else:
            raise InvalidTagError(AvTag.TEXT, self._tag)

    def decode_integer(self) -> int:
        """
        decode the value as an integer.
        If the tag is not integer, raise a InvalidTagError.
        """
        if self._tag == AvTag.INTEGER.value:
            return int(self._bytes.decode(ENCODING))
        else:
            raise InvalidTagError(AvTag.INTEGER, self._tag)

    def decode_float(self) -> float:
        """
        decode the value as a float.
        If the tag is not float, raise a InvalidTagError.
        """
        if self._tag == AvTag.FLOAT.value:
            return float(self._bytes)
        else:
            raise InvalidTagError(AvTag.FLOAT, self._tag)

    def decode_entity(self) -> AvEntity:
        """
        decode the value as an entity.
        If the tag is not entity, raise a InvalidTagError.
        """
        if self._tag == AvTag.ENTITY.value:
            return entity_of(self._bytes.decode(ENCODING))
        else:
            raise InvalidTagError(AvTag.ENTITY, self._tag)

    def decode_time(self) -> AvTime:
        """
        decode the value as a time.
        If the tag is not time, raise a InvalidTagError.
        """
        if self._tag == AvTag.TIME.value:
            return AvTime.fromtimestamp(
                int(self._bytes.decode(ENCODING)), tz=UTC
            ).replace(microsecond=0)
        else:
            raise InvalidTagError(AvTag.TIME, self._tag)

    def decode_web(self) -> str:
        """
        decode the value as a web.
        If the tag is not web, raise a InvalidTagError.
        """
        if self._tag == AvTag.WEB.value:
            return self._bytes.decode(ENCODING)
        else:
            raise InvalidTagError(AvTag.WEB, self._tag)

    def decode_interchange(self) -> str:
        """
        decode the value as an interchange.
        If the tag is not interchange, raise a InvalidTagError.
        """
        if self._tag == AvTag.INTERCHANGE.value:
            return self._bytes.decode(ENCODING)
        else:
            raise InvalidTagError(AvTag.INTERCHANGE, self._tag)

    def decode_data(self) -> bytes:
        """
        decode the value as a data.
        If the tag is not data, raise a InvalidTagError.
        """
        if self._tag == AvTag.DATA.value:
            return base64.b16decode(self._bytes)
        else:
            raise InvalidTagError(AvTag.DATA, self._tag)

    def decode_exception(self) -> Tuple[AvError, str]:
        """
        decode the value as an exception.
        If the tag is not exception, raise a InvalidTagError.
        """
        if self._tag == AvTag.EXCEPTION.value:
            json_str = self._bytes.decode(ENCODING)
            json_obj = json.loads(json_str)
            return (
                AvError[json_obj["ERROR"].removesuffix("_ERROR")],
                json_obj["MESSAGE"],
            )
        else:
            raise InvalidTagError(AvTag.EXCEPTION, self._tag)

    def decode_operator(self) -> AvOperator:
        """
        decode the value as an operator.
        If the tag is not operator, raise a InvalidTagError.
        """
        if self._tag == AvTag.OPERATOR.value:
            return AvOperator[self._bytes.decode(ENCODING).removesuffix("_OPERATOR")]
        else:
            raise InvalidTagError(AvTag.FUNCTION, self._tag)

    def decode_function(self) -> AvEntity:
        """
        decode the value as a function.
        If the tag is not function, raise a InvalidTagError.
        """
        if self._tag == AvTag.FUNCTION.value:
            return entity_of(self._bytes.decode(ENCODING))
        else:
            raise InvalidTagError(AvTag.FUNCTION, self._tag)

    def decode_locutor(self) -> AvLocutor:
        """
        decode the value as a locutor.
        If the tag is not function, raise a InvalidTagError.
        """
        if self._tag == AvTag.LOCUTOR.value:
            return AvLocutor.from_dict(json.loads(self._bytes.decode(ENCODING)))
        else:
            raise InvalidTagError(AvTag.LOCUTOR, self._tag)

    def decode_locutoropt(self) -> AvLocutorOpt:
        """
        decode the value as a locutor, with distinction between missing fields 
        and null fields.
        If the tag is not function, raise a InvalidTagError.
        """
        if self._tag == AvTag.LOCUTOR.value:
            return AvLocutorOpt.from_dict(json.loads(self._bytes.decode(ENCODING)))
        else:
            raise InvalidTagError(AvTag.LOCUTOR, self._tag)

    def decode_authorization(self) -> AvAuthorization:
        """
        decode the value as an authorization.
        If the tag is not authorization, raise a InvalidTagError.
        """
        if self._tag == AvTag.AUTHORIZATION.value:
            return AvAuthorization(self._bytes.decode(ENCODING))
        else:
            raise InvalidTagError(AvTag.AUTHORIZATION, self._tag)

    def decode_duration(self) -> float:
        """
        decode the value as a duration.
        If the tag is not duration, raise a InvalidTagError.
        """
        if self._tag == AvTag.DURATION.value:
            return float(self._bytes.decode(ENCODING))
        else:
            raise InvalidTagError(AvTag.DURATION, self._tag)

    # TODO: Measurement
    # TODO: Locutor
    # TODO: VARIABLE
    def decode_variable(self) -> Tuple[str, AvValue]:
        """
        decode the value as a variable.
        If the tag is not variable, raise a InvalidTagError.
        """
        if self._tag == AvTag.VARIABLE.value:
            obj = json.loads(self._bytes.decode(ENCODING))
            key, value_obj = list(obj.items())[0]
            value = AvValue.from_json(value_obj)
            return key, value
        else:
            raise InvalidTagError(AvTag.VARIABLE, self._tag)

    def decode_array(self) -> List[AvValue]:
        """
        decode the value as an array.
        If the tag is not variable, raise a InvalidTagError.
        """
        if self._tag == AvTag.ARRAY.value:
            values = []
            obj: List = json.loads(self._bytes.decode(ENCODING))
            for value_obj in obj:
                values.append(AvValue.from_json(value_obj))
            return values
        else:
            raise InvalidTagError(AvTag.ARRAY, self._tag)

    def decode_aggregate(self) -> Dict[str, AvValue]:
        """
        decode the value as a aggregate.
        If the tag is not variable, raise a InvalidTagError.
        """
        if self._tag == AvTag.AGGREGATE.value:
            values = {}
            obj: Dict = json.loads(self._bytes.decode(ENCODING))
            for key, value_obj in obj.items():
                values[key] = AvValue.from_json(value_obj)
            return values
        else:
            raise InvalidTagError(AvTag.AGGREGATE, self._tag)

    def tag(self) -> AvTag:
        return self._tag

    def bytes(self) -> bytes:
        return self._bytes


#########################
# Argument verification #
#########################


class Verify:
    @staticmethod
    def entity(obj) -> None:
        """Raise error if obj is not an entity."""
        if not isinstance(obj, AvEntity):
            raise AvesTerraError("{} is not a valid entity".format(obj))

    @staticmethod
    def integer(obj) -> None:
        """Raise error if obj is not an integer."""
        if not isinstance(obj, int) or isinstance(obj, enum.IntEnum):
            raise AvesTerraError("{} is not a valid integer".format(obj))

    @staticmethod
    def natural(obj) -> None:
        """Raise error if obj is not a non-negative integer."""
        if not isinstance(obj, int) or isinstance(obj, enum.IntEnum):
            raise AvesTerraError("{} is not a validate natural".format(obj))
        if obj < 0:
            raise AvesTerraError("{} is less than zero".format(obj))

    @staticmethod
    def string(obj) -> None:
        """Raise error if obj is not a string."""
        if not isinstance(obj, str):
            raise AvesTerraError("{} is not a valid string".format(obj))

    @staticmethod
    def interchange(obj) -> None:
        """Raise error if obj is not an interchange."""
        if not isinstance(obj, str):
            raise AvesTerraError("{} is not a valid interchange".format(obj))

    @staticmethod
    def bytes(obj) -> None:
        """Raise error if obj is not bytes."""
        if not isinstance(obj, bytes):
            raise AvesTerraError("{} is not a valid bytes object".format(obj))

    @staticmethod
    def category(obj) -> None:
        """Raise error if obj is not a valid category."""
        if not isinstance(obj, AvCategory):
            raise AvesTerraError("{} is not a valid category".format(obj))

    @staticmethod
    def klass(obj) -> None:
        """Raise error if obj is not a valid class."""
        if not isinstance(obj, AvClass):
            raise AvesTerraError("{} is not a valid class".format(obj))

    @staticmethod
    def context(obj) -> None:
        """Raise error if obj is not a valid context."""
        if not isinstance(obj, AvContext):
            raise AvesTerraError("{} is not a valid context".format(obj))

    @staticmethod
    def aspect(obj) -> None:
        """Raise error if obj is not a valid aspect."""
        if not isinstance(obj, AvAspect):
            raise AvesTerraError("{} is not a valid aspect".format(obj))

    @staticmethod
    def method(obj) -> None:
        """Raise error if obj is not a valid context."""
        if not isinstance(obj, AvMethod):
            raise AvesTerraError("{} is not a valid method".format(obj))

    @staticmethod
    def attribute(obj) -> None:
        """Raise error if obj is not a valid attribute."""
        if not isinstance(obj, AvAttribute):
            raise AvesTerraError("{} is not a valid attribute".format(obj))

    @staticmethod
    def event(obj) -> None:
        """Raise error if obj is not a valid event."""
        if not isinstance(obj, AvEvent):
            raise AvesTerraError("{} is not a valid event".format(obj))

    @staticmethod
    def mode(obj) -> None:
        """Raise error if obj is not a valid mode."""
        if not isinstance(obj, AvMode):
            raise AvesTerraError("{} is not a valid mode".format(obj))

    @staticmethod
    def state(obj) -> None:
        """Raise error if obj is not a valid state."""
        if not isinstance(obj, AvState):
            raise AvesTerraError("{} is not a valid state".format(obj))

    @staticmethod
    def parameter(obj) -> None:
        """Raise error if obj is not a valid parameter."""
        if not isinstance(obj, AvParameter):
            raise AvesTerraError("{} is not a valid parameter".format(obj))

    @staticmethod
    def condition(obj) -> None:
        """Raise error if obj is not a valid mode."""
        if not isinstance(obj, AxCondition):
            raise AvesTerraError("{} is not a valid condition".format(obj))

    @staticmethod
    def precedence(obj) -> None:
        """Raise error if obj is not a valid precedence."""
        if not isinstance(obj, int):
            raise AvesTerraError("{} is not a valid precedence".format(obj))

    @staticmethod
    def time(obj) -> None:
        """Raise error if obj is not a valid time."""
        if not isinstance(obj, AvTime):
            raise AvesTerraError("{} is not a valid time".format(obj))

    @staticmethod
    def value(obj) -> None:
        if not isinstance(obj, AvValue):
            raise AvesTerraError("{} is not a valid value".format(obj))

    @staticmethod
    def authorization(obj) -> None:
        """Raise error if obj is not an authorization."""
        if not isinstance(obj, AvAuthorization):
            raise AuthorizationError("{} is not a valid authorization".format(obj))

    @staticmethod
    def callback(obj) -> None:
        if obj is not None and not callable(obj):
            raise AvesTerraError(f"{obj} is not a callable callback.")


NULL_VALUE = AvValue(AvTag.NULL, b"")

######################
# Session Operations #
######################


def initialize(
    server: str = "",
    directory: str = "",
    socket_count: int = 16,
    max_timeout: AvTimeout = 360,
):
    """Start an AvesTerra session."""
    api.initialize(
        server=server,
        directory=directory,
        socket_count=socket_count,
        max_timeout=max_timeout,
    )


def finalize() -> None:
    """End the AvesTerra session."""
    api.finalize()


# Avial 4.7: Server entity call now routable using server parameter
def server_entity(server: AvEntity) -> AvEntity:
    """Return the server entity"""
    return api.local(server=server)


# Avial 4.7: Server gateway call now routable using server parameter
def server_gateway(server: AvEntity) -> AvEntity:
    """Return the local server entity"""
    return api.server_gateway(server=server)


# Avial 4.7: Server hostname call now routable using server parameter
def server_hostname(server: AvEntity) -> str:
    """Return the local serve entity"""
    return str(api.hostname(server=server), ENCODING)


# Avial 4.7: Server internet call now routable using server parameter
def server_internet(server: AvEntity) -> AvValue:
    """Return the local serve entity"""
    tag_int, _bytes = api.internet(server=server)
    return AvValue(tag=AvTag(tag_int), bytes=_bytes)


# Avial 4.7: Server version call now routable using server parameter
def server_version(server: AvEntity) -> str:
    """Return the local serve entity"""
    return str(api.version(server=server), ENCODING)


# Avial 4.7: Server status call now routable using server parameter
def server_status(server: AvEntity) -> str:
    """Return the local server entity"""
    return str(api.status(server=server), ENCODING)


# Avial 4.7: Server clock call now routable using server parameter
def server_clock(server: AvEntity) -> AvTime:
    """Return the server time"""
    return AvTime.fromtimestamp(api.clock(server=server), tz=UTC).replace(microsecond=0)


# Avial 4.7: Server address call now routable using server parameter
def server_address(server: AvEntity) -> IPv4Address | IPv6Address:
    """Return the IPv4/IPv6 address of the server"""
    return api.address(server=server)


def local_time() -> AvTime:
    """Return the local time"""
    return AvTime.now(UTC).replace(microsecond=0)


#####################
# Entity operations #
#####################


# Avial 4.7: Create entity now routable, by supplying the `server` argument
def create_entity(
    name: str = NULL_NAME,
    key: str = NULL_KEY,
    context: AvContext = NULL_CONTEXT,
    category: AvCategory = NULL_CATEGORY,
    klass: AvClass = NULL_CLASS,
    method: AvMethod = NULL_METHOD,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    event: AvEvent = NULL_EVENT,
    precedence: int = NULL_PRECEDENCE,
    outlet: AvEntity = NULL_ENTITY,
    server: AvEntity = NULL_ENTITY,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvEntity:
    """Create and return a new entity."""
    Verify.string(name)
    Verify.string(key)
    Verify.context(context)
    Verify.category(category)
    Verify.klass(klass)
    Verify.method(method)
    Verify.attribute(attribute)
    Verify.event(event)
    Verify.precedence(precedence)
    Verify.entity(outlet)
    Verify.entity(server)
    Verify.integer(timeout)
    Verify.authorization(authorization)
    entity = api.create(
        name=name.encode(ENCODING),
        key=key.encode(ENCODING),
        context=context,
        category=category,
        klass=klass,
        method=method,
        attribute=attribute,
        event=event,
        precedence=precedence,
        server=server,
        outlet=outlet,
        timeout=timeout,
        authorization=authorization,
    )
    return entity


# Avial 4.7: Delete entity now has a timeout
def delete_entity(
    entity: AvEntity,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Delete an entity"""
    Verify.entity(entity)
    Verify.natural(timeout)
    Verify.authorization(authorization)
    api.delete(entity=entity, timeout=timeout, authorization=authorization)


def invoke_locutor(locutor: AvLocutor) -> AvValue:
    return invoke_entity(
        entity=locutor.entity,
        method=locutor.method,
        attribute=locutor.attribute,
        name=locutor.name,
        key=locutor.key,
        value=locutor.value,
        parameter=locutor.parameter,
        resultant=locutor.resultant,
        index=locutor.index,
        instance=locutor.instance,
        offset=locutor.offset,
        count=locutor.count,
        aspect=locutor.aspect,
        context=locutor.context,
        category=locutor.category,
        klass=locutor.klass,
        event=locutor.event,
        mode=locutor.mode,
        state=locutor.state,
        condition=locutor.condition,
        precedence=locutor.precedence,
        time=locutor.time,
        timeout=locutor.timeout,
        auxiliary=locutor.auxiliary,
        ancillary=locutor.ancillary,
        authority=locutor.authority,
        authorization=locutor.authorization,
    )

def invoke_locutor_with_bo(
    locutor: AvLocutor,
    broken_outlet_repeat_max: int = 10
) -> AvValue:
    return invoke_entity_retry_bo(
        entity=locutor.entity,
        method=locutor.method,
        attribute=locutor.attribute,
        name=locutor.name,
        key=locutor.key,
        value=locutor.value,
        parameter=locutor.parameter,
        resultant=locutor.resultant,
        index=locutor.index,
        instance=locutor.instance,
        offset=locutor.offset,
        count=locutor.count,
        aspect=locutor.aspect,
        context=locutor.context,
        category=locutor.category,
        klass=locutor.klass,
        event=locutor.event,
        mode=locutor.mode,
        state=locutor.state,
        condition=locutor.condition,
        precedence=locutor.precedence,
        time=locutor.time,
        timeout=locutor.timeout,
        auxiliary=locutor.auxiliary,
        ancillary=locutor.ancillary,
        authority=locutor.authority,
        authorization=locutor.authorization,
        broken_outlet_repeat_max=broken_outlet_repeat_max,
    )

def invoke_entity(
    entity: AvEntity,
    method: AvMethod = AvMethod.NULL,
    attribute: AvAttribute = AvAttribute.NULL,
    name: str = NULL_NAME,
    key: str = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    resultant: int = NULL_RESULTANT,
    index: int = NULL_INDEX,
    instance: int = NULL_INSTANCE,
    offset: int = NULL_OFFSET,
    count: int = NULL_COUNT,
    aspect: AvAspect = AvAspect.NULL,
    context: AvContext = AvContext.NULL,
    category: AvCategory = AvCategory.NULL,
    klass: AvClass = AvClass.NULL,
    event: AvEvent = AvEvent.NULL,
    mode: AvMode = AvMode.NULL,
    state: AvState = AvState.NULL,
    condition: AxCondition = AxCondition.NULL,
    precedence: int = NULL_PRECEDENCE,
    time: AvTime = NULL_TIME,
    timeout: AvTimeout = NULL_TIMEOUT,
    auxiliary: AvEntity = NULL_ENTITY,
    ancillary: AvEntity = NULL_ENTITY,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Invoke a method on the entity."""
    Verify.entity(entity)
    Verify.string(name)
    Verify.string(key)
    Verify.value(value)
    Verify.parameter(parameter)
    Verify.integer(resultant)
    Verify.natural(index)
    Verify.natural(instance)
    Verify.natural(offset)
    Verify.natural(count)
    Verify.aspect(aspect)
    Verify.method(method)
    Verify.attribute(attribute)
    Verify.context(context)
    Verify.category(category)
    Verify.klass(klass)
    Verify.event(event)
    Verify.mode(mode)
    Verify.state(state)
    Verify.condition(condition)
    Verify.precedence(precedence)
    Verify.natural(timeout)
    Verify.entity(auxiliary)
    Verify.entity(ancillary)
    Verify.authorization(authority)
    Verify.authorization(authorization)

    result_tag_code, result_bytes = api.invoke(
        entity=entity,
        auxiliary=auxiliary,
        ancillary=ancillary,
        method=method.value,
        attribute=attribute.value,
        instance=instance,
        offset=offset,
        name=name.encode(ENCODING),
        key=key.encode(ENCODING),
        bytes=value.bytes(),
        parameter=parameter,
        resultant=resultant,
        index=index,
        count=count,
        aspect=aspect.value,
        context=context.value,
        category=category.value,
        klass=klass.value,
        event=event.value,
        mode=mode.value,
        state=state.value,
        condition=condition.value,
        precedence=precedence,
        tag=value.tag().value,
        time=int(time.timestamp()),
        timeout=timeout,
        authority=authority,
        authorization=authorization,
    )

    return AvValue(tag=AvTag(result_tag_code), bytes=result_bytes)


def invoke_entity_retry_bo(
    entity: AvEntity,
    method: AvMethod = AvMethod.NULL,
    attribute: AvAttribute = AvAttribute.NULL,
    name: str = NULL_NAME,
    key: str = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    resultant: int = NULL_RESULTANT,
    index: int = NULL_INDEX,
    instance: int = NULL_INSTANCE,
    offset: int = NULL_OFFSET,
    count: int = NULL_COUNT,
    aspect: AvAspect = AvAspect.NULL,
    context: AvContext = AvContext.NULL,
    category: AvCategory = AvCategory.NULL,
    klass: AvClass = AvClass.NULL,
    event: AvEvent = AvEvent.NULL,
    mode: AvMode = AvMode.NULL,
    state: AvState = AvState.NULL,
    condition: AxCondition = AxCondition.NULL,
    precedence: AvPrecedence = NULL_PRECEDENCE,
    time: AvTime = NULL_TIME,
    timeout: AvTimeout = 30,
    auxiliary: AvEntity = NULL_ENTITY,
    ancillary: AvEntity = NULL_ENTITY,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
    broken_outlet_repeat_max: int = 10,
):
    """
    Same as `invoke_entity`, except that it retries the invoke in case of a
    broken outlet, up to `broken_outlet_repeat_max` times. Broken outlet errors
    happen when an adapter called `adapt` on an outlet, but the adapter was
    shutdown. The outlet no longer has an open communication with the adapter
    when the remote rendez-vous happen.
    """
    for i in range(broken_outlet_repeat_max + 1):
        try:
            return invoke_entity(
                entity=entity,
                method=method,
                attribute=attribute,
                name=name,
                key=key,
                value=value,
                parameter=parameter,
                resultant=resultant,
                index=index,
                instance=instance,
                offset=offset,
                count=count,
                aspect=aspect,
                context=context,
                category=category,
                klass=klass,
                event=event,
                mode=mode,
                state=state,
                condition=condition,
                precedence=precedence,
                time=time,
                timeout=timeout,
                auxiliary=auxiliary,
                ancillary=ancillary,
                authority=authority,
                authorization=authorization,
            )
        except NetworkError:  # Handles broken outlet problem
            if i > broken_outlet_repeat_max:
                raise
    assert False, "Unreachable code"


def inquire_entity(
    entity: AvEntity,
    attribute: AvAttribute = AvAttribute.NULL,
    name: str = NULL_NAME,
    key: str = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: int = NULL_PARAMETER,
    resultant: int = NULL_RESULTANT,
    index: int = NULL_INDEX,
    instance: int = NULL_INSTANCE,
    offset: int = NULL_OFFSET,
    count: int = NULL_COUNT,
    aspect: AvAspect = AvAspect.NULL,
    context: AvContext = AvContext.NULL,
    category: AvCategory = AvCategory.NULL,
    klass: AvClass = AvClass.NULL,
    event: AvEvent = AvEvent.NULL,
    mode: AvMode = AvMode.NULL,
    state: AvState = AvState.NULL,
    condition: AxCondition = AxCondition.NULL,
    precedence: int = NULL_PRECEDENCE,
    time: AvTime = NULL_TIME,
    timeout: AvTimeout = NULL_TIMEOUT,
    auxiliary: AvEntity = NULL_ENTITY,
    ancillary: AvEntity = NULL_ENTITY,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Invoke a method on the entity."""
    Verify.entity(entity)
    Verify.string(name)
    Verify.string(key)
    Verify.value(value)
    Verify.parameter(parameter)
    Verify.integer(resultant)
    Verify.natural(index)
    Verify.natural(instance)
    Verify.natural(offset)
    Verify.natural(count)
    Verify.aspect(aspect)
    Verify.attribute(attribute)
    Verify.context(context)
    Verify.category(category)
    Verify.klass(klass)
    Verify.event(event)
    Verify.mode(mode)
    Verify.state(state)
    Verify.condition(condition)
    Verify.precedence(precedence)
    Verify.natural(timeout)
    Verify.entity(auxiliary)
    Verify.entity(ancillary)
    Verify.authorization(authority)
    Verify.authorization(authorization)

    result_tag_code, result_bytes = api.inquire(
        entity=entity,
        auxiliary=auxiliary,
        ancillary=ancillary,
        attribute=attribute.value,
        instance=instance,
        offset=offset,
        name=name.encode(ENCODING),
        key=key.encode(ENCODING),
        bytes=value.bytes(),
        parameter=parameter,
        resultant=resultant,
        index=index,
        count=count,
        aspect=aspect.value,
        context=context.value,
        category=category.value,
        klass=klass.value,
        event=event.value,
        mode=mode.value,
        state=state.value,
        condition=condition.value,
        precedence=precedence,
        tag=value.tag().value,
        time=int(time.timestamp()),
        timeout=timeout,
        authority=authority,
        authorization=authorization,
    )

    return AvValue(tag=AvTag(result_tag_code), bytes=result_bytes)


def reference_entity(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Increment the reference count of the entity."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    api.reference(entity=entity, authorization=authorization)


def dereference_entity(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Decrement the reference count of the entity."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    api.dereference(entity=entity, authorization=authorization)


def redirect_entity(
    from_entity: AvEntity,
    to_entity: AvEntity,
    server: AvEntity = NULL_ENTITY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Make a UUID abbreviation for another."""
    Verify.entity(from_entity)
    Verify.entity(to_entity)
    Verify.entity(server)
    Verify.authorization(authorization)
    api.redirect(
        server=server,
        from_entity=from_entity,
        to_entity=to_entity,
        authorization=authorization,
    )


def change_entity(
    entity,
    name: str = NULL_NAME,
    key: str = NULL_KEY,
    context: AvContext = AvContext.NULL,
    category: AvCategory = AvCategory.NULL,
    klass: AvClass = AvClass.NULL,
    state: AvState = AvState.NULL,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Change characteristics of an entity."""
    Verify.entity(entity)
    Verify.string(name)
    Verify.string(key)
    Verify.context(context)
    Verify.category(category)
    Verify.klass(klass)
    Verify.state(state)
    Verify.authorization(authority)
    Verify.authorization(authorization)
    api.change(
        entity=entity,
        name=name.encode(ENCODING),
        key=key.encode(ENCODING),
        context=context.value,
        klass=klass.value,
        category=category.value,
        state=state.value,
        authority=authority,
        authorization=authorization,
    )


def fetch_entity(
    entity: AvEntity,
    name: str = NULL_NAME,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Fetch characteristics of an entity."""
    Verify.entity(entity)
    Verify.string(name)
    Verify.authorization(authorization)
    _tag, _bytes = api.fetch(
        entity=entity, name=name.encode(ENCODING), authorization=authorization
    )

    return AvValue(tag=AvTag(_tag), bytes=_bytes)


#####################
# Common Operations "
#####################


def save_entity(entity: AvEntity, authorization: AvAuthorization) -> None:
    """Save any non-persisted changes."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    api.invoke(entity=entity, method=AvMethod.SAVE, authorization=authorization)


def restore_entity(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Revert the entity to its persisted state."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    api.invoke(entity=entity, method=AvMethod.LOAD, authorization=authorization)


# Avial 4.11 Purge entity now accepts attribute and aspect
def purge_entity(
    entity: AvEntity,
    attribute: AvAttribute = AvAttribute.NULL,
    instance: AvInstance = NULL_INSTANCE,
    aspect: AvAspect = AvAspect.NULL,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Purge an entity, removing all of its aspects."""
    Verify.entity(entity)
    Verify.attribute(attribute)
    Verify.natural(instance)
    Verify.authorization(authorization)
    api.invoke(
        entity=entity,
        method=AvMethod.PURGE,
        attribute=attribute,
        instance=instance,
        aspect=aspect,
        authorization=authorization,
    )


# Avial 4.7: Added timeout to call
def store_entity(
    entity: AvEntity,
    mode: AvMode = NULL_MODE,
    value: AvValue = NULL_VALUE,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Store new content on the entity"""
    Verify.entity(entity)
    Verify.mode(mode)
    Verify.value(value)
    Verify.natural(timeout)
    Verify.authorization(authorization)
    result_tag_code, result_bytes = api.invoke(
        entity=entity,
        method=AvMethod.STORE,
        mode=mode,
        timeout=timeout,
        bytes=value.bytes(),
        tag=value.tag().value,
        authorization=authorization,
    )
    return AvValue(tag=AvTag(result_tag_code), bytes=result_bytes)


# Avial 4.7: Added timeout to call
def retrieve_entity(
    entity: AvEntity,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Retrieve the contents of entity, in interchange format"""
    Verify.entity(entity)
    Verify.natural(timeout)
    Verify.authorization(authorization)
    result_tag_code, result_bytes = api.invoke(
        entity=entity,
        method=AvMethod.RETRIEVE.value,
        timeout=timeout,
        authorization=authorization,
    )
    return AvValue(tag=AvTag(result_tag_code), bytes=result_bytes)


#########################
# Attachment Operations #
#########################


def attach_attribute(
    entity: AvEntity,
    outlet: AvEntity,
    attribute: AvAttribute = AvAttribute.NULL,
    precedence: int = NULL_PRECEDENCE,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Attach an outlet to an entity with a particular attribute."""
    Verify.entity(entity)
    Verify.entity(outlet)
    Verify.attribute(attribute)
    Verify.precedence(precedence)
    Verify.natural(timeout)
    Verify.authorization(authorization)
    api.attach(
        entity=entity,
        outlet=outlet,
        attribute=attribute.value,
        precedence=precedence,
        timeout=timeout,
        authorization=authorization,
    )


def detach_attribute(
    entity: AvEntity,
    attribute: AvAttribute = AvAttribute.NULL,
    precedence: int = NULL_PRECEDENCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Detach an attribute from an entity"""
    Verify.entity(entity)
    Verify.attribute(attribute)
    Verify.precedence(precedence)
    Verify.authorization(authorization)
    api.detach(
        entity=entity,
        attribute=attribute.value,
        precedence=precedence,
        authorization=authorization,
    )


def attribute_attached(
    entity: AvEntity,
    attribute: AvAttribute = AvAttribute.NULL,
    precedence: int = NULL_PRECEDENCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    """Is an attribute attached to an entity?"""
    Verify.entity(entity)
    Verify.attribute(attribute)
    Verify.precedence(precedence)
    Verify.authorization(authorization)
    return api.attached(
        entity=entity,
        attribute=attribute.value,
        precedence=precedence,
        authorization=authorization,
    )


def attachment_count(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
):
    """How many attachments does an entity have?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.attachments(entity=entity, authorization=authorization)


def entity_attachment(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> Tuple[AvEntity, AvAttribute, int, int]:
    """Return attachment details (outlet, attribute, precedence, and expiration)?"""
    Verify.entity(entity)
    Verify.natural(index)
    Verify.authorization(authorization)
    (
        result_outlet,
        result_attribute,
        result_precedence,
        result_expiration,
    ) = api.attachment(entity=entity, index=index, authorization=authorization)
    return (
        result_outlet,
        AvAttribute(result_attribute),
        result_precedence,
        result_expiration,
    )


#########################
# Connection Operations #
#########################


def connect_method(
    entity: AvEntity,
    outlet: AvEntity,
    method: AvMethod = AvMethod.NULL,
    precedence: int = NULL_PRECEDENCE,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Connect an outlet to an entity with a particular method."""
    Verify.entity(entity)
    Verify.entity(outlet)
    Verify.method(method)
    Verify.precedence(precedence)
    Verify.natural(timeout)
    Verify.authorization(authorization)
    api.connect(
        entity=entity,
        outlet=outlet,
        method=method.value,
        precedence=precedence,
        timeout=timeout,
        authorization=authorization,
    )


def disconnect_method(
    entity: AvEntity,
    method: AvMethod = AvMethod.NULL,
    precedence: int = NULL_PRECEDENCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Disconnect a method from an entity"""
    Verify.entity(entity)
    Verify.method(method)
    Verify.precedence(precedence)
    Verify.authorization(authorization)
    api.disconnect(
        entity=entity,
        method=method.value,
        precedence=precedence,
        authorization=authorization,
    )


def method_connected(
    entity: AvEntity,
    method: AvMethod = AvMethod.NULL,
    precedence: int = NULL_PRECEDENCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    """Is a method connected to an entity?"""
    Verify.entity(entity)
    Verify.method(method)
    Verify.precedence(precedence)
    Verify.authorization(authorization)
    return api.connected(
        entity=entity,
        method=method.value,
        precedence=precedence,
        authorization=authorization,
    )


def connection_count(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """How many connections does an entity have?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.connections(entity=entity, authorization=authorization)


def entity_connection(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> Tuple[AvEntity, AvMethod, int, AvTime]:
    """Return connection details (outlet, attribute, precedence, and expiration)?"""
    Verify.entity(entity)
    Verify.natural(index)
    Verify.authorization(authorization)
    (
        result_outlet,
        result_method_code,
        result_precedence_code,
        result_time,
    ) = api.connection(entity=entity, index=index, authorization=authorization)
    return (
        result_outlet,
        AvMethod(result_method_code),
        result_precedence_code,
        AvTime.fromtimestamp(result_time, tz=UTC).replace(microsecond=0),
    )


########################
# Condition Operations #
########################


# AvesTerra 6.0
def set_condition(
    entity: AvEntity = NULL_ENTITY,
    condition: AxCondition = AxCondition.NULL,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Set an entity's condition."""
    Verify.entity(entity)
    Verify.condition(condition)
    Verify.string(name)
    Verify.value(value)
    Verify.authorization(authorization)
    api.set(
        entity=entity,
        condition=condition.value,
        name=name.encode(ENCODING),
        tag=value.tag(),
        bytes=value.bytes(),
        authorization=authorization,
    )


# AvesTerra 6.0
def clear_condition(
    entity: AvEntity = NULL_ENTITY,
    condition: AxCondition = AxCondition.NULL,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Clear an entitiy's condition."""
    Verify.entity(entity)
    Verify.condition(condition)
    Verify.authorization(authorization)
    api.clear(entity=entity, condition=condition, authorization=authorization)


# AvesTerra 6.0
def test_condition(
    entity: AvEntity = NULL_ENTITY,
    condition: AxCondition = AxCondition.NULL,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    """Test an entity's condition."""
    Verify.entity(entity)
    Verify.condition(condition)
    Verify.authorization(authorization)
    return api.test(
        entity=entity, condition=condition.value, authorization=authorization
    )


# so that pytest doesn't try to run this function as a test
setattr(test_condition, "__test__", False)


# AvesTerra 6.0
def condition_count(
    entity: AvEntity = NULL_ENTITY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvCount:
    """Test an entity's condition."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.conditions(entity=entity, authorization=authorization)


# AvesTerra 6.0
def condition_name(
    entity: AvEntity = NULL_ENTITY,
    condition: AxCondition = AxCondition.NULL,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvName:
    """Test an entity's condition."""
    Verify.entity(entity)
    Verify.condition(condition)
    Verify.authorization(authorization)
    return api.label(
        entity=entity, condition=condition.value, authorization=authorization
    ).decode(ENCODING)


# AvesTerra 6.0
def condition_value(
    entity: AvEntity = NULL_ENTITY,
    condition: AxCondition = AxCondition.NULL,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Test an entity's condition."""
    Verify.entity(entity)
    Verify.condition(condition)
    Verify.authorization(authorization)
    tag, _bytes = api.variable(
        entity=entity, condition=condition.value, authorization=authorization
    )
    return AvValue(tag=AvTag(tag), bytes=_bytes)


# AvesTerra 6.0
def entity_condition(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AxCondition:
    """Get entity condition"""
    Verify.entity(entity)
    Verify.natural(index)
    Verify.authorization(authorization)
    return AxCondition(
        api.condition(entity=entity, index=index, authorization=authorization)
    )


######################
# Element Operations #
######################


def insert_element(
    entity: AvEntity,
    value: AvValue = NULL_VALUE,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Insert a value into an entity"""
    Verify.entity(entity)
    Verify.value(value)
    Verify.natural(index)
    Verify.authorization(authorization)
    api.insert(
        entity=entity,
        tag=value.tag().value,
        bytes=value.bytes(),
        index=index,
        authorization=authorization,
    )


def remove_element(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Remove a value from an entity"""
    Verify.entity(entity)
    Verify.natural(index)
    Verify.authorization(authorization)
    api.remove(entity=entity, index=index, authorization=authorization)


def replace_element(
    entity: AvEntity,
    value: AvValue = NULL_VALUE,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Replace a value in an entity"""
    Verify.entity(entity)
    Verify.value(value)
    Verify.natural(index)
    Verify.authorization(authorization)
    api.replace(
        entity=entity,
        tag=value.tag().value,
        bytes=value.bytes(),
        index=index,
        authorization=authorization,
    )


def erase_elements(entity, authorization=NULL_AUTHORIZATION) -> None:
    """Erase values in an entity"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    api.erase(entity=entity, authorization=authorization)


def find_element(
    entity: AvEntity,
    value: AvValue = NULL_VALUE,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> int:
    """Find element in an entity"""
    Verify.entity(entity)
    Verify.value(value)
    Verify.natural(index)
    Verify.authorization(authorization)
    return api.find(
        entity=entity,
        tag=value.tag(),
        bytes=value.bytes(),
        index=index,
        authorization=authorization,
    )


def entity_element(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    """Return element of an entity?"""
    Verify.entity(entity)
    Verify.natural(index)
    Verify.authorization(authorization)
    result = api.element(entity, index=index, authorization=authorization)
    return AvValue(tag=AvTag(result[0]), bytes=result[1])


def element_count(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Number of elements in entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.length(entity=entity, authorization=authorization)


####################
# Event Operations #
####################


def publish_event(
    entity: AvEntity,
    method: AvMethod = AvMethod.NULL,
    attribute: AvAttribute = AvAttribute.NULL,
    name: str = NULL_NAME,
    key: str = NULL_KEY,
    value: AvValue = NULL_VALUE,
    parameter: AvParameter = NULL_PARAMETER,
    resultant: int = NULL_RESULTANT,
    index: int = NULL_INDEX,
    instance: int = NULL_INSTANCE,
    offset: int = NULL_OFFSET,
    count: int = NULL_COUNT,
    aspect: AvAspect = AvAspect.NULL,
    context: AvContext = AvContext.NULL,
    category: AvCategory = AvCategory.NULL,
    klass: AvClass = AvClass.NULL,
    event: AvEvent = AvEvent.NULL,
    mode: AvMode = AvMode.NULL,
    state: AvState = AvState.NULL,
    condition: AxCondition = AxCondition.NULL,
    precedence: int = NULL_PRECEDENCE,
    time: AvTime = NULL_TIME,
    timeout: AvTimeout = NULL_TIMEOUT,
    auxiliary: AvEntity = NULL_ENTITY,
    ancillary: AvEntity = NULL_ENTITY,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Publish an event on an entity."""
    Verify.entity(entity)
    Verify.method(method)
    Verify.attribute(attribute)
    Verify.string(name)
    Verify.string(key)
    Verify.value(value)
    Verify.parameter(parameter)
    Verify.integer(resultant)
    Verify.natural(index)
    Verify.natural(instance)
    Verify.natural(offset)
    Verify.natural(count)
    Verify.aspect(aspect)
    Verify.context(context)
    Verify.category(category)
    Verify.klass(klass)
    Verify.event(event)
    Verify.mode(mode)
    Verify.state(state)
    Verify.condition(condition)
    Verify.precedence(precedence)
    Verify.natural(timeout)
    Verify.entity(auxiliary)
    Verify.entity(ancillary)
    Verify.authorization(authority)
    Verify.authorization(authorization)
    api.publish(
        entity=entity,
        auxiliary=auxiliary,
        ancillary=ancillary,
        method=method.value,
        attribute=attribute.value,
        instance=instance,
        offset=offset,
        name=name.encode(ENCODING),
        key=key.encode(ENCODING),
        bytes=value.bytes(),
        parameter=parameter,
        resultant=resultant,
        index=index,
        count=count,
        aspect=aspect.value,
        context=context.value,
        category=category.value,
        klass=klass.value,
        event=event.value,
        mode=mode.value,
        state=state.value,
        condition=condition.value,
        precedence=precedence,
        tag=value.tag().value,
        time=int(time.timestamp()),
        timeout=timeout,
        authority=authority,
        authorization=authorization,
    )


def subscribe_event(
    entity: AvEntity,
    outlet: AvEntity,
    event: AvEvent = AvEvent.NULL,
    precedence: int = NULL_PRECEDENCE,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Subscribe outlet to events."""
    Verify.entity(entity)
    Verify.entity(outlet)
    Verify.event(event)
    Verify.precedence(precedence)
    Verify.natural(timeout)
    Verify.authorization(authorization)
    api.subscribe(
        entity=entity,
        outlet=outlet,
        event=event.value,
        precedence=precedence,
        timeout=timeout,
        authorization=authorization,
    )


def unsubscribe_event(
    entity: AvEntity,
    outlet: AvEntity,
    event: AvEvent = AvEvent.NULL,
    precedence: int = NULL_PRECEDENCE,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Unsubscribe outlet from event."""
    Verify.entity(entity)
    Verify.entity(outlet)
    Verify.event(event)
    Verify.precedence(precedence)
    Verify.natural(timeout)
    Verify.authorization(authorization)
    api.unsubscribe(
        entity=entity,
        outlet=outlet,
        event=event.value,
        precedence=precedence,
        timeout=timeout,
        authorization=authorization,
    )


def flush_events(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Unsubscribe outlet from event."""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.flush(outlet=outlet, authorization=authorization)


@dataclass
class EventData:
    entity: AvEntity
    outlet: AvEntity
    method: AvMethod
    attribute: AvAttribute
    name: AvName
    key: AvKey
    value: AvValue
    parameter: AvParameter
    resultant: int
    index: AvIndex
    instance: AvInstance
    offset: AvOffset
    count: AvCount
    aspect: AvAspect
    context: AvContext
    category: AvCategory
    klass: AvClass
    event: AvEvent
    mode: AvMode
    state: AvState
    condition: AxCondition
    precedence: AvPrecedence
    time: AvTime
    timeout: AvTimeout
    auxiliary: AvEntity
    ancillary: AvEntity
    authority: AvAuthorization
    authorization: AvAuthorization

def wait_event(
    outlet: AvEntity,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> EventData:
    """
    Wait for a single event
    If saving on network latency, consider using `wait_event_sustained` instead.
    The difference is that `wait_event` will only ask for the server for one
    event, and get one event back. That's a single back and forth.  
    `wait_event_sustained` will ask for the surver for all events, and get
    events back one by one as they come in. That's a single call to the server
    and multiple responses.
    """
    Verify.entity(outlet)
    Verify.natural(timeout)
    Verify.authorization(authorization)

    res = None

    def _local_callback(
        entity: AvEntity,
        outlet: AvEntity,
        auxiliary: AvEntity,
        ancillary: AvEntity,
        method: int,
        attribute: int,
        aspect: int,
        context: int,
        category: int,
        klass: int,
        event: int,
        mode: int,
        state: int,
        condition: int,
        precedence: int,
        tag: int,
        name: bytes,
        key: bytes,
        bytes: bytes,
        index: int,
        count: int,
        instance: int,
        offset: int,
        parameter: int,
        resultant: int,
        time: int,
        timeout: AvTimeout,
        authority: AvAuthorization,
        authorization: AvAuthorization,
    ) -> None:
        nonlocal res

        res = EventData(
            entity=entity,
            outlet=outlet,
            method=AvMethod(method),
            attribute=AvAttribute(attribute),
            name=name.decode(ENCODING),
            key=key.decode(ENCODING),
            value=AvValue(tag=AvTag(tag), bytes=bytes),
            parameter=parameter,
            resultant=resultant,
            index=index,
            instance=instance,
            offset=offset,
            count=count,
            aspect=AvAspect(aspect),
            context=AvContext(context),
            category=AvCategory(category),
            klass=AvClass(klass),
            event=AvEvent(event),
            mode=AvMode(mode),
            state=AvState(state),
            condition=AxCondition(condition),
            precedence=precedence,
            time=AvTime.fromtimestamp(time, tz=UTC).replace(microsecond=0),
            timeout=timeout,
            auxiliary=auxiliary,
            ancillary=ancillary,
            authority=authority,
            authorization=authorization,
            )

    api.wait(
        outlet=outlet,
        timeout=timeout,
        authorization=authorization,
        callback=_local_callback,
    )
    assert res is not None
    return res

def wait_event_sustained(
    outlet: AvEntity,
    callback: Callable[[EventData], bool],
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """
    Wait for events with callback.
    If network latency is not a concern, prefer using `wait_event` instead for 
    simplicity.  
    See `wait_event` documentation for a more detailed comparison.  
    As long as the callback returns `True`, the loop continues.  
    As soon as the callback returns `False`, the loop stops and this call returns.  
    """
    Verify.entity(outlet)
    Verify.natural(timeout)
    Verify.authorization(authorization)

    def _local_callback(
        entity: AvEntity,
        outlet: AvEntity,
        auxiliary: AvEntity,
        ancillary: AvEntity,
        method: int,
        attribute: int,
        aspect: int,
        context: int,
        category: int,
        klass: int,
        event: int,
        mode: int,
        state: int,
        condition: int,
        precedence: int,
        tag: int,
        name: bytes,
        key: bytes,
        bytes: bytes,
        index: int,
        count: int,
        instance: int,
        offset: int,
        parameter: int,
        resultant: int,
        time: int,
        timeout: AvTimeout,
        authority: AvAuthorization,
        authorization: AvAuthorization,
    ) -> bool:
        return callback(EventData(
            entity=entity,
            outlet=outlet,
            method=AvMethod(method),
            attribute=AvAttribute(attribute),
            name=name.decode(ENCODING),
            key=key.decode(ENCODING),
            value=AvValue(tag=AvTag(tag), bytes=bytes),
            parameter=parameter,
            resultant=resultant,
            index=index,
            instance=instance,
            offset=offset,
            count=count,
            aspect=AvAspect(aspect),
            context=AvContext(context),
            category=AvCategory(category),
            klass=AvClass(klass),
            event=AvEvent(event),
            mode=AvMode(mode),
            state=AvState(state),
            condition=AxCondition(condition),
            precedence=precedence,
            time=AvTime.fromtimestamp(time, tz=UTC).replace(microsecond=0),
            timeout=timeout,
            auxiliary=auxiliary,
            ancillary=ancillary,
            authority=authority,
            authorization=authorization,
            )
                 )

    api.wait_sustained(
        outlet=outlet,
        timeout=timeout,
        authorization=authorization,
        callback=_local_callback,
    )


def event_count(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Number of events"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    return api.pending(entity=outlet, authorization=authorization)


def event_subscribed(
    entity: AvEntity,
    event: AvEvent = AvEvent.NULL,
    precedence: int = NULL_PRECEDENCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    """Is there an event subscrption for an entity?"""
    Verify.entity(entity)
    Verify.event(event)
    Verify.precedence(precedence)
    Verify.authorization(authorization)
    return api.subscribed(
        entity=entity,
        event=event.value,
        precedence=precedence,
        authorization=authorization,
    )


def subscription_count(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Number of entity's subscription"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.subscriptions(entity=entity, authorization=authorization)


def entity_subscription(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Details of a subscription (outlet, event, precedence, and expiration)"""
    Verify.entity(entity)
    Verify.natural(index)
    Verify.authorization(authorization)
    (
        result_entity,
        result_event_code,
        result_precedence_code,
        result_time,
    ) = api.subscription(entity, index=index, authorization=authorization)
    return (
        result_entity,
        AvEvent(result_event_code),
        result_precedence_code,
        AvTime.fromtimestamp(result_time, tz=UTC).replace(microsecond=0),
    )


#####################
# Outlet operations #
#####################


def activate_entity(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Activate an outlet"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.activate(outlet=outlet, authorization=authorization)


def deactivate_entity(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Deactivate an outlet"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.deactivate(outlet=outlet, authorization=authorization)


@dataclass
class InvokeArgs:
    entity: AvEntity
    outlet: AvEntity
    method: AvMethod
    attribute: AvAttribute
    name: AvName
    key: AvKey
    value: AvValue
    parameter: AvParameter
    resultant: int
    index: AvIndex
    instance: AvInstance
    offset: AvOffset
    count: AvCount
    aspect: AvAspect
    context: AvContext
    category: AvCategory
    klass: AvClass
    event: AvEvent
    mode: AvMode
    state: AvState
    condition: AxCondition
    precedence: int
    time: AvTime
    timeout: AvTimeout
    auxiliary: AvEntity
    ancillary: AvEntity
    authorization: AvAuthorization
    mask: AvMask
    """Permission mask"""
    authority: AvAuthorization


# Avial 4.7: Added parameter to call, to support sustained adapts
# Avial 4.12: Adapt now passes permissions to local callback!
def adapt_outlet(
    outlet: AvEntity,
    callback: Callable[[InvokeArgs], AvValue],
    timeout: AvTimeout = NULL_TIMEOUT,
    parameter: AvParameter = NULL_PARAMETER,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    """Fasten a callback to an outlet, to be executed when invoked/inquired"""
    Verify.entity(outlet)
    Verify.natural(timeout)
    Verify.parameter(parameter)
    Verify.authorization(authorization)

    def _local_callback(
        msg: HGTPFrame
    ) -> Tuple[AvTag, bytes]:
        authority, mask = decode_credential(msg.authority)
        result = callback(InvokeArgs(
            entity=msg.entity,
            outlet=msg.outlet,
            method=AvMethod(msg.method_code),
            attribute=AvAttribute(msg.attribute_code),
            name=msg.name.decode(ENCODING),
            key=msg.key.decode(ENCODING),
            value=AvValue(tag=AvTag(msg.tag_code), bytes=msg._bytes),
            parameter=msg.parameter,
            resultant=msg.resultant,
            index=msg.index,
            instance=msg.instance,
            offset=msg.offset,
            count=msg.count,
            aspect=AvAspect(msg.aspect_code),
            context=AvContext(msg.context_code),
            category=AvCategory(msg.category_code),
            klass=AvClass(msg.class_code),
            event=AvEvent(msg.event_code),
            mode=AvMode(msg.mode_code),
            state=AvState(msg.state_code),
            condition=AxCondition(msg.condition_code),
            precedence=msg.precedence,
            time=AvTime.fromtimestamp(msg.time, tz=UTC).replace(microsecond=0),
            timeout=msg.timeout,
            auxiliary=msg.auxiliary,
            ancillary=msg.ancillary,
            authorization=msg.authorization,
            mask=mask,
            authority=authority,
        ))
        return result.tag(), result.bytes()

    api.adapt(
        outlet=outlet,
        timeout=timeout,
        parameter=parameter,
        authorization=authorization,
        callback=_local_callback,
    )


def synchronize_outlet(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Synchronize an outlet rendezvous"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.sync(outlet=outlet, authorization=authorization)


def lock_outlet(
    outlet: AvEntity,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Lock an outlet semaphore"""
    Verify.entity(outlet)
    Verify.natural(timeout)
    Verify.authorization(authorization)
    api.lock(outlet=outlet, timeout=timeout, authorization=authorization)


def unlock_outlet(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Unlock an outlet semaphore"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.unlock(outlet=outlet, authorization=authorization)


def arm_outlet(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Arm an outlet timer"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.arm(outlet=outlet, authorization=authorization)


def disarm_outlet(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
):
    """Disarm outlet timer"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.disarm(outlet=outlet, authorization=authorization)


def schedule_outlet(
    outlet: AvEntity,
    count: int = NULL_COUNT,
    event: AvEvent = AvEvent.NULL,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Set outlet timer/event"""
    Verify.entity(outlet)
    Verify.natural(count)
    Verify.event(event)
    Verify.authorization(authorization)
    api.schedule(outlet=outlet, count=count, event=event, authorization=authorization)


def start_outlet(outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION):
    """Start outlet timer"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.start(outlet=outlet, authorization=authorization)


def stop_outlet(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Stop outlet timer"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.stop(outlet=outlet, authorization=authorization)


def reset_outlet(outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION):
    """Reset outlet timer"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.reset(outlet=outlet, authorization=authorization)


def execute_outlet(
    outlet: AvEntity,
    entity: AvEntity,
    context: AvContext,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Execute an entity on outlet with a context"""
    Verify.entity(outlet)
    Verify.entity(entity)
    Verify.entity(context)
    Verify.natural(timeout)
    Verify.authorization(authorization)
    api.execute(
        outlet=outlet,
        entity=entity,
        context=context,
        timeout=timeout,
        authorization=authorization,
    )


def halt_outlet(
    outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """Halt an outlet"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.halt(outlet=outlet, authorization=authorization)


def flush_outlet(outlet: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION):
    """Flush an outlet event queue"""
    Verify.entity(outlet)
    Verify.authorization(authorization)
    api.flush(outlet=outlet, authorization=authorization)


###################
# Data operations #
###################


def read_data(
    entity: AvEntity,
    timeout: AvTimeout = NULL_TIMEOUT,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bytes:
    """Read an entity's data"""
    return invoke_entity(
        entity=entity,
        method=AvMethod.READ,
        timeout=timeout,
        authorization=authorization,
    ).bytes()


def write_data(
    entity, data: bytes, timeout=NULL_TIMEOUT, authorization=NULL_AUTHORIZATION
) -> None:
    """Write an entity's data"""
    Verify.bytes(data)
    invoke_entity(
        entity=entity,
        method=AvMethod.WRITE,
        value=AvValue(tag=AvTag.DATA, bytes=data),
        timeout=timeout,
        authorization=authorization,
    )


def purge_data(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> None:
    """purge_data(entity, auth"""
    invoke_entity(entity=entity, method=AvMethod.PURGE, authorization=authorization)


def data_count(entity, authorization=NULL_AUTHORIZATION) -> int:
    """Return size of entity's data"""
    return invoke_entity(
        entity=entity, method=AvMethod.COUNT, authorization=authorization
    ).decode_integer()


############################
# Authorization operations #
############################


def authorize_entity(
    entity: AvEntity,
    restrictions: AvParameter = NULL_PARAMETER,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Authorize an an entity"""
    Verify.entity(entity)
    Verify.integer(restrictions)
    Verify.authorization(authority)
    Verify.authorization(authorization)
    api.authorize(
        entity=entity,
        parameter=restrictions,
        authority=authority,
        authorization=authorization,
    )


def deauthorize_entity(
    entity: AvEntity,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    """Deauthorize an an entity"""
    Verify.entity(entity)
    Verify.authorization(authority)
    Verify.authorization(authorization)
    api.deauthorize(entity=entity, authority=authority, authorization=authorization)


def entity_authorization(
    entity: AvEntity,
    index: int = NULL_INDEX,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvAuthorization:
    """Deauthorize an an entity"""
    Verify.entity(entity)
    Verify.natural(index)
    Verify.authorization(authorization)
    return api.authorization(entity=entity, index=index, authorization=authorization)


def entity_authorized(
    entity: AvEntity,
    authority: AvAuthorization = NULL_AUTHORIZATION,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    """Deauthorize an an entity"""
    Verify.entity(entity)
    Verify.authorization(authority)
    Verify.authorization(authorization)
    return api.authorized(
        entity=entity, authority=authority, authorization=authorization
    )


def entity_authorizations(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of authorizations on entity"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.authorizations(entity=entity, authorization=authorization)


##################
# Entity Reports #
##################


def entity_name(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> str:
    """Return the name of the entity, as a string."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.name(entity=entity, authorization=authorization).decode(ENCODING)


def entity_key(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> str:
    """Return the name of the entity, as a string."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.key(entity=entity, authorization=authorization).decode(ENCODING)


def entity_context(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvContext:
    """Return the (AvesTerra) context of the entity."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return AvContext(api.context(entity=entity, authorization=authorization))


def entity_category(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvCategory:
    """Return the (AvesTerra) class of the entity."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return AvCategory(api.category(entity=entity, authorization=authorization))


def entity_class(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvClass:
    """Return the (AvesTerra) class of the entity."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return AvClass(api.klass(entity=entity, authorization=authorization))


def entity_state(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvState:
    """Return the (AvesTerra) class of the entity."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return AvState(api.state(entity=entity, authorization=authorization))


def entity_extinct(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    """Has the entity been deleted?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.extinct(entity=entity, authorization=authorization)


def entity_available(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    """Is entity available?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.available(entity=entity, authorization=authorization)


def entity_activated(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    """Is entity available?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.activated(entity=entity, authorization=authorization)


def entity_locked(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    """Is entity locked?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.locked(entity=entity, authorization=authorization)


def entity_armed(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    """Is entity armed?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.armed(entity=entity, authorization=authorization)


def entity_active(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    """Is entity armed?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.armed(entity=entity, authorization=authorization)


def entity_busy(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> bool:
    """Is entity armed?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.busy(entity=entity, authorization=authorization)


def entity_references(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """What is the reference count of the entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.references(entity=entity, authorization=authorization)


def entity_attachments(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of attachments on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.attachments(entity=entity, authorization=authorization)


def entity_authority(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvAuthorization:
    """Return number of authorizations on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.authority(
        entity=entity, authorization=authorization, authority=authorization
    )


def entity_conditions(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of conditions on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.conditions(entity=entity, authorization=authorization)


def entity_connections(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of connections on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.connections(entity=entity, authorization=authorization)


def entity_elements(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Number of elements in entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.elements(entity=entity, authorization=authorization)


def entity_subscriptions(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of connections on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.subscriptions(entity=entity, authorization=authorization)


def entity_timer(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of timer on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.timer(entity=entity, authorization=authorization)


def entity_elapsed(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of timer on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.elapsed(entity=entity, authorization=authorization)


def entity_blocking(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of timer on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.blocking(entity=entity, authorization=authorization)


def entity_pending(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of timer on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.pending(entity=entity, authorization=authorization)


def entity_waiting(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of timer on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.waiting(entity=entity, authorization=authorization)


def entity_adapting(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of timer on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.adapting(entity=entity, authorization=authorization)


def entity_invoking(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> int:
    """Return number of timer on an entity?"""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.invoking(entity=entity, authorization=authorization)


def entity_server(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvEntity:
    """Determine the server that manages the entity."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.server(entity=entity, authorization=authorization)


def entity_redirection(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvEntity:
    """Return redirection of an entity."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.redirection(entity=entity, authorization=authorization)


def entity_rendezvous(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> str:
    """Return the rendezvous status of an entity."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return api.rendezvous(entity=entity, authorization=authorization)


def entity_timestamp(
    entity: AvEntity, authorization: AvAuthorization = NULL_AUTHORIZATION
):
    """Return the time that the entity was created, as an epoch integer."""
    Verify.entity(entity)
    Verify.authorization(authorization)
    return AvTime.fromtimestamp(
        api.timestamp(entity=entity, authorization=authorization), tz=UTC
    ).replace(microsecond=0)


#####################
# Utility functions #
#####################


def max_async_connections() -> int:
    return api.max_async_connections()


#######################
# Avesterra Functions #
#######################

def retrieve_avesterra(
    server: AvEntity,
    authorization: AvAuthorization,
) -> Dict:
    result = invoke_entity(
        entity=server,
        method=AvMethod.AVESTERRA,
        parameter=TRUE_PARAMETER,
        authorization=authorization,
    )

    avesterra_model: Dict = json.loads(result.decode())
    return avesterra_model
