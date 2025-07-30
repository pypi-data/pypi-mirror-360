""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import os
from typing import Callable, TypeVar
from avesterra import av_log


AVESTERRA_AUTH = "AVESTERRA_AUTH"
AVESTERRA_HOST = "AVESTERRA_HOST"
AVESTERRA_CERTIFICATE_DIR_PATH = "AVESTERRA_CERTIFICATE_DIR_PATH"
MOUNT_OUTLET = "MOUNT_OUTLET"


T = TypeVar("T")


def get_or_default(
    var: str, default: T, fn: Callable[[str], T] = lambda x: x, log_warn=True
) -> T:
    """
    If you intend to read from a dotenv, make sure to load the dotenv before
    calling this function.

    Gets a variable from the environment, or a default value.
    By default, logs a warning message saying that default value is used if
    missing.
    Optionnaly takes a function to construct an object from the found string,
    which can be used to provide default value of object that would be
    constructed from a string.

    ```
    host = env.get_or_default(env.AVESTERRA_HOST, '127.0.0.1')
    outlet = env.get_or_default("OUTLET", AvEntity(0, 0, 4200), AvEntity.from_str)
    outlet = env.get_or_default("OUTLET", AvEntity(0, 0, 4200), AvEntity.from_str, log_warn = False)
    ```
    """
    try:
        return fn(get_or_raise(var))
    except Exception:
        if log_warn:
            av_log.warn(
                f"{var} environment variable not present; using default value of '{str(default)}'"
            )
        return default


T = TypeVar("T")


def get_or_raise(name: str, fn: Callable[[str], T] = lambda x: x) -> T:
    """
    Similar to `get_or_default`, but raises an exception if the variable is
    not set
    """
    value = os.getenv(name)
    if value is None:
        raise Exception(f"{name} environment variable not present")
    return fn(value)
