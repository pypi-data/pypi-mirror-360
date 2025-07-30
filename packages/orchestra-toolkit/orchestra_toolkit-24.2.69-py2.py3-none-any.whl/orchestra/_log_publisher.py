import secrets
from dataclasses import dataclass
from datetime import datetime
import time
import traceback
from queue import SimpleQueue

import avesterra as av

_g_log_queue: SimpleQueue[str] = SimpleQueue()


@dataclass
class Config:
    max_log_length: int
    enabled: bool

    DEFAULT_MAX_LOG_LENGTH = 100
    DEFAULT_ENABLED = True
    _cache: tuple["Config", float] | None = None

    @classmethod
    def read_or_default(
        cls, outlet: av.AvEntity, authorization: av.AvAuthorization
    ) -> "Config":
        CACHE_DURATION_SECONDS = 5
        if cls._cache is not None:
            val, timestamp = cls._cache
            if time.time() - timestamp < CACHE_DURATION_SECONDS:
                return val

        max_log_length = cls.DEFAULT_MAX_LOG_LENGTH
        enabled = cls.DEFAULT_ENABLED
        try:
            val = av.get_attribute(
                outlet, authorization, av.AvAttribute.LOG
            ).decode_aggregate()
            if "max_log_length" in val:
                max_log_length = val["max_log_length"].decode_integer()
            if "enabled" in val:
                enabled = val["enabled"].decode_boolean()
        except Exception:
            pass
        config = cls(max_log_length=max_log_length, enabled=enabled)
        cls._cache = (config, time.time())
        return config

    def write(self, outlet: av.AvEntity, authorization: av.AvAuthorization):
        av.set_attribute(
            outlet,
            authorization,
            av.AvAttribute.LOG,
            av.AvValue.encode_aggregate(
                {
                    "max_log_length": av.AvValue.encode_integer(self.max_log_length),
                    "enabled": av.AvValue.encode_boolean(self.enabled),
                }
            ),
        )


def publish_log(line: str):
    _g_log_queue.put(line)


def clear_log(outlet: av.AvEntity, authorization: av.AvAuthorization):
    try:
        av.purge_traits(outlet, authorization, av.AvAttribute.LOG)
    except Exception as e:
        if "attribute not found" not in str(e):
            raise


def log_publisher_thread(outlet: av.AvEntity, authorization: av.AvAuthorization):
    """Should be started after av.initialize"""
    global _g_log_queue

    config = Config.read_or_default(outlet, authorization)
    config.write(outlet, authorization)  # ensures the config is set

    while True:
        try:
            line = _g_log_queue.get()
            if Config.read_or_default(outlet, authorization).enabled:
                _save_log(outlet, authorization, line)
        except AssertionError:  # finalize was called
            return
        except Exception as e:
            av.av_log.error(f"Log publisher error: {e}")
            av.av_log.debug(traceback.format_exc())


def _save_log(outlet: av.AvEntity, authorization: av.AvAuthorization, line: str):
    max_log_length = Config.read_or_default(outlet, authorization).max_log_length
    name = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    av.insert_trait(
        outlet,
        authorization,
        av.AvAttribute.LOG,
        name,
        key=secrets.token_hex(6),  # Random key because unkeyed traits are a pain
        value=av.AvValue.encode_text(line),
    )
    while av.trait_count(outlet, authorization, av.AvAttribute.LOG) > max_log_length:
        av.remove_trait(outlet, authorization, av.AvAttribute.LOG, index=1)
