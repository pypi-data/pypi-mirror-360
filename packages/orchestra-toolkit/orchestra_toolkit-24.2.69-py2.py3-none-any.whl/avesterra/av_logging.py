""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import traceback
from threading import Lock
from typing import List
from avesterra.taxonomy import AvNotice
from datetime import datetime

log_aggregate_lock = Lock()
log_aggregate = []


def notice_to_string(notice: AvNotice) -> str:
    # If notice is NULL, then return
    # a NULL filter
    if notice == AvNotice.NULL:
        return ""
    else:
        # Use first letter of name as
        # the notice code
        return notice.name[0]


def log(notice: AvNotice, message: str) -> str:
    # Build log record
    log_record: str = f"{notice_to_string(notice)}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}"

    # Lock
    log_aggregate_lock.acquire()

    try:
        # Add log to memory aggregate
        log_aggregate.append(log_record)
    except Exception:
        print(f"Log aggregate append error {traceback.format_exc()}")
    finally:
        # Unlock
        log_aggregate_lock.release()

    # Log to stdout
    print(log_record)

    return log_record


def get(notice: AvNotice = AvNotice.NULL, n: int = 0) -> str:
    output: str = ""

    # Lock
    log_aggregate_lock.acquire()

    try:
        # Filter lines based on provided notice
        log_slice: List[str] = [
            line for line in log_aggregate if notice_to_string(notice) in line
        ]

        # Protection against an n that is larger than the
        # actual log aggregate
        if n.__abs__() > len(log_slice):
            start_index = 0
        else:
            start_index = n

        # Get log as one string
        output = "\n".join(log_slice[start_index:])

    except Exception:
        print(f"Log retrieval error {traceback.format_exc()}")

    finally:
        # Unlock
        log_aggregate_lock.release()

    # Return log as one string
    return output


def wipe():
    # Lock
    log_aggregate_lock.acquire()

    try:
        # Wipe out log aggregate
        log_aggregate.clear()

    except Exception:
        print(f"Log wipe error {traceback.format_exc()}")

    finally:
        # Unlock
        log_aggregate_lock.release()
