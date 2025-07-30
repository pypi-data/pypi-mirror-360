""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""
import hashlib
import os
from os import getcwd
import stat
from avesterra.avial import *
from avesterra.predefined import file_outlet
import avesterra.attributes as attributes

# Avial 4.10 Added this module

AvFile = AvEntity


def create_file(
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    mode: AvMode = AvMode.NULL,
    outlet: AvEntity = NULL_ENTITY,
    server: AvEntity = NULL_ENTITY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvFile:
    adapter = file_outlet if outlet == NULL_ENTITY else outlet
    value = invoke_entity(
        adapter,
        AvMethod.CREATE,
        name=name,
        key=key,
        context=AvContext.AVESTERRA,
        category=AvCategory.AVESTERRA,
        klass=AvClass.FILE,
        mode=mode,
        ancillary=server,
        authorization=authorization,
    )
    return value.decode_entity()


def delete_file(file: AvFile, authorization: AvAuthorization = NULL_AUTHORIZATION):
    invoke_entity(file, AvMethod.DELETE, authorization=authorization)


def download_file(
    file: AvFile,
    name: str,
    timeout: AvTimeout,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    try:
        data = read_data(entity=file, timeout=timeout, authorization=authorization)
    except Exception as e:
        raise AvialError(f"Failed to download file {file}({name}): {str(e)}") from e

    try:
        with open(f"{name}", "wb") as f:
            f.write(data)
    except Exception as e:
        raise IOError(
            f"Failed to write file {file}({name}) to directory {getcwd()}/{name}"
        )

    try:
        mode = attributes.get_attribute(
            entity=file, attribute=AvAttribute.MODE, authorization=authorization
        ).decode()
        mode = int(mode)
    except Exception as e:
        mode = 0o664
    os.chmod(f"{name}", mode)


def upload_file(
    file: AvFile,
    path: str,
    version: str,
    timeout: AvTimeout,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
):
    mode = stat.S_IMODE(os.lstat(path).st_mode)

    file_mod_time = datetime.fromtimestamp(os.path.getmtime(path), tz=UTC)

    with open(path, "rb") as f:
        data = f.read()

    try:
        attributes.set_attribute(
            entity=file,
            attribute=AvAttribute.MODE,
            value=AvValue.encode_integer(mode),
            authorization=authorization,
        )
        attributes.set_attribute(
            entity=file,
            attribute=AvAttribute.TIME,
            value=AvValue.encode_time(file_mod_time),
            authorization=authorization,
        )

        # Avial 4.10 Calculate hash and set it in the KS
        attributes.set_attribute(
            entity=file,
            attribute=AvAttribute.HASH,
            value=AvValue.encode_string(hash_file_content(data)),
            authorization=authorization,
        )
        # Avial 4.11 Version attribute can now be set on file uploads
        attributes.set_attribute(
            entity=file,
            attribute=AvAttribute.VERSION,
            value=AvValue.encode_string(version),
            authorization=authorization,
        )

        write_data(entity=file, data=data, timeout=timeout, authorization=authorization)
    except Exception as e:
        raise AvialError(f"Failed to upload {path} to entity {file}: {str(e)}")


def file_size(file: AvFile, authorization: AvAuthorization = NULL_AUTHORIZATION):
    return AvValue.decode_integer(
        invoke_entity(file, AvMethod.COUNT, authorization=authorization)
    )


def file_time(
    file: AvFile, authorization: AvAuthorization = NULL_AUTHORIZATION
) -> AvTime:
    return attributes.get_attribute(
        entity=file, attribute=AvAttribute.TIME, authorization=authorization
    ).decode_time()


def file_mode(file: AvFile, authorization: AvAuthorization = NULL_AUTHORIZATION):
    return attributes.get_attribute(
        entity=file, attribute=AvAttribute.MODE, authorization=authorization
    ).decode_integer()


def file_hash(file: AvFile, authorization: AvAuthorization = NULL_AUTHORIZATION):
    return attributes.get_attribute(
        entity=file, attribute=AvAttribute.HASH, authorization=authorization
    ).decode_string()


def hash_file_content(byte_content: bytes) -> str:
    return hashlib.sha512(byte_content).hexdigest()
