import os
import logging
from pathlib import Path
from dataclasses import field, dataclass
from functools import cached_property
from typing import TypedDict, Literal, Optional

import istari_digital_core

from istari_digital_client.env import env_bool, env_int, env_str, env_cache_root

logger = logging.getLogger("istari-digital-client.configuration")


BearerAuthSetting = TypedDict(
    "BearerAuthSetting",
    {
        "type": Literal["bearer"],
        "in": Literal["header"],
        "key": Literal["Authorization"],
        "value": str,
    },
)

AuthSettings = TypedDict(
    "AuthSettings",
    {
        "RequestAuthenticator": BearerAuthSetting,
    },
    total=False,
)


@dataclass
class Configuration:
    registry_url: Optional[str] = field(
        default_factory=env_str("ISTARI_REGISTRY_URL", default=None)
    )
    registry_auth_token: Optional[str] = field(
        default_factory=env_str("ISTARI_REGISTRY_AUTH_TOKEN")
    )
    http_request_timeout_secs: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_HTTP_REQUEST_TIMEOUT_SECS"),
    )
    retry_enabled: Optional[bool] = field(
        default_factory=env_bool("ISTARI_CLIENT_RETRY_ENABLED", default=True)
    )
    retry_max_attempts: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_RETRY_MAX_ATTEMPTS")
    )
    retry_min_interval_millis: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_RETRY_MIN_INTERVAL_MILLIS")
    )
    retry_max_interval_millis: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_RETRY_MAX_INTERVAL_MILLIS")
    )
    filesystem_cache_enabled: Optional[bool] = field(
        default_factory=env_bool("ISTARI_CLIENT_FILESYSTEM_CACHE_ENABLED", default=True)
    )
    filesystem_cache_root: Path = field(
        default_factory=env_cache_root("ISTARI_CLIENT_FILESYSTEM_CACHE_ROOT")
    )
    filesystem_cache_clean_on_exit: Optional[bool] = field(
        default_factory=env_bool(
            "ISTARI_CLIENT_FILESYSTEM_CACHE_CLEAN_BEFORE_EXIT", default=True
        )
    )
    retry_jitter_enabled: Optional[bool] = field(
        default_factory=env_bool("ISTARI_CLIENT_RETRY_JITTER_ENABLED", default=True)
    )
    multipart_chunksize: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_MULTIPART_CHUNKSIZE")
    )
    multipart_threshold: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_MULTIPART_THRESHOLD")
    )
    datetime_format: str = field(init=False, default="%Y-%m-%dT%H:%M:%S.%f%z")
    date_format: str = field(init=False, default="%Y-%m-%d")

    def __post_init__(self) -> None:
        os.environ["ISTARI_REGISTRY_URL"] = self.registry_url or ""
        logger.debug(
            "set os.environ['ISTARI_REGISTRY_URL'] to '%s'",
            os.environ.get("ISTARI_REGISTRY_URL"),
        )
        os.environ["ISTARI_REGISTRY_AUTH_TOKEN"] = self.registry_auth_token or ""
        logger.debug(
            "setting os.environ['ISTARI_REGISTRY_AUTH_TOKEN'] to '%s'",
            os.environ.get("ISTARI_REGISTRY_AUTH_TOKEN"),
        )

    def auth_settings(self) -> AuthSettings:
        """Gets Auth Settings dict for api client.

        :return: The Auth Settings information dict.
        """
        auth: AuthSettings = {}
        if self.registry_auth_token is not None:
            auth["RequestAuthenticator"] = {
                "type": "bearer",
                "in": "header",
                "key": "Authorization",
                "value": "Bearer " + self.registry_auth_token,
            }
        return auth

    @classmethod
    def from_native_configuration(
        cls: type["Configuration"], native: istari_digital_core.Configuration
    ) -> "Configuration":
        return Configuration(
            registry_url=native.registry_url,
            registry_auth_token=native.registry_auth_token,
            retry_enabled=native.retry_enabled,  # type: ignore[attr-defined]
            retry_max_attempts=native.retry_max_attempts,  # type: ignore[attr-defined]
            retry_min_interval_millis=native.retry_min_interval_millis,  # type: ignore[attr-defined]
            retry_max_interval_millis=native.retry_max_interval_millis,  # type: ignore[attr-defined]
            retry_jitter_enabled=native.retry_jitter_enabled,
            multipart_chunksize=native.multipart_chunksize,
            multipart_threshold=native.multipart_threshold,
        )

    @cached_property
    def native_configuration(self) -> istari_digital_core.Configuration:
        return istari_digital_core.Configuration(
            registry_url=self.registry_url,
            registry_auth_token=self.registry_auth_token,
            retry_enabled=self.retry_enabled,  # type: ignore[attr-defined]
            retry_max_attempts=self.retry_max_attempts,  # type: ignore[attr-defined]
            retry_min_interval_millis=self.retry_min_interval_millis,  # type: ignore[attr-defined]
            retry_max_interval_millis=self.retry_max_interval_millis,  # type: ignore[attr-defined]
            retry_jitter_enabled=self.retry_jitter_enabled,
            multipart_chunksize=self.multipart_chunksize,
            multipart_threshold=self.multipart_threshold,
        )


class ConfigurationError(ValueError):
    pass
