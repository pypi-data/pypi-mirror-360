""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from abc import abstractmethod
from functools import cache
import avesterra as av
from orchestra import env
from orchestra.adapter_interface import Interface


class FromEnv:
    """Placeholder value to signify we'll get that value from environment"""


def mount_outlet(
    key: str,
    auth: av.AvAuthorization,
    authority: av.AvAuthorization,
    interface: Interface,
    mount_adapter: av.AvEntity | FromEnv = FromEnv(),
) -> av.AvEntity:
    if isinstance(mount_adapter, FromEnv):
        mount_adapter = _get_mount_outlet_from_env()

    return _current_mount_impl(mount_adapter, auth).mount_outlet(
        mount_adapter, key, auth, authority, interface
    )


def get_outlet(
    key: str, auth: av.AvAuthorization, mount_adapter: av.AvEntity | FromEnv = FromEnv()
):
    if isinstance(mount_adapter, FromEnv):
        mount_adapter = _get_mount_outlet_from_env()

    return _current_mount_impl(mount_adapter, auth).get_outlet(mount_adapter, key, auth)


# ----- Anything below that point doesn't make sense and shouldn't exist ----
"""
We currently have different implementation of the mount adapter.
This class acts as an abstraction that exposes the common functionnality,
and allow us to use them regardless of which implementation is currently
running.
Use the `detect_current_implementation` method to get an instance of the current implementation.

We should have a single mount adapter ASAP to avoid having to do this.
"""


class _Mount:

    @staticmethod
    def detect_current_implementation(
        mount_adapter: av.AvEntity, auth: av.AvAuthorization
    ) -> "_Mount":
        """
        Detect the current implementation of the mount adapter and returns an
        instance of the corresponding class.
        """
        try:
            av.invoke_entity_retry_bo(
                entity=mount_adapter,
                method=av.AvMethod.TEST,
                attribute=av.AvAttribute.REGISTRY,
                key="_",
                precedence=1,
                authorization=auth,
            )
            return LKMountAdapter()
        except Exception as e:
            if "not authorized" in str(e):
                raise
            return MaestroMountAdapter()

    @abstractmethod
    def mount_outlet(
        self,
        mount_adapter: av.AvEntity,
        key: str,
        auth: av.AvAuthorization,
        authority: av.AvAuthorization,
        interface: Interface,
    ) -> av.AvEntity:
        pass

    @abstractmethod
    def get_outlet(
        self,
        mount_adapter: av.AvEntity,
        key: str,
        auth: av.AvAuthorization,
    ) -> av.AvEntity:
        pass


class LKMountAdapter(_Mount):
    def mount_outlet(
        self,
        mount_adapter: av.AvEntity,
        key: str,
        auth: av.AvAuthorization,
        authority: av.AvAuthorization,
        interface: Interface,
    ) -> av.AvEntity:
        del interface
        res = av.invoke_entity_retry_bo(
            entity=mount_adapter,
            method=av.AvMethod.CREATE,
            attribute=av.AvAttribute.OUTLET,
            auxiliary=av.NULL_ENTITY,
            key=key,
            name=key,
            precedence=1,
            value=av.AvValue.encode(authority),
            authorization=auth,
        )
        outlet = res.decode_entity()

        is_object = False
        try:
            count = av.entity_connections(outlet, auth)
            for i in range(count):
                o, _, _, _ = av.entity_connection(outlet, i + 1, auth)
                if o == av.object_outlet:
                    is_object = True
        except Exception as e:
            raise RuntimeError(
                "Failed to check if outlet is connected to Object adapter (we're using LKMountAdapter)"
            ) from e

        if not is_object:
            try:
                av.connect_method(outlet, av.object_outlet, authorization=auth)
                av.invoke_entity(outlet, method=av.AvMethod.CREATE, authorization=auth)
            except Exception as e:
                raise RuntimeError(
                    "Failed to connect outlet to Object adapter on precedence 0 (we're using LKMountAdapter)"
                ) from e
        return outlet

    def get_outlet(
        self,
        mount_adapter: av.AvEntity,
        key: str,
        auth: av.AvAuthorization,
    ) -> av.AvEntity:
        res = av.invoke_entity_retry_bo(
            entity=mount_adapter,
            method=av.AvMethod.GET,
            attribute=av.AvAttribute.OUTLET,
            key=key,
            precedence=1,
            authorization=auth,
        )
        return res.decode_entity()


class MaestroMountAdapter(_Mount):
    def mount_outlet(
        self,
        mount_adapter: av.AvEntity,
        key: str,
        auth: av.AvAuthorization,
        authority: av.AvAuthorization,
        interface: Interface,
    ) -> av.AvEntity:
        del authority
        res = av.invoke_entity_retry_bo(
            entity=mount_adapter,
            method=av.AvMethod.EXECUTE,
            name="MOUNT",
            key=key,
            value=interface.to_avialmodel().to_interchange(),
            precedence=0,
            authorization=auth,
        )
        return res.decode_entity()

    def get_outlet(
        self,
        mount_adapter: av.AvEntity,
        key: str,
        auth: av.AvAuthorization,
    ) -> av.AvEntity:
        res = av.invoke_entity_retry_bo(
            entity=mount_adapter,
            method=av.AvMethod.EXECUTE,
            name="GET",
            key=key,
            precedence=0,
            authorization=auth,
        )
        return res.decode_entity()


@cache
def _get_mount_outlet_from_env() -> av.AvEntity:
    return env.get_or_raise(env.MOUNT_OUTLET, av.AvEntity.from_str)


@cache
def _current_mount_impl(mount_adapter: av.AvEntity, auth: av.AvAuthorization) -> _Mount:
    return _Mount.detect_current_implementation(mount_adapter, auth)
