""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from dataclasses import dataclass
from typing import Union
import avesterra as av


class ValueType:
    """
    Represents the type of a value, as described by https://gitlab.com/groups/ledr/-/wikis/home/Core/Platform/Standard-Adapter-Interface
    Construct instance using the class method corresponding to the tag you want
    """

    tag: av.AvTag
    nested: Union[dict[str, "ValueType"], list["ValueType"], "ValueType", None]

    @classmethod
    def _init(
        cls,
        tag: av.AvTag,
        nested: Union[
            dict[str, "ValueType"], list["ValueType"], "ValueType", None
        ] = None,
    ):
        res = cls()
        res.tag = tag
        res.nested = nested
        return res

    @classmethod
    def null(cls):
        return cls._init(av.AvTag.NULL)

    @classmethod
    def avesterra(cls):
        return cls._init(av.AvTag.AVESTERRA)

    @classmethod
    def boolean(cls):
        return cls._init(av.AvTag.BOOLEAN)

    @classmethod
    def character(cls):
        return cls._init(av.AvTag.CHARACTER)

    @classmethod
    def string(cls):
        return cls._init(av.AvTag.STRING)

    @classmethod
    def text(cls):
        return cls._init(av.AvTag.TEXT)

    @classmethod
    def integer(cls):
        return cls._init(av.AvTag.INTEGER)

    @classmethod
    def float(cls):
        return cls._init(av.AvTag.FLOAT)

    @classmethod
    def entity(cls):
        return cls._init(av.AvTag.ENTITY)

    @classmethod
    def time(cls):
        return cls._init(av.AvTag.TIME)

    @classmethod
    def web(cls):
        return cls._init(av.AvTag.WEB)

    @classmethod
    def interchange(cls):
        return cls._init(av.AvTag.INTERCHANGE)

    @classmethod
    def data(cls):
        return cls._init(av.AvTag.DATA)

    @classmethod
    def exception(cls):
        return cls._init(av.AvTag.EXCEPTION)

    @classmethod
    def operator(cls):
        return cls._init(av.AvTag.OPERATOR)

    @classmethod
    def function(cls):
        return cls._init(av.AvTag.FUNCTION)

    @classmethod
    def locutor(cls):
        return cls._init(av.AvTag.LOCUTOR)

    @classmethod
    def authorization(cls):
        return cls._init(av.AvTag.AUTHORIZATION)

    @classmethod
    def duration(cls):
        return cls._init(av.AvTag.DURATION)

    @classmethod
    def variable(cls, content: "ValueType"):
        return cls._init(av.AvTag.VARIABLE, content)

    @classmethod
    def array(cls, content: list["ValueType"]):
        return cls._init(av.AvTag.ARRAY, content)

    @classmethod
    def aggregate(cls, content: dict[str, "ValueType"]):
        return cls._init(av.AvTag.AGGREGATE, content)

    def to_value(self) -> av.AvValue:
        match self.tag:
            case av.AvTag.NULL:
                return av.AvValue.encode_null()
            case av.AvTag.AVESTERRA:
                return av.AvValue.encode_avesterra()
            case av.AvTag.BOOLEAN:
                return av.AvValue.encode_boolean(False)
            case av.AvTag.CHARACTER:
                return av.AvValue.encode_character("a")
            case av.AvTag.STRING:
                return av.AvValue.encode_string("")
            case av.AvTag.TEXT:
                return av.AvValue.encode_text("")
            case av.AvTag.INTEGER:
                return av.AvValue.encode_integer(0)
            case av.AvTag.FLOAT:
                return av.AvValue.encode_float(0)
            case av.AvTag.ENTITY:
                return av.AvValue.encode_entity(av.NULL_ENTITY)
            case av.AvTag.TIME:
                return av.AvValue.encode_time(av.AvTime.fromtimestamp(0))
            case av.AvTag.WEB:
                return av.AvValue.encode_web("")
            case av.AvTag.INTERCHANGE:
                return av.AvValue.encode_interchange("{}")
            case av.AvTag.DATA:
                return av.AvValue.encode_data(bytes())
            case av.AvTag.EXCEPTION:
                return av.AvValue.encode_exception(av.AvError.NULL, "")
            case av.AvTag.OPERATOR:
                return av.AvValue.encode_operator(av.AvOperator.NULL)
            case av.AvTag.FUNCTION:
                return av.AvValue.encode_function(av.NULL_ENTITY)
            case av.AvTag.LOCUTOR:
                return av.AvValue.encode_locutor(av.AvLocutor())
            case av.AvTag.AUTHORIZATION:
                return av.AvValue.encode_authorization(av.NULL_AUTHORIZATION)
            case av.AvTag.DURATION:
                return av.AvValue.encode_duration(0)
            case av.AvTag.VARIABLE:
                assert isinstance(self.nested, ValueType)
                return av.AvValue.encode_variable("", self.nested.to_value())
            case av.AvTag.AGGREGATE:
                assert isinstance(self.nested, dict)
                return av.AvValue.encode_aggregate(
                    {key: valtype.to_value() for key, valtype in self.nested.items()}
                )
            case av.AvTag.ARRAY:
                assert isinstance(self.nested, list)
                return av.AvValue.encode_array(
                    [valtype.to_value() for valtype in self.nested]
                )
            case _:
                assert (
                    False
                ), "Value type is either not supported or we forgot to update this"

    @classmethod
    def from_value(cls, val: av.AvValue):
        match val.tag():
            case av.AvTag.NULL:
                return ValueType.null()
            case av.AvTag.AVESTERRA:
                return ValueType.avesterra()
            case av.AvTag.BOOLEAN:
                return ValueType.boolean()
            case av.AvTag.CHARACTER:
                return ValueType.character()
            case av.AvTag.STRING:
                return ValueType.string()
            case av.AvTag.TEXT:
                return ValueType.text()
            case av.AvTag.INTEGER:
                return ValueType.integer()
            case av.AvTag.FLOAT:
                return ValueType.float()
            case av.AvTag.ENTITY:
                return ValueType.entity()
            case av.AvTag.TIME:
                return ValueType.time()
            case av.AvTag.WEB:
                return ValueType.web()
            case av.AvTag.INTERCHANGE:
                return ValueType.interchange()
            case av.AvTag.DATA:
                return ValueType.data()
            case av.AvTag.EXCEPTION:
                return ValueType.exception()
            case av.AvTag.OPERATOR:
                return ValueType.operator()
            case av.AvTag.FUNCTION:
                return ValueType.function()
            case av.AvTag.LOCUTOR:
                return ValueType.locutor()
            case av.AvTag.AUTHORIZATION:
                return ValueType.authorization()
            case av.AvTag.DURATION:
                return ValueType.duration()
            case av.AvTag.VARIABLE:
                (_, nestedval) = val.decode_variable()
                return ValueType.variable(ValueType.from_value(nestedval))
            case av.AvTag.AGGREGATE:
                arr = val.decode_aggregate()
                return ValueType.aggregate(
                    {
                        key: ValueType.from_value(nestedval)
                        for key, nestedval in arr.items()
                    }
                )
            case av.AvTag.ARRAY:
                arr = val.decode_array()
                return ValueType.array(
                    [ValueType.from_value(nestedval) for nestedval in arr]
                )
            case _:
                assert (
                    False
                ), "Value type is either not supported or we forgot to update this"


@dataclass
class Method:
    name: str
    description: str
    base: av.AvLocutorOpt
    args: list[av.AvAspect]
    value_in: ValueType = ValueType.null()
    value_out: ValueType = ValueType.null()


@dataclass
class Interface:
    name: str
    version: str
    description: str
    methods: list[Method]

    @staticmethod
    def from_avialmodel(model: av.AvialModel) -> "Interface":
        name = model.facts[av.AvAttribute.NAME].value.decode()
        if not isinstance(name, str):
            name = ""
        version = model.facts[av.AvAttribute.VERSION].value.decode()
        if not isinstance(version, str):
            version = ""
        description = model.facts[av.AvAttribute.DESCRIPTION].value.decode()
        if not isinstance(description, str):
            description = ""
        methods = []
        for facet in model.facts[av.AvAttribute.METHOD].facets:
            mname = facet.name
            mdescription = facet.value.decode()
            if not isinstance(mdescription, str):
                mdescription = ""
            mbase = facet.factors["base"].value.decode_locutor()
            margs = []
            for arg in facet.factors["args"].value.decode_array():
                margs.append(arg.decode_locutor().aspect)
            mvalue_in = facet.factors["value_in"].value
            mvalue_out = facet.factors["value_out"].value

            methods.append(
                Method(
                    name=mname,
                    description=mdescription,
                    base=mbase.to_locutoropt(keep_null=True),
                    args=margs,
                    value_in=ValueType.from_value(mvalue_in),
                    value_out=ValueType.from_value(mvalue_out),
                )
            )

        return Interface(name, version, description, methods)

    def to_avialmodel(self) -> av.AvialModel:
        model = av.AvialModel()
        model.facts[av.AvAttribute.NAME].value = av.AvValue.encode_text(self.name)
        model.facts[av.AvAttribute.VERSION].value = av.AvValue.encode_string(
            self.version
        )
        model.facts[av.AvAttribute.DESCRIPTION].value = av.AvValue.encode_text(
            self.description
        )
        for method in self.methods:
            facet = model.facts[av.AvAttribute.METHOD].facets[method.name]
            facet.value = av.AvValue.encode_text(method.description)
            facet.factors["base"].value = av.AvValue.encode_locutor(
                method.base.to_locutor()
            )
            facet.factors["args"].value = av.AvValue.encode_array(
                [
                    av.AvValue.encode_locutor(av.AvLocutor(aspect=arg))
                    for arg in method.args
                ]
            )
            facet.factors["value_in"].value = method.value_in.to_value()
            facet.factors["value_out"].value = method.value_out.to_value()
        return model
