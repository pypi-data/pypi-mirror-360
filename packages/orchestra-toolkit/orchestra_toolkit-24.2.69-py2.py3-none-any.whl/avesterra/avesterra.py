"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from __future__ import annotations

import builtins
import functools
import re
import uuid

LARGEST_32_BIT_INT = 4_294_967_295
LARGEST_64_BIT_INT = 18_446_744_073_709_551_615
ENCODING = "utf-8"

##########################
# Main AvesTerra classes #
##########################


class AvEntity:
    """A Python type that represents an AvesTerra Entity

    Attributes
    __________
    pid : int
        Used to specify the network on which an entity exists; pid=0 refers to an entity that exists on the local network, relative to the Avial Connection.
    hid : int
        Used to specify the host on which an entity exists; hid=0 refers to an entity that exists on the local host, relative to the Avial Connection.
    uid : int
        Used to specify the entity unique identifier of an entity on an individual AvesTerra host; uid 1 - 200000 is reserved for redirections and uid 0 refers to the AvesTerra entity that stores information about an individual AvesTerra server

    """

    pid: int
    hid: int
    uid: int

    def __init__(self, pid: int, hid: int, uid: int):
        if 0 <= pid <= LARGEST_32_BIT_INT:
            self.pid = pid
        else:
            raise EntityError(
                "Public host ID {} either too small or too big".format(pid)
            )

        if 0 <= hid <= LARGEST_32_BIT_INT:
            self.hid = hid
        else:
            raise EntityError(
                "Local host ID {} either too small or too big".format(hid)
            )

        if 0 <= uid <= LARGEST_64_BIT_INT:
            self.uid = uid
        else:
            raise EntityError(
                "Unique entity ID {} either too small or too big".format(uid)
            )

    def to_bytes(self) -> bytearray:
        """Creates a bytearray representation from the AvEntity instance

        Examples
        ________
        A really cool example

        >>> AvEntity.from_str("<100|1000|10000>").to_bytes()

        Returns
        _______
        bytearray
            Bytearray representation of the AvesTerra entity

        """
        entity_bytes = bytearray(0)
        entity_bytes.extend(self.pid.to_bytes(4, byteorder="little"))
        entity_bytes.extend(self.hid.to_bytes(4, byteorder="little"))
        entity_bytes.extend(self.uid.to_bytes(8, byteorder="little"))
        return entity_bytes

    @staticmethod
    def from_bytes(entity_bytes: bytes) -> AvEntity:
        """Converts given ``entity_bytes`` into a Python AvEntity object

        Parameters
        __________
        entity_bytes : bytes
            Bytes representation of an AvesTerra Entity

        Examples
        ________

        >>> pid, hid, uid = 1000, 900, 12038219 # random
        >>> entity_bytearray = bytearray()
        >>> entity_bytearray.extend(pid.to_bytes(4, byteorder="little"))
        >>> entity_bytearray.extend(hid.to_bytes(4, byteorder="little"))
        >>> entity_bytearray.extend(uid.to_bytes(8, byteorder="little"))
        >>> AvEntity.from_bytes(entity_bytes=entity_bytearray)
        <1000|900|12038219>

        Returns
        _______
        AvEntity
            AvEntity representation of the given ``entity_bytes``

        """
        return AvEntity(
            pid=int.from_bytes(entity_bytes[0:4], byteorder="little"),
            hid=int.from_bytes(entity_bytes[4:8], byteorder="little"),
            uid=int.from_bytes(entity_bytes[8:16], byteorder="little"),
        )

    @staticmethod
    def from_str(entity_str: str) -> AvEntity:
        """Converts given ``entity_str`` into a Python AvEntity object

        Parameters
        __________
        entity_str : str
            String representation of an AvesTerra Entity

        Examples
        ________

        >>> from avesterra.avesterra import AvEntity
        >>> entity = AvEntity.from_str("<0|1020|1048302>")
        >>> print(entity)
        >>> print(f"PID: {entity.pid}, HID: {entity.hid}, UID: {entity.uid}")
        <0|1020|1048302>
        PID: 0, HID: 1020, UID: 1048302

        Returns
        _______
        AvEntity
            AvEntity from parsed from ``entity_str``

        """
        split_entity_str = entity_str.replace("<", "").replace(">", "").split("|")
        pid_str: str = split_entity_str[0]
        hid_str: str = split_entity_str[1]
        uid_str: str = split_entity_str[2]
        return AvEntity(int(pid_str), int(hid_str), int(uid_str))

    def __repr__(self) -> str:
        """Creates an object representation of an AvEntity

        Examples
        ________

        >>> from avesterra.avesterra import AvEntity
        >>> entity = AvEntity.from_str("<0|1020|1048302>")
        >>> repr(entity)
        AvEntity(0, 1020, 1048302)

        Returns
        _______
        str
            Pythonic object representation of an AvEntity

        """
        return "Entity({}, {}, {})".format(self.pid, self.hid, self.uid)

    def __str__(self):
        """Creates an AvesTerra Entity string from an AvEntity instance

        Examples
        ________
        >>> entity = AvEntity(1029, 1000, 982628)
        >>> str(entity)
        <1029|1000|982628>

        Returns
        _______
        str
            AvesTerra entity string

        """
        return "<{}|{}|{}>".format(self.pid, self.hid, self.uid)

    def __eq__(self, other: object) -> bool:
        """Returns true if the PID, HID, and PID of self and other are the same

        Parameters
        __________
        other : object
            The object to compare ``self`` with; should be of type AvEntity

        Raises
        ______
        ValueError
            if other is not of type AvEntity

        Examples
        ________

        >>> AvEntity.from_str("<0|0|10002>") == AvEntity.from_str("<0|0|10002>")
        True

        >>> AvEntity.from_str("<0|0|10002>") == AvEntity.from_str("<0|0|88888>")
        False

        Returns
        _______
        bool
            True if ``other`` and ``self`` have the same combination of ``pid``, ``hid``, ``uid``

        """
        if isinstance(other, AvEntity):
            return (
                self.pid == other.pid
                and self.hid == other.hid
                and self.uid == other.uid
            )
        elif isinstance(other, str):
            return str(self) == other
        else:
            raise ValueError(f"Cannot compare AvEntity with type {type(other)}")

    def __ne__(self, other):
        """Returns true if the combination of PID, HID, and PID of ``self`` and ``other`` are not the same

        Parameters
        __________
        other : object
            The object to compare ``self`` with; should be of type AvEntity

        Examples
        ________

        >>> AvEntity.from_str("<0|0|10002>") != AvEntity.from_str("<0|0|10002>")
        False

        >>> AvEntity.from_str("<0|0|10002>") != AvEntity.from_str("<0|0|88888>")
        True

        Raises
        ______
        ValueError
            if ``other`` is not of type AvEntity

        Returns
        _______
        bool
            True if ``other`` and ``self`` have different combinations of ``pid``, ``hid``, ``uid``

        """
        if isinstance(other, AvEntity):
            return not (
                self.pid == other.pid
                and self.hid == other.hid
                and self.uid == other.uid
            )
        elif isinstance(other, str):
            return str(self) != other
        else:
            raise ValueError(f"Cannot compare AvEntity with type {type(other)}")

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def dict(self):
        return {"ENTITY": str(self)}


class AvAuthorization(uuid.UUID):
    """A Python type that represents an AvesTerra Authorization code, which is essentially a UUID from RFC 4122, look here <https://datatracker.ietf.org/doc/html/rfc4122>"""

    def __init__(self, hex: str | None = None, *args, **kwargs) -> None:
        if hex == "********-****-****-****-************":
            return super().__init__(hex="ffffffff-ffff-ffff-ffff-ffffffffffff")
        return super().__init__(hex=hex, *args, **kwargs)

    @staticmethod
    def simple(digits: str) -> AvAuthorization:
        """Convert a string of hex digits, witohut dashes, into an AvesTerra Authorization

        Parameters
        __________
        digits : str
            String of hex digits; no dashes in between and the hex string shouldn't represent a number larger than 128 bits

        Examples
        ________
        >>> auth_digits = "69463cc29bcf4f879e4c9b9ed3f73810"# random
        Replace dashes with empty spaces, to create a dash-less hex string
        >>> AvAuthorization(auth_digits.replace("-", ""))
        AvAuthorization("69463cc2-9bcf-4f87-9e4c-9b9ed3f73810")

        Returns
        _______
        AvAuthorization
            Authorization represented by the inputted hex digits

        """
        return AvAuthorization(int=int(digits, 16))

    @staticmethod
    def random() -> AvAuthorization:
        """Randomly generate AvAuthorization

        Examples
        ________
        >>> AvAuthorization.random()
        AvAuthorization("69463cc2-9bcf-4f87-9e4c-9b9ed3f73810") #random

        Returns
        _______
        AvAuthorization
            Randomly genrated AvAuthorization

        """
        return AvAuthorization(str(uuid.uuid4()))


# Avial 4.12 Used to represent permissions extracted, or to be applied, to an Permission
class AvMask:
    @property
    def a(self) -> bool:
        """AvesTerra permission"""
        return self._a

    @property
    def r(self) -> bool:
        """Read permission"""
        return self._r

    @property
    def w(self) -> bool:
        """Write permission"""
        return self._w

    @property
    def e(self) -> bool:
        """Execute permission"""
        return self._e

    @property
    def d(self) -> bool:
        """Delete permission"""
        return self._d

    def __init__(
        self,
        a: bool = False,
        r: bool = False,
        w: bool = False,
        e: bool = False,
        d: bool = False,
        string: str = "",
    ):
        if string:
            if len(string) != 5:
                raise builtins.ValueError(
                    f"badly formed AvMask string, expected length 5 but found {len(string)}"
                )
            chars = "ARWED"
            for i, c in enumerate(string):
                if c != chars[i] and c != "_":
                    raise builtins.ValueError(
                        f"badly formed AvMask string, invalid character '{c}' at index {i}, expected either '{chars[i]}' or '_'"
                    )
            self._a = string[0] == "A"
            self._r = string[1] == "R"
            self._w = string[2] == "W"
            self._e = string[3] == "E"
            self._d = string[4] == "D"
        else:
            self._a = a
            self._r = r
            self._w = w
            self._e = e
            self._d = d

    def __str__(self):
        a = "A" if self.a else "_"
        r = "R" if self.r else "_"
        w = "W" if self.w else "_"
        e = "E" if self.e else "_"
        d = "D" if self.d else "_"
        return a + r + w + e + d

    def __repr__(self) -> str:
        return f"AvMask({str(self)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AvMask):
            return False
        return str(self) == str(other)

    def __bool__(self):
        """Only false if no permissions are set"""
        return self.a or self.r or self.w or self.e or self.d

    def __and__(self, other: AvMask) -> AvMask:
        return AvMask(
            a=self.a and other.a,
            r=self.r and other.r,
            w=self.w and other.w,
            e=self.e and other.e,
            d=self.d and other.d,
        )

    def __or__(self, other: AvMask) -> AvMask:
        return AvMask(
            a=self.a or other.a,
            r=self.r or other.r,
            w=self.w or other.w,
            e=self.e or other.e,
            d=self.d or other.d,
        )


AvesTerra = AvMask(a=True)
"""The AvesTerra permission mask"""
Read = AvMask(r=True)
"""The Read permission mask"""
Write = AvMask(w=True)
"""The Write permission mask"""
Execute = AvMask(e=True)
"""The Execute permission mask"""
Delete = AvMask(d=True)
"""The Delete permission mask"""

RWED = Read | Write | Execute | Delete
ARWED = AvesTerra | RWED


def decode_credential(credential: AvAuthorization) -> tuple[AvAuthorization, AvMask]:
    mask = AvMask(
        a=bool(credential.bytes[8] & 0x40),
        r=bool(credential.bytes[6] & 0x10),
        w=bool(credential.bytes[6] & 0x20),
        e=bool(credential.bytes[6] & 0x40),
        d=bool(credential.bytes[6] & 0x80),
    )

    b = bytearray(credential.bytes)
    b[6] = 0x40 + (0x0F & b[6])
    b[8] = 0x80 + (0x3F & b[8])
    return AvAuthorization(bytes=bytes(b)), mask


def encode_credential(auth: AvAuthorization, mask: AvMask) -> AvAuthorization:
    b = bytearray(auth.bytes)

    b[6] = 0x0F & b[6]
    b[8] = 0x3F & b[8]
    if mask.a:
        b[8] |= 0x40
    if mask.r:
        b[6] |= 0x10
    if mask.w:
        b[6] |= 0x20
    if mask.e:
        b[6] |= 0x40
    if mask.d:
        b[6] |= 0x80
    return AvAuthorization(bytes=bytes(b))


#######################
# AvesTerra constants #
#######################

NULL_ENTITY = AvEntity(0, 0, 0)
NULL_DATA = b""
NULL_INSTANCE = 0
NULL_OFFSET = 0
NULL_NAME = ""
NULL_KEY = ""
NULL_PARAMETER = 0
NULL_RESULTANT = 0
NULL_PRECEDENCE = 0
NULL_INDEX = 0
NULL_COUNT = 0
NULL_MODE = 0
NULL_TIME = 0
NULL_TIMEOUT = 0
NULL_ADDRESS = 0


NULL_AUTHORIZATION = AvAuthorization("00000000-0000-0000-0000-000000000000")
NO_AUTHORIZATION = AvAuthorization("FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF")
VIEW_AUTHORIZATION = AvAuthorization("00000000-0000-0000-0000-000000000001")
VERIFY_AUTHORIZATION = AvAuthorization("00000000-0000-0000-0000-000000000002")

##########
# Errors #
##########


class AvesTerraError(Exception):
    """Some sort of error with the AvesTerra"""

    def __init__(self, message):
        self.message = message


class MessageError(AvesTerraError):
    pass


class AvialError(AvesTerraError):
    pass


class EntityError(AvesTerraError):
    pass


class OutletError(AvesTerraError):
    pass


class TimeoutError(AvesTerraError):
    pass


class AuthorizationError(AvesTerraError):
    pass


class ExecutionError(AvesTerraError):
    pass


class AdapterError(AvesTerraError):
    pass


class SubscriberError(AvesTerraError):
    pass


class NetworkError(AvesTerraError):
    pass


class ApplicationError(AvesTerraError):
    pass


class BypassError(AvesTerraError):
    pass


class ForwardError(AvesTerraError):
    pass


class ValueError(AvesTerraError):
    pass


class ShutdownError(AvesTerraError):
    pass


class TaxonomyError(AvesTerraError):
    pass


class CommunicationError(AvesTerraError):
    pass


class MessageTooLargeError(AvesTerraError):
    pass


# Perhaps this should just be an init method of Entity?
def entity_of(s):
    match = re.fullmatch(_entity_regex_pattern(), s)
    if match:
        return AvEntity.from_str(match.string)
    else:
        raise EntityError("Bad entity ID: {}".format(s))


@functools.lru_cache(maxsize=1)
def _entity_regex_pattern():
    """Return the regex pattern for entities."""
    return re.compile(r"<\d+\|\d+\|\d+>")


def is_entity(thing):
    """Returns whether thing is an entity or can be interpreted as one."""
    try:
        return thing.is_entity()
    except Exception:
        try:
            return re.fullmatch(_entity_regex_pattern(), thing) is not None
        except Exception:
            return False
