""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import socket
import struct
import queue
import collections
import threading
import time
import ssl
import os.path
import traceback
import avesterra.avesterra as avesterra
from enum import IntEnum
from socket import SocketType
from ipaddress import ip_address
from avesterra.avesterra import AvEntity, AvAuthorization, NULL_AUTHORIZATION


############################
# HGTP constants and enums #
############################


# HGTP message codes:
class Command(IntEnum):
    NULL = 0  # Avesterra 7.0: 0 was previously BYE
    CREATE = 1
    DELETE = 2
    CONNECT = 3
    DISCONNECT = 4
    ATTACH = 5
    DETACH = 6
    INVOKE = 7
    INQUIRE = 8
    CALL = 9
    ADAPT = 10
    SYNC = 11
    CONNECTION = 12
    ATTACHMENT = 13
    REFERENCE = 14
    DEREFERENCE = 15
    ACTIVATE = 16
    DEACTIVATE = 17
    PUBLISH = 18
    SUBSCRIBE = 19
    NOTIFY = 20
    UNSUBSCRIBE = 21
    SUBSCRIPTION = 22
    WAIT = 23
    FLUSH = 24
    ATTACHED = 25
    CONNECTED = 26
    SUBSCRIBED = 27
    AUTHORIZE = 28
    DEAUTHORIZE = 29
    AUTHORIZED = 30
    AUTHORIZATION = 31
    REPORT = 32
    LOCK = 33
    UNLOCK = 34
    CHANGE = 35
    INSERT = 36
    REMOVE = 37
    REPLACE = 38
    ERASE = 39
    FIND = 40
    ELEMENT = 41
    LENGTH = 42
    ARM = 43
    DISARM = 44
    START = 45
    STOP = 46
    RESET = 47
    FETCH = 48
    SET = 49
    CLEAR = 50
    TEST = 51
    EXECUTE = 52
    HALT = 53
    SCHEDULE = 54
    REDIRECT = 55
    CONDITION = 56
    TUNNEL = 57
    BYE = 58  # Avesterra 7.0: BYE was 0, now it is 58
    LABEL = 59
    VARIABLE = 60  # AvesTerra 8.0
    FORCE = 61  # AvesTerra 8.0


class Report(IntEnum):
    NULL = 0
    AVAILABLE = 1
    NAME = 2
    CATEGORY = 3
    CLASS = 4
    ACTIVATED = 5
    CONNECTIONS = 6
    ATTACHMENTS = 7
    SUBSCRIPTIONS = 8
    AUTHORIZATIONS = 9
    REDIRECTION = 10
    REFERENCES = 11
    TIMESTAMP = 12
    SERVER = 13
    LOCAL = 14
    GATEWAY = 15
    HOSTNAME = 16
    VERSION = 17
    EXTINCT = 18
    PENDING = 19
    LOCKED = 20
    RENDEZVOUS = 21
    STATUS = 22
    CONTEXT = 23
    CLOCK = 24
    TIMER = 25
    ELAPSED = 26
    ARMED = 27
    ACTIVE = 28
    STATE = 29
    CONDITIONS = 30
    ELEMENTS = 31
    KEY = 32
    BUSY = 33
    BLOCKING = 34
    WAITING = 35
    ADAPTING = 36
    INVOKING = 37
    INTERNET = 38
    AUTHORITY = 39
    ADDRESS = 40  # Avesterra 7.0


# same as error_type in Avial.HGTP in reference implementation
class HGTPException(IntEnum):
    NULL = 0
    AVESTERRA = 1
    ENTITY = 2
    OUTLET = 3
    NETWORK = 4
    TIMEOUT = 5
    AUTHORIZATION = 6
    ADAPTER = 7
    SUBSCRIBER = 8
    APPLICATION = 9
    BYPASS = 10
    FORWARD = 11
    VALUE = 12
    MESSAGE = 13
    EXECUTION = 14
    SHUTDOWN = 15  # Avial V3.4


PORT = 20057

MESSAGE_SIZE_LIMIT_IN_BYTES = 1_048_575


class HGTPFrame:
    command_code: int
    error_code: int
    version_code: int
    report_code: int
    method_code: int
    attribute_code: int
    event_code: int
    mode_code: int
    category_code: int
    class_code: int
    context_code: int
    aspect_code: int
    state_code: int
    precedence: int
    tag_code: int
    condition_code: int

    instance: int
    offset: int
    time: int
    index: int
    count: int
    extension: int
    parameter: int
    resultant: int
    timeout: int

    entity: AvEntity
    outlet: AvEntity
    auxiliary: AvEntity
    ancillary: AvEntity

    authorization: AvAuthorization
    authority: AvAuthorization

    name_count: int
    name: bytes

    key_count: int
    key: bytes

    bytes_count: int
    _bytes: bytes

    data_extension: bytes

    def __init__(self):
        self.command_code = 0
        self.error_code = 0
        self.version_code = 0
        self.report_code = 0
        self.method_code = 0
        self.attribute_code = 0
        self.event_code = 0
        self.mode_code = 0
        self.category_code = 0
        self.class_code = 0
        self.context_code = 0
        self.aspect_code = 0
        self.state_code = 0
        self.precedence = 0
        self.tag_code = 0
        self.condition_code = 0

        self.instance = 0
        self.offset = 0
        self.time = 0
        self.index = 0
        self.count = 0
        self.extension = 0
        self.parameter = 0
        self.resultant = 0
        self.timeout = 0

        self.entity = AvEntity(0, 0, 0)
        self.outlet = AvEntity(0, 0, 0)
        self.auxiliary = AvEntity(0, 0, 0)
        self.ancillary = AvEntity(0, 0, 0)

        self.authorization = NULL_AUTHORIZATION
        self.authority = NULL_AUTHORIZATION

        self.name_count = 0
        self.name = bytes(0)

        self.key_count = 0
        self.key = bytes(0)

        self.bytes_count = 0
        self._bytes = b""

        self.data_extension = b""

    @staticmethod
    def from_bytes(frame: bytes):
        hgtp_obj: HGTPFrame = HGTPFrame()
        hgtp_obj.command_code = int.from_bytes(frame[0:2], byteorder="little")
        hgtp_obj.error_code = int.from_bytes(frame[2:4], byteorder="little")
        hgtp_obj.version_code = int.from_bytes(frame[4:6], byteorder="little")
        hgtp_obj.report_code = int.from_bytes(frame[6:8], byteorder="little")
        hgtp_obj.method_code = int.from_bytes(frame[8:10], byteorder="little")
        hgtp_obj.attribute_code = int.from_bytes(frame[10:12], byteorder="little")
        hgtp_obj.event_code = int.from_bytes(frame[12:14], byteorder="little")
        hgtp_obj.mode_code = int.from_bytes(frame[14:16], byteorder="little")
        hgtp_obj.category_code = int.from_bytes(frame[16:18], byteorder="little")
        hgtp_obj.class_code = int.from_bytes(frame[18:20], byteorder="little")
        hgtp_obj.context_code = int.from_bytes(frame[20:22], byteorder="little")
        hgtp_obj.aspect_code = int.from_bytes(frame[22:24], byteorder="little")
        hgtp_obj.state_code = int.from_bytes(frame[24:26], byteorder="little")
        hgtp_obj.precedence = int.from_bytes(frame[26:28], byteorder="little")
        hgtp_obj.tag_code = int.from_bytes(frame[28:30], byteorder="little")
        hgtp_obj.condition_code = int.from_bytes(frame[30:32], byteorder="little")

        hgtp_obj.instance = int.from_bytes(frame[32:36], byteorder="little")
        hgtp_obj.offset = int.from_bytes(frame[36:40], byteorder="little")
        hgtp_obj.time = int.from_bytes(frame[40:48], byteorder="little")
        hgtp_obj.index = int.from_bytes(frame[48:56], byteorder="little")
        hgtp_obj.count = int.from_bytes(frame[56:64], byteorder="little")
        hgtp_obj.extension = int.from_bytes(frame[64:72], byteorder="little")
        hgtp_obj.parameter = int.from_bytes(frame[72:80], byteorder="little")
        hgtp_obj.resultant = int.from_bytes(frame[80:88], byteorder="little")
        hgtp_obj.timeout = int.from_bytes(frame[88:96], byteorder="little")

        # 64 Bytes Reserved
        hgtp_obj.entity = AvEntity.from_bytes(frame[160:176])
        hgtp_obj.outlet = AvEntity.from_bytes(frame[176:192])
        hgtp_obj.auxiliary = AvEntity.from_bytes(frame[192:208])
        hgtp_obj.ancillary = AvEntity.from_bytes(frame[208:224])

        hgtp_obj.authorization = AvAuthorization(bytes=frame[224:240])
        hgtp_obj.authority = AvAuthorization(bytes=frame[240:256])

        hgtp_obj.name_count = int.from_bytes(frame[256:257], byteorder="little")
        hgtp_obj.name = frame[257 : 257 + hgtp_obj.name_count]

        hgtp_obj.key_count = int.from_bytes(frame[512:513], byteorder="little")
        hgtp_obj.key = frame[513 : 513 + hgtp_obj.key_count]

        hgtp_obj.bytes_count = int.from_bytes(frame[768:769], byteorder="little")
        hgtp_obj._bytes = frame[769 : 769 + hgtp_obj.bytes_count]

        return hgtp_obj

    def load_bytes(self, bytes: bytes):
        if len(bytes) > 255:
            self.bytes_count = 0
            self._bytes = bytearray(255)
            self.extension = len(bytes)
            self.data_extension = bytes
        else:
            self.bytes_count = len(bytes)
            self._bytes = bytes
            self.extension = 0
            self.data_extension = b""

    def build_frame_bytes(self) -> bytearray:
        frame: bytearray = bytearray(0)
        frame.extend(self.command_code.to_bytes(2, byteorder="little"))
        frame.extend(self.error_code.to_bytes(2, byteorder="little"))
        frame.extend(self.version_code.to_bytes(2, byteorder="little"))
        frame.extend(self.report_code.to_bytes(2, byteorder="little"))
        frame.extend(self.method_code.to_bytes(2, byteorder="little"))
        frame.extend(self.attribute_code.to_bytes(2, byteorder="little"))
        frame.extend(self.event_code.to_bytes(2, byteorder="little"))
        frame.extend(self.mode_code.to_bytes(2, byteorder="little"))
        frame.extend(self.category_code.to_bytes(2, byteorder="little"))
        frame.extend(self.class_code.to_bytes(2, byteorder="little"))
        frame.extend(self.context_code.to_bytes(2, byteorder="little"))
        frame.extend(self.aspect_code.to_bytes(2, byteorder="little"))
        frame.extend(self.state_code.to_bytes(2, byteorder="little"))
        frame.extend(self.precedence.to_bytes(2, byteorder="little"))

        frame.extend(self.tag_code.to_bytes(2, byteorder="little"))
        frame.extend(self.condition_code.to_bytes(2, byteorder="little"))

        frame.extend(self.instance.to_bytes(4, byteorder="little"))
        frame.extend(self.offset.to_bytes(4, byteorder="little"))
        frame.extend(self.time.to_bytes(8, byteorder="little"))
        frame.extend(self.index.to_bytes(8, byteorder="little"))
        frame.extend(self.count.to_bytes(8, byteorder="little"))
        frame.extend(self.extension.to_bytes(8, byteorder="little"))
        frame.extend(self.parameter.to_bytes(8, byteorder="little"))
        frame.extend(self.resultant.to_bytes(8, byteorder="little"))
        frame.extend(self.timeout.to_bytes(8, byteorder="little"))

        frame.extend(b"\0" * 64)

        frame.extend(self.entity.to_bytes())
        frame.extend(self.outlet.to_bytes())
        frame.extend(self.auxiliary.to_bytes())
        frame.extend(self.ancillary.to_bytes())

        frame.extend(self.authorization.bytes)
        frame.extend(self.authority.bytes)

        frame.extend(self.name_count.to_bytes(1, byteorder="little"))
        frame.extend(self.name + bytes(255 - len(self.name)))

        frame.extend(self.key_count.to_bytes(1, byteorder="little"))
        frame.extend(self.key + bytes(255 - len(self.key)))

        frame.extend(self.bytes_count.to_bytes(1, byteorder="little"))
        frame.extend(self._bytes + bytes(255 - len(self._bytes)))

        if self.extension > 0:
            frame.extend(self.data_extension)

        return frame

    def __str__(self):
        str_frame = ""

        str_frame += "----------------------------------\n"
        str_frame += "{}|{} [command_code, error_code]\n".format(
            str(self.command_code), str(self.error_code)
        )
        str_frame += "{}|{} [version_code, report_code]\n".format(
            str(self.version_code), str(self.report_code)
        )
        str_frame += "{}|{} [method_code, attribute_code]\n".format(
            str(self.method_code), str(self.attribute_code)
        )
        str_frame += "{}|{} [event_code, mode_code]\n".format(
            str(self.event_code), str(self.mode_code)
        )
        str_frame += "{}|{} [category_code, class_code]\n".format(
            str(self.category_code), str(self.class_code)
        )
        str_frame += "{}|{} [context_code, aspect_code]\n".format(
            str(self.context_code), str(self.aspect_code)
        )
        str_frame += "{}|{} [state_code, precedence_code]\n".format(
            str(self.state_code), str(self.precedence)
        )
        str_frame += "{}|{} [tag_code, condition_code]\n".format(
            str(self.tag_code), str(self.condition_code)
        )

        str_frame += "{}|{} [instance, offset]\n".format(
            str(self.instance), str(self.offset)
        )
        str_frame += "{} [time]\n".format(str(self.instance))
        str_frame += "{}|{} [index, count]\n".format(str(self.index), str(self.count))
        str_frame += "{}|{} [extension, parameter]\n".format(
            str(self.extension), str(self.parameter)
        )
        str_frame += "{}|{} [resultant, timeout]\n".format(
            str(self.resultant), str(self.timeout)
        )

        str_frame += "RESERVED: 64 Bytes\n"

        str_frame += "{}|{} [authorization, authority]\n".format(
            str(self.authorization), str(self.authority)
        )

        str_frame += "{} [entity]\n".format(str(self.entity))
        str_frame += "{} [outlet]\n".format(str(self.outlet))
        str_frame += "{} [auxiliary]\n".format(str(self.auxiliary))
        str_frame += "{} [ancillary]\n".format(str(self.ancillary))

        str_frame += "{} [name]\n".format(str(self.name))
        str_frame += "{} [key]\n".format(str(self.key))
        str_frame += "{} [bytes]\n".format(str(self._bytes))
        str_frame += "{} [extension]\n".format(str(self.data_extension))
        str_frame += "----------------------------------\n"

        return str_frame


##################
# HGTP interface #
##################


def initialize(
    server: str, directory: str, socket_count: int = 16, max_timeout: int = 360
):
    # Allocate esources to communicate with AvesTerra server
    global _socket_pool
    # global _address
    # To do: check whether existing _socket_pool points to same server
    # if not: raise error

    socket_pool_alive: bool = False
    try:
        if _socket_pool.alive():
            socket_pool_alive = True
    except NameError:
        pass
    except AttributeError:
        pass  # Ignore if process initializes, finalizes, and then initializes again

    if server == 0:
        # convert the IP address of the local host into an int
        # should replace with convert_IP_address_to_int()
        server = "localhost"

    # If socket pool is not alive or is not defined, define it
    if not socket_pool_alive:
        try:
            _socket_pool = _create_new_socket_pool(
                server, directory, socket_count, max_timeout=max_timeout
            )
            # Raise an error if connection to server fails
            _socket_pool.return_socket(_socket_pool.borrow_socket())
        except Exception:
            assert _socket_pool is not None
            _socket_pool.end_pool()
            _socket_pool = None
            raise


def _test_socket_pool(spool, address):
    try:
        sock = spool.borrow_socket()
    except Exception:
        spool.end_pool()
        raise avesterra.AvesTerraError(
            "Failed to initialize connection to {}".format(address)
        )
    else:
        spool.return_socket(sock)


def finalize():
    global _socket_pool
    if _socket_pool:
        _socket_pool.end_pool()
        _socket_pool = None


def _ip2addr(ip):
    return struct.unpack("!L", socket.inet_aton(ip))[0]


def _addr2ip(addr):
    return socket.inet_ntoa(struct.pack("!L", addr))


def borrow_socket(dont_send_bye=False):
    assert _socket_pool is not None, "Did you forget to call `initialize()`?"
    return _socket_pool.borrow_socket(dont_send_bye)


def return_socket(socket: SocketType):
    if _socket_pool:
        _socket_pool.return_socket(socket)


def _confirm(frame: HGTPFrame):
    def parse_error(response: HGTPFrame):
        # Parse the error response and return the error and message (if any)
        try:
            error_code = response.error_code
            # return (error_code, response.bytes.get_bytes())
            return error_code, response._bytes
        except Exception:
            msg = "Invalid error format: {}".format(response)
            raise avesterra.CommunicationError(msg)

    if frame.error_code != 0:
        err_code, error_message_reported = parse_error(frame)
        error = {
            HGTPException.AVESTERRA.value: avesterra.AvesTerraError,
            HGTPException.ENTITY.value: avesterra.EntityError,
            HGTPException.OUTLET.value: avesterra.OutletError,
            HGTPException.TIMEOUT.value: avesterra.TimeoutError,
            HGTPException.NETWORK.value: avesterra.NetworkError,
            HGTPException.AUTHORIZATION.value: avesterra.AuthorizationError,
            HGTPException.ADAPTER.value: avesterra.AdapterError,
            HGTPException.SUBSCRIBER.value: avesterra.SubscriberError,
            HGTPException.APPLICATION.value: avesterra.ApplicationError,
            HGTPException.EXECUTION.value: avesterra.ExecutionError,
            HGTPException.BYPASS.value: avesterra.BypassError,
            HGTPException.FORWARD.value: avesterra.ForwardError,
            HGTPException.VALUE.value: avesterra.ValueError,
            HGTPException.MESSAGE.value: avesterra.MessageError,
            HGTPException.SHUTDOWN.value: avesterra.ShutdownError,
        }[err_code]

        error_message = "Server reported {} error: {}".format(
            HGTPException(err_code).name, error_message_reported.decode("utf-8")
        )

        raise error(error_message)


def send(socket: SocketType, frame: HGTPFrame):
    """In case of Exception, the socket is discarded from the pool"""
    try:
        socket.sendall(frame.build_frame_bytes())
    except Exception:
        print(f"SEND ERROR: {traceback.format_exc()}")
        if _socket_pool:
            _socket_pool.discard_socket(socket)
        raise


def recv(socket: SocketType) -> HGTPFrame:
    """In case of Exception, the socket is either discarded or returned to the
    pool, depending on whether the error was fatal to the connection"""
    try:
        temp = socket.recv(1024)
        if temp is None:
            return HGTPFrame()
        assert (
            len(temp) == 1024
        ), f"Received {len(temp)} bytes HGTP frame, expected 1024. Content:\n{temp.decode()}"

        response: HGTPFrame = HGTPFrame.from_bytes(temp)

        if response.extension > 0:
            response_buffer: bytearray = bytearray(response.extension)
            view = memoryview(response_buffer)
            left_to_read = response.extension
            while left_to_read > 0:
                bytes_read = socket.recv_into(view, left_to_read)
                view = view[bytes_read:]
                left_to_read -= bytes_read

            # Assigned new bytes object to response bytes
            response._bytes = bytes(response_buffer)

            # Nuke byte buffer...since bytes is a completely new object
            del response_buffer
            response_buffer = None

    except Exception:
        if _socket_pool:
            _socket_pool.discard_socket(socket)
        raise

    try:
        _confirm(response)
    except Exception:
        if _socket_pool:
            _socket_pool.return_socket(socket)
        raise

    return response


def post(frame: HGTPFrame):
    socket = borrow_socket()
    send(socket, frame)
    response = recv(socket)
    if _socket_pool:
        _socket_pool.return_socket(socket)
    return response


def host_to_ip(host: str) -> int:
    return (
        int(ip_address(socket.gethostbyname(host)))
        if host != ""
        else int(ip_address(socket.gethostbyname(socket.gethostname())))
    )


##############
# SocketPool #
##############


class SocketPool:
    # A threadsafe pool of socket connections to this host and port

    host: str

    def __init__(self, host, port, directory, quantity, timeout=360):
        # could check whether host_ip is an string for an IP address,
        # and whether port is a valid port

        self.host = host
        self._port = port
        self._dont_send_bye = set()
        self._pool = TimeoutPool(
            lambda: self._create_socket(directory),
            lambda s: self._close_socket(s),
            quantity,
            timeout,
        )

    def borrow_socket(self, dont_send_bye=False):
        # Get a socket from the pool of sockets. Block until available
        sock = self._pool.borrow_resource()
        if dont_send_bye:
            self._dont_send_bye.add(sock)
        return sock

    def return_socket(self, sock):
        """Return socket to the pool"""
        if sock in self._dont_send_bye:
            self._dont_send_bye.remove(sock)
        self._pool.return_resource(sock)

    def discard_socket(self, sock):
        """Discard socket, so it is not used again."""
        if sock in self._dont_send_bye:
            self._dont_send_bye.remove(sock)
        self._pool.discard_resource(sock)

    def end_pool(self):
        # Close all sockets in the pool
        self._pool.spin_down_pool()

    def alive(self):
        # Is the socket pool still alive or has it already ended?
        return self._pool.alive()

    def _create_socket(self, directory):
        address = host_to_ip(self.host)

        ssl._create_default_https_context = ssl._create_unverified_context

        # Create a new socket to host and port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssock = None

        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.options &= ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1
        if address != 0:
            try:
                context.load_verify_locations(
                    os.path.join(directory, str(address) + ".pem")
                )
            except Exception:
                try:
                    context.load_verify_locations(os.path.join(directory, "local.pem"))
                except Exception:
                    cert_dir_path = os.path.join(directory, "avesterra.pem")
                    try:
                        context.load_verify_locations(cert_dir_path)
                    except Exception:
                        print(os.path.join(directory, "avesterra.pem"))
                        print(traceback.format_exc())
                        raise IOError(
                            f"Unable to load a valid TLS certificate from {cert_dir_path}"
                        )
        try:
            s.connect((self.host, self._port))
        except OSError as err:
            s.close()
            raise
        try:
            ssock = context.wrap_socket(s, server_hostname=self.host)
        except ssl.SSLError as err:
            s.close()
            raise

        return ssock

    def _close_socket(self, sock: SocketType):
        """Close this socket"""

        def close_socket():
            if sock not in self._dont_send_bye:
                try:
                    frame = HGTPFrame()
                    frame.command_code = Command.BYE
                    sock.sendall(frame.build_frame_bytes())
                except Exception:
                    pass

            try:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except Exception:
                pass

        # IN a separate thread in case it takes awhile
        threading.Thread(target=close_socket).start()


_socket_pool: SocketPool | None = None


#
#  TimeoutPool --- a generic class for managing a pool of resources
#                  that timeout after no usage for awhile
#
#  This wants to be moved to its own module
#
class TimeoutPool:
    # A pool of resources that will spin down automatically with no usage
    # resources must be hashable
    def __init__(self, spin_up, spin_down, max_quantity, no_usage_duration=60):
        # spin_up --- callable to create a resource, returns resource
        # spin_down --- callable to destory a resource
        # max_quantity --- maximum number of resources that are allowed
        # no_usage_duration --- how long (in seconds) of no use before automatic spin_down
        if max_quantity < 1:
            raise TimeoutPoolError("max_quantity must be at least 1")
        elif no_usage_duration < 1:
            raise TimeoutPoolError("No usage duration must be at least 1 sec")
        else:
            # only need this for debugging data structures
            self._lifeguard = _TimeoutPoolLifeguard(
                spin_up, spin_down, max_quantity, no_usage_duration
            )
            self._lifeguard_requests = self._lifeguard.request_queue()

    def borrow_resource(self):
        # Borrow a resource from the pool, creating or blocking as nec
        assert self.alive(), "Attempting to borrow from spun down pool"
        # Are queues lightweight enough for use once and dispose?
        resource_destination = queue.Queue()
        self._lifeguard_requests.put(("borrow", resource_destination))
        results = resource_destination.get()
        if results == "error":
            result = resource_destination.get()
            raise TimeoutPoolError(result)
        else:
            return results

    def return_resource(self, res):
        # Return the resource to the pool
        assert self.alive(), "Attempting to return to spun down pool"
        self._lifeguard_requests.put(("return", res))

    def discard_resource(self, res):
        # Throw away the resource.
        assert self.alive(), "Attempt to discard resource in spun down pool"
        self._lifeguard_requests.put(("discard", res))

    def spin_down_pool(self):
        # Spin down all resources in the pool
        if self.alive():
            self._lifeguard_requests.put(("stop",))
            del self._lifeguard_requests

    def alive(self):
        # Is the timeout pool still alive?
        return hasattr(self, "_lifeguard_requests")


class _TimeoutPoolLifeguard:
    # Manages a TimeoutPool; exactly one lifeguard for each pool

    def __init__(self, spin_up, spin_down, max_quantity, no_usage_duration=60):
        # spin_up --- callable to create a resource, returns resource
        # spin_down --- callable to destory a resource, given resource
        # quantity --- how many resources to create as max
        # no_usage_duration --- how long (in seconds) of no use before automatic spin_down
        self._spin_up = spin_up
        self._spin_down = spin_down
        self._max_quantity = max_quantity
        self._no_usage_duration = no_usage_duration
        self._free_resources = {}  # dict of resource and time last returned
        self._all_resources = set()
        self._waiting_to_borrow = collections.deque()
        self._requestq = queue.Queue()

        # Multi thread patrolling
        # for i in range(0, 1):
        threading.Thread(
            target=self._perform_requests_forever, args=(), daemon=True
        ).start()

    def request_queue(self):
        return self._requestq

    def _perform_requests_forever(self):
        # perform requests one at a time, checking occasionally for staleness
        while True:
            try:
                request = self._requestq.get(timeout=20)
                self._perform_request(*request)
            except queue.Empty:
                self._spin_down_stale_resources()
            except FinishLifeguarding:
                break
            except Exception:
                print(traceback.format_exc())

    def _perform_request(self, request_action, *args):
        # Do whatever is requested
        if request_action == "borrow":
            (borrower_queue,) = args
            self._provide_resource_to_borrower(borrower_queue)
        elif request_action == "return":
            (resource_returned,) = args
            self._collect_resource_from_borrower(resource_returned)
        elif request_action == "discard":
            (trash,) = args
            self._discard_resource(trash)
        elif request_action == "stop":
            self._discard_all_resources()
            raise FinishLifeguarding
        else:
            raise TimeoutPoolError("Unknown request {}".format(request_action))

    def _provide_resource_to_borrower(self, borrower_queue):
        if self._free_resources:
            resource, ignore = self._free_resources.popitem()
            # 'Resource %s put on queue %s', resource, borrower_queue
            borrower_queue.put(resource)
        elif len(self._all_resources) < self._max_quantity:
            # 'Resource must be created for queue %s', borrower_queue
            self._create_resource(borrower_queue)
        else:
            # 'Waiting for resource to be freed'
            self._waiting_to_borrow.append(borrower_queue)

    def _collect_resource_from_borrower(self, resource_returned):
        # Someone has returned a resource. Put it back in the free list
        # 'Resource %s is returned.', resource_returned
        if self._waiting_to_borrow:
            q = self._waiting_to_borrow.popleft()
            # 'Returned resource %s sent on %s', resource_returned, q
            q.put(resource_returned)
        else:
            tm = time.time()
            # 'Returned resource %s put on freelist at %s',resource_returned,tm)
            self._free_resources[resource_returned] = tm

    def _spin_down_stale_resources(self):
        # f any of the resources are stale, spin them down
        now = time.time()
        # 'Checking for stale resources at %s', now
        # copy is critical because we may remove resources from list
        for resource, last_used in self._free_resources.copy().items():
            if last_used + self._no_usage_duration < now:
                self._spin_down_and_remove(resource)

    def _discard_all_resources(self):
        copy = list(self._all_resources)
        for resource in copy:
            self._discard_resource(resource)

    def _spin_down_and_remove(self, resource):
        # Spin down a single resource and remove it from the freelist
        self._free_resources.pop(resource)
        self._discard_resource(resource)

    def _create_resource(self, q):
        # Create a new resource, put on q, and record how many are out.
        try:
            res = self._spin_up()
            self._all_resources.add(res)
            q.put(res)
        except Exception as err:
            q.put("error")
            q.put("{}: {}".format(type(err).__name__, str(err)))

    def _discard_resource(self, resource_to_discard):
        if not resource_to_discard in self._all_resources:
            return
        self._all_resources.remove(resource_to_discard)
        self._spin_down(resource_to_discard)


class FinishLifeguarding(Exception):
    # When the socket pool is finishing up
    pass


class TimeoutPoolError(Exception):
    # Error with the timeout pool
    def __init__(self, message):
        self.message = message


def _create_new_socket_pool(host, directory, socket_count, max_timeout) -> SocketPool:
    return SocketPool(host, PORT, directory, socket_count, timeout=max_timeout)
