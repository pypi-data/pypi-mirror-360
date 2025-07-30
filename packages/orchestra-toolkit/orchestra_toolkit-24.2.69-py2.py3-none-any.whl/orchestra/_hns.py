"""
Health and Status logic
"""

from collections import defaultdict, deque
from dataclasses import dataclass
import traceback
import time
import statistics
from typing import Callable, Literal
import avesterra as av
from orchestra import mount
from . import sysmon


class Health:
    status: Literal["GREEN", "YELLOW", "RED"]
    justification: str | None
    """If status is not GREEN, this field should contain a justification for the status"""

    @classmethod
    def _init(
        cls, status: Literal["GREEN", "YELLOW", "RED"], justification: str | None = None
    ):
        res = cls()
        res.status = status
        res.justification = justification
        return res

    @classmethod
    def green(cls):
        return cls._init("GREEN", None)

    @classmethod
    def yellow(cls, justification: str):
        return cls._init("YELLOW", justification)

    @classmethod
    def red(cls, justification: str):
        return cls._init("RED", justification)


@dataclass
class CallStat:
    restime: float
    """Response time of the call in seconds"""
    timestamp: float
    """Timestamp at which the call was made"""
    exception: Exception | None
    """The exception raised during the call, if any. If None, the call was successful."""


g_routes: dict[str, deque[CallStat]] = defaultdict(lambda: deque[CallStat](maxlen=100))


class MonitorStats:
    def __init__(self, name: str):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del traceback
        end_time = time.time()
        assert self.start_time is not None

        g_routes[self.name].append(
            CallStat(
                restime=end_time - self.start_time,
                timestamp=self.start_time,
                exception=exc_value if exc_type else None,
            )
        )


def health_n_status_thread(
    component: av.AvEntity,
    authorization: av.AvAuthorization,
    statusfn: Callable[[], Health],
):
    """
    Regularly publishes health and status, using the measurements done by the
    `measure` decorator function
    """
    _check_sysmon_version(authorization)
    while True:
        try:
            health = statusfn()
            # backward compatibility with old health status functions
            # Written on 2025-06-23, can probably be removed in 2026
            if isinstance(health, str):
                health = Health._init(health, None)  # pyright: ignore
            elif not isinstance(health, Health):
                av.av_log.error(
                    f"Health status function returned an invalid type: {type(health)}"
                )
                health = Health.red(
                    f"Health status function did not return a valid HealthReport object: {health}",
                )
        except Exception as e:
            av.av_log.error(
                f"Exception raised in the health status function: {e}, default to RED"
            )
            health = Health.red(f"Exception raised: {repr(e)}")
        try:
            _refresh_hns(component, authorization, health)
            time.sleep(10)
        except Exception:
            av.av_log.error(
                f"/!\\ bug in orchestra-toolkit library: Uncaught exception while reporting health status: {traceback.format_exc()}"
            )


def _refresh_hns(
    component: av.AvEntity,
    authorization: av.AvAuthorization,
    healthreport: Health,
):
    try:
        sysmon.refresh_status(
            component=component,
            status=healthreport.status,
            justification=healthreport.justification,
            perfStatus="GREEN",
            authorization=authorization,
        )
    except Exception as e:
        av.av_log.warn(f"Invoke to sysmon failed: {e}")

    model = av.AvialModel()
    for name, metrics in g_routes.items():
        if not metrics:
            continue

        metrics = metrics.copy()  # in case the deque is modified during the loop
        restime_ordered = sorted(s.restime for s in metrics)
        avg_response_time = sum(restime_ordered) / len(restime_ordered)
        timespan = time.time() - metrics[0].timestamp

        d = {
            "sample size": av.AvValue.encode_integer(len(metrics)),
            "avg response time": av.AvValue.encode_float(round(avg_response_time, 4)),
            "avg call per minute": av.AvValue.encode_float(
                round(len(metrics) / (timespan / 60.0), 1)
            ),
            "success rate %": av.AvValue.encode_float(
                round(sum(100 for s in metrics if s.exception) / len(metrics), 1)
            ),
        }
        if len(metrics) > 1:

            d |= {
                "response time stddev": av.AvValue.encode_float(
                    round(statistics.stdev(restime_ordered), 4)
                ),
                "response time p01": av.AvValue.encode_float(
                    round(restime_ordered[int(len(metrics) * 0.01)], 4)
                ),
                "response time p10": av.AvValue.encode_float(
                    round(restime_ordered[int(len(metrics) * 0.1)], 4)
                ),
                "response time p50": av.AvValue.encode_float(
                    round(restime_ordered[len(metrics) // 2], 4)
                ),
                "response time p90": av.AvValue.encode_float(
                    round(restime_ordered[int(len(metrics) * 0.9)], 4)
                ),
                "response time p99": av.AvValue.encode_float(
                    round(restime_ordered[int(len(metrics) * 0.99)], 4)
                ),
            }
        model.attributes[av.AvAttribute.PERFORMANCE].traits[name].value = (
            av.AvValue.encode_aggregate(d)
        )

    try:
        av.store_entity(
            component,
            value=model.to_interchange(),
            authorization=authorization,
        )
        av.publish_event(
            component,
            event=av.AvEvent.UPDATE,
            attribute=av.AvAttribute.HEALTH,
            authorization=authorization,
        )
    except Exception as e:
        av.av_log.warn(f"Failed to store health and status in outlet: {e}")


def _check_sysmon_version(authorization: av.AvAuthorization):
    outlet = mount.get_outlet(sysmon.MOUNT_KEY, authorization)
    version = av.get_fact(outlet, av.AvAttribute.VERSION, authorization=authorization)
    versionstr = version.decode_string()
    # Not doing full semver parsing to not depend on third party
    major, minor, _ = map(int, versionstr.split("."))
    if major == 0 and minor < 3:
        raise RuntimeError(
            f"Sysmon outlet version {versionstr} is too old, please update the sysmon adapter to at least 0.3.0"
        )
