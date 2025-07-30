"""Dataflow template management."""

import abc
import json
import os
from functools import cache
from io import BytesIO
from typing import Any, TypedDict, cast

from datarush.config import (
    FilesystemTemplateStoreConfig,
    S3TemplateStoreConfig,
    TemplateStoreType,
    get_datarush_config,
)
from datarush.core.dataflow import Dataflow, Operation
from datarush.core.operations import get_operation_type_by_name
from datarush.core.types import ParameterSpec
from datarush.exceptions import TemplateAlreadyExistsError
from datarush.utils.s3_client import S3Client
from datarush.version import __version__

_TEMPLATES_FOLDER = "templates"
_TEMPLATE_FILE = "template.json"

ParameterDict = TypedDict("ParameterDict", ParameterSpec.__annotations__)  # type: ignore


class OperationDict(TypedDict):
    """Operation dictionary for the template store."""

    name: str
    data: dict[str, Any]
    advanced_mode: bool


class TemplateDict(TypedDict):
    """Template dictionary for the template store."""

    parameters: list[ParameterDict]
    operations: list[dict]
    datarush_version: str


class TemplateManager(abc.ABC):
    """Abstract base class for template managers."""

    @abc.abstractmethod
    def list_templates(self) -> list[str]:
        """List all templates in the template store."""
        raise NotImplementedError

    @abc.abstractmethod
    def list_template_versions(self, template_name: str) -> list[str]:
        """List all versions of a template in the template store."""
        raise NotImplementedError

    @abc.abstractmethod
    def read_template(self, template_name: str, version: str) -> TemplateDict:
        """Read a template from the template store."""
        raise NotImplementedError

    @abc.abstractmethod
    def write_template(self, template: TemplateDict, template_name: str, version: str) -> None:
        """Write a template to the template store."""
        raise NotImplementedError


class S3TemplateManager(TemplateManager):
    """S3 based template manager."""

    def __init__(self, config: S3TemplateStoreConfig | None = None):
        """Initialize the S3 template manager."""
        config = config or get_datarush_config().template_store.s3
        self._s3 = S3Client()
        self._bucket = config.bucket
        self._prefix = config.prefix

    def list_templates(self) -> list[str]:
        """List all templates in the S3 template store."""
        return self._s3.list_folders(self._bucket, f"{self._prefix}/{_TEMPLATES_FOLDER}")

    def list_template_versions(self, template_name: str) -> list[str]:
        """List all versions of a template in the S3 template store."""
        raw_versions = self._s3.list_folders(
            self._bucket, f"{self._prefix}/{_TEMPLATES_FOLDER}/{template_name}"
        )
        return [v.replace("version=", "") for v in raw_versions if v.startswith("version=")]

    def read_template(self, template_name: str, version: str) -> TemplateDict:
        """Read a template from the S3 template store."""
        key = f"{self._prefix}/{_TEMPLATES_FOLDER}/{template_name}/version={version}/{_TEMPLATE_FILE}"
        obj = self._s3.get_object(self._bucket, key)
        return cast(TemplateDict, json.load(obj))

    def write_template(self, template: TemplateDict, template_name: str, version: str) -> None:
        """Write a template to the S3 template store."""
        key = f"{self._prefix}/{_TEMPLATES_FOLDER}/{template_name}/version={version}/{_TEMPLATE_FILE}"
        if self._s3.list_object_keys(self._bucket, key):
            raise TemplateAlreadyExistsError(f"Template version {version} already exists")

        buffer = BytesIO(json.dumps(template).encode("utf-8"))
        self._s3.put_object(self._bucket, key, buffer)


class FilesystemTemplateManager(TemplateManager):
    """File system based template manager."""

    def __init__(self, config: FilesystemTemplateStoreConfig | None = None):
        """Initialize the filesystem template manager."""
        config = config or get_datarush_config().template_store.filesystem
        self._path = config.path

    def list_templates(self) -> list[str]:
        """List all templates in the filesystem template store."""
        templates_path = f"{self._path}/{_TEMPLATES_FOLDER}"

        if not os.path.exists(templates_path):
            os.makedirs(templates_path, exist_ok=True)
            return []

        return [
            folder
            for folder in os.listdir(templates_path)
            if os.path.isdir(os.path.join(templates_path, folder))
        ]

    def list_template_versions(self, template_name: str) -> list[str]:
        """List all versions of a template in the filesystem template store."""
        template_path = f"{self._path}/{_TEMPLATES_FOLDER}/{template_name}"

        if not os.path.exists(template_path):
            os.makedirs(template_path, exist_ok=True)
            return []

        return [
            folder.replace("version=", "")
            for folder in os.listdir(template_path)
            if os.path.isdir(os.path.join(template_path, folder))
        ]

    def read_template(self, template_name: str, version: str) -> TemplateDict:
        """Read a template from the filesystem."""
        template_path = (
            f"{self._path}/{_TEMPLATES_FOLDER}/{template_name}/version={version}/{_TEMPLATE_FILE}"
        )
        with open(template_path, "r") as f:
            return cast(TemplateDict, json.load(f))

    def write_template(self, template: TemplateDict, template_name: str, version: str) -> None:
        """Write a template to the filesystem."""
        template_path = f"{self._path}/{_TEMPLATES_FOLDER}/{template_name}/version={version}"
        os.makedirs(template_path, exist_ok=True)

        if os.path.exists(f"{template_path}/{_TEMPLATE_FILE}"):
            raise TemplateAlreadyExistsError(f"Template version {version} already exists")

        with open(f"{template_path}/{_TEMPLATE_FILE}", "w") as f:
            json.dump(template, f, indent=4)


@cache
def get_template_manager() -> TemplateManager:
    """Get the configured template manager."""
    config = get_datarush_config().template_store

    if config.store_type == TemplateStoreType.FILESYSTEM:
        return FilesystemTemplateManager(config.filesystem)
    elif config.store_type == TemplateStoreType.S3:
        return S3TemplateManager(config.s3)
    else:
        raise ValueError(f"Unknown template store type: {config.store_type}")


def template_to_dataflow(template: TemplateDict) -> Dataflow:
    """Convert a template to a dataflow."""
    parameters = [ParameterSpec.model_validate(param) for param in template.get("parameters", [])]

    operations: list[Operation] = []
    for operation in template["operations"]:
        operation_type = get_operation_type_by_name(operation["name"])
        operations.append(
            operation_type(
                model_dict=operation["data"],
                advanced_mode=operation.get("advanced_mode", False),
            )
        )

    return Dataflow(parameters=parameters, operations=operations)


def dataflow_to_template(dataflow: Dataflow) -> TemplateDict:
    """Convert a dataflow to a template."""
    parameters = [cast(ParameterDict, param.model_dump()) for param in dataflow.parameters]
    operations = [
        {
            "name": operation.name,
            "data": operation.model_dict,
            "advanced_mode": operation.advanced_mode,
        }
        for operation in dataflow.operations
    ]

    return {"parameters": parameters, "operations": operations, "datarush_version": __version__}
