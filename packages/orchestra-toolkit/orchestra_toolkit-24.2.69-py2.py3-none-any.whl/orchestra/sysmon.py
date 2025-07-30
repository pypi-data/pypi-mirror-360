"""
Main methods of the standard sysmon adapter.
"""

from datetime import datetime
from orchestra import mount
from avesterra import av

MOUNT_KEY = "sysmon"


def refresh_status(
    component: av.AvEntity,
    status: str,
    justification: str | None,
    perfStatus: str,
    authorization: av.AvAuthorization,
):
    data = {
        "component": av.AvValue.encode_entity(component),
        "pubtime": av.AvValue.encode_time(datetime.now()),
        "status": av.AvValue.encode_string(status),
        "perfStatus": av.AvValue.encode_string(perfStatus),
    }
    if justification:
        data["justification"] = av.AvValue.encode_string(justification)
    av.invoke_entity_retry_bo(
        entity=mount.get_outlet(MOUNT_KEY, authorization),
        method=av.AvMethod.REFRESH,
        attribute=av.AvAttribute.STATUS,
        value=av.AvValue.encode_aggregate(data),
        precedence=1,
        authorization=authorization,
    )


def retrieve_component(key: str, authorization: av.AvAuthorization) -> av.AvValue:
    return av.invoke_entity_retry_bo(
        entity=mount.get_outlet(MOUNT_KEY, authorization),
        method=av.AvMethod.RETRIEVE,
        attribute=av.AvAttribute.COMPONENT,
        key=key,
        precedence=1,
        authorization=authorization,
    )
