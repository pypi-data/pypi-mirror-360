"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from typing import Callable
from avesterra.taxonomy import AvNotice
from orchestra._log_publisher import publish_log


def null(msg: str):
    _log(AvNotice.NULL, msg)


def avesterra(msg: str):
    _log(AvNotice.AVESTERRA, msg)


def success(msg: str):
    _log(AvNotice.SUCCESS, msg)


def info(msg: str):
    _log(AvNotice.INFORM, msg)


def warn(msg: str):
    _log(AvNotice.WARNING, msg)


def error(msg: str):
    _log(AvNotice.ERROR, msg)


def fatal(msg: str):
    _log(AvNotice.FATAL, msg)


def debug(msg: str):
    _log(AvNotice.DEBUG, msg)


def test(msg: str):
    _log(AvNotice.TEST, msg)


def set_custom_formatter(f: Callable[[AvNotice, str], str]):
    global _global_custom_formatter
    _global_custom_formatter = f


def _default_formatter(notice: AvNotice, msg: str) -> str:
    return notice_to_string(notice) + "| " + msg


_global_custom_formatter = _default_formatter


def notice_to_string(notice: AvNotice) -> str:
    if notice == AvNotice.NULL:
        return " "
    else:
        return notice.name[0]


def _log(notice: AvNotice, msg: str):
    lines = msg.split("\n")
    lines = [_global_custom_formatter(notice, line) for line in lines]

    if notice in (
        AvNotice.SUCCESS,
        AvNotice.INFORM,
        AvNotice.WARNING,
        AvNotice.ERROR,
        AvNotice.FATAL,
    ):
        for ln in lines:
            publish_log(ln)

    output = "\n".join(lines)
    print(output)
