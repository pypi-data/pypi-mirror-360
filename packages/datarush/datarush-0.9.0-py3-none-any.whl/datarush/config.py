"""Application config."""

import logging
from contextvars import ContextVar
from enum import StrEnum
from functools import cached_property
from typing import Any, Callable

from dotenv import load_dotenv
from envarify import AnyHttpUrl, BaseConfig, EnvVar, SecretString

from datarush.core.dataflow import Operation

load_dotenv(override=False)

LOG = logging.getLogger(__name__)


################################
########## S3 CONFIG ###########
################################


class S3Config(BaseConfig):
    """S3 Configuration."""

    endpoint: AnyHttpUrl = EnvVar("S3_ENDPOINT")
    access_key: str = EnvVar("S3_ACCESS_KEY")
    secret_key: SecretString = EnvVar("S3_SECRET_KEY")
    session_token: SecretString | None = EnvVar("S3_SESSION_TOKEN", default=None)
    region_name: str | None = EnvVar("S3_REGION_NAME", default=None)
    account_id: str | None = EnvVar("S3_ACCOUNT_ID", default=None)
    profile_name: str | None = EnvVar("S3_PROFILE_NAME", default=None)
    default_bucket: str | None = EnvVar("S3_DEFAULT_BUCKET", default=None)

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize S3Config with environment variables.

        Args:
            endpoint: S3 endpoint URL.
            access_key: S3 access key.
            secret_key: S3 secret key (as SecretString).
            session_token: Optional session token for temporary credentials.
            region_name: Optional AWS region name.
            account_id: Optional AWS account ID.
            profile_name: Optional AWS profile name.
            default_bucket: Optional default bucket name.
        """
        super().__init__(**kwargs)


################################
#### TEMPLATE STORE CONFIG #####
################################


class TemplateStoreType(StrEnum):
    """Template Store Type."""

    S3 = "S3"
    FILESYSTEM = "FILESYSTEM"


################################
####### LOGGING CONFIG ########
################################


class LoggingConfig(BaseConfig):
    """Logging Configuration."""

    level: str = EnvVar("DATARUSH_LOG_LEVEL", default="INFO")
    log_file: str | None = EnvVar("DATARUSH_LOG_FILE", default=None)
    format_string: str | None = EnvVar("DATARUSH_LOG_FORMAT", default=None)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize LoggingConfig with environment variables."""
        super().__init__(**kwargs)
        LOG.debug(f"LoggingConfig initialized with level: {self.level}")


class S3TemplateStoreConfig(BaseConfig):
    """S3 based template manager config."""

    bucket: str = EnvVar("TEMPLATE_STORE_S3_BUCKET")
    prefix: str = EnvVar("TEMPLATE_STORE_S3_PREFIX", default="datarush")


class FilesystemTemplateStoreConfig(BaseConfig):
    """File system based template manager config."""

    path: str = EnvVar("TEMPLATE_STORE_FILESYSTEM_PATH", default=".")


class TemplateStoreConfig(BaseConfig):
    """Template Manager Configuration."""

    store_type: TemplateStoreType = EnvVar("TEMPLATE_STORE_TYPE")

    @property
    def s3(self) -> S3TemplateStoreConfig:
        """S3 template store config."""
        if self.store_type != TemplateStoreType.S3:
            raise ValueError("Template store type is not S3")
        return S3TemplateStoreConfig.fromenv()

    @property
    def filesystem(self) -> FilesystemTemplateStoreConfig:
        """File system template store config."""
        if self.store_type != TemplateStoreType.FILESYSTEM:
            raise ValueError("Template store type is not FILESYSTEM")
        return FilesystemTemplateStoreConfig.fromenv()


################################
###### APPLICATION CONFIG ######
################################


class DatarushConfig:
    """Datarush application configuration."""

    def __init__(
        self,
        custom_operations: list[type[Operation]] | None = None,
        s3_config_factory: Callable[[], S3Config] | None = None,
    ) -> None:
        """
        Initialize the Datarush configuration.

        Args:
            custom_operations: List of custom operations to be registered.
            s3_config_factory: Optional factory function to create S3Config.
        """
        LOG.debug("Initializing DatarushConfig")
        self._custom_operations = custom_operations or []
        self._s3_config_factory = s3_config_factory
        LOG.debug(
            f"DatarushConfig initialized with {len(self._custom_operations)} custom operations"
        )

    @property
    def custom_operations(self) -> list[type[Operation]]:
        """Custom operations."""
        return self._custom_operations

    @cached_property
    def s3(self) -> S3Config:
        """Get S3 configuration."""
        if self._s3_config_factory is not None:
            return self._s3_config_factory()
        return S3Config.fromenv()

    @cached_property
    def template_store(self) -> TemplateStoreConfig:
        """Get template store configuration."""
        return TemplateStoreConfig.fromenv()

    @cached_property
    def logging(self) -> LoggingConfig:
        """Get logging configuration."""
        return LoggingConfig.fromenv()


_config_var = ContextVar[DatarushConfig]("config")


def set_datarush_config(config: DatarushConfig) -> None:
    """Set the Datarush configuration to contextvar."""
    _config_var.set(config)


def get_datarush_config() -> DatarushConfig:
    """Get the current Datarush configuration."""
    try:
        return _config_var.get()
    except LookupError as e:
        raise LookupError("set_datarush_config must be called before get_datarush_config") from e
