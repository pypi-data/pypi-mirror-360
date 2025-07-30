"""Dataflow related definitions."""

from __future__ import annotations

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Iterable, Iterator, Type, get_type_hints

import pandas as pd

from datarush.core.types import BaseOperationModel, ParameterSpec
from datarush.exceptions import UnknownTableError
from datarush.utils.jinja2 import model_validate_jinja2
from datarush.utils.logging import OperationLogger

LOG = logging.getLogger(__name__)


class Table:
    """Table representation."""

    def __init__(self, name: str, df: pd.DataFrame) -> None:
        """Initialize table with name and dataframe."""
        self.name = name
        self.df = df

    def copy(self) -> Table:
        """Return a deep copy of this table."""
        return Table(self.name, self.df.copy())


class Tableset:
    """Represent collection of tables."""

    def __init__(self, tables: Iterable[Table]) -> None:
        """Initialize tableset with a list of tables."""
        self._table_map = {table.name: table for table in tables}

    def copy(self) -> Tableset:
        """Return a deep copy of this tableset."""
        return Tableset(table.copy() for table in self._table_map.values())

    def get_df(self, name: str) -> pd.DataFrame:
        """Get dataframe by the name of its table."""
        table = self._table_map.get(name)
        if not table:
            LOG.error(
                f"Table '{name}' not found. Available tables: {list(self._table_map.keys())}"
            )
            raise UnknownTableError(name)
        LOG.debug(f"Retrieved table '{name}' with shape {table.df.shape}")
        return table.df

    def set_df(self, name: str, df: pd.DataFrame) -> None:
        """Set dataframe for the given table name."""
        LOG.debug(f"Setting table '{name}' with shape {df.shape}")
        self._table_map[name] = Table(name, df)

    def __getitem__(self, key: str) -> Table:
        """Get table by name."""
        return self._table_map[key]

    def __setitem__(self, key: str, value: Table) -> None:
        """Set table by name."""
        self._table_map[key] = value

    def __delitem__(self, key: str) -> None:
        """Delete table by name."""
        del self._table_map[key]

    def __iter__(self) -> Iterator[str]:
        """Iterate over table names."""
        return iter(self._table_map.keys())

    def __bool__(self) -> bool:
        """Return False if there are no tables and True otherwise."""
        return bool(self._table_map)


# flake8: noqa: D103
class Operation[T: BaseOperationModel](ABC):
    """Represent operation."""

    is_enabled: bool = True
    advanced_mode: bool = False

    def __init__(self, model_dict: dict[str, Any], advanced_mode: bool = False) -> None:
        """Initialize operation with model dictionary and mode."""
        self._model_dict = model_dict
        self._template_context: dict[str, Any] = {}
        self.advanced_mode = advanced_mode
        self.initialize()

    def initialize(self) -> None:
        """Initialize operation."""
        pass

    @property
    def model_dict(self) -> dict[str, Any]:
        """Get dictionary with operation parameters."""
        return self._model_dict

    @property
    def model(self) -> T:
        """Get model with operation parameters."""
        if not self.advanced_mode:
            return self.schema().model_validate(self.model_dict)

        return model_validate_jinja2(
            self.schema(), self.model_dict, context=self._template_context
        )

    @classmethod
    def schema(cls) -> Type[T]:
        """Get the model schema/type used by this operation."""
        return get_type_hints(cls)["model"]  # type: ignore

    def update_template_context(self, context: dict[str, Any]) -> None:
        """Update the template context for Jinja2 rendering."""
        self._template_context = context

    def input_hash(self) -> str:
        key_data = {
            "class": self.__class__.__name__,
            "model_dict": self.model_dict,
            "context": self._template_context,
            "advanced_mode": self.advanced_mode,
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    @property
    @abstractmethod
    def name(self) -> str:
        """Get operation unique name."""
        raise NotImplementedError

    @property
    @abstractmethod
    def title(self) -> str:
        """Get operation title."""
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        """Get operation description."""
        raise NotImplementedError

    @abstractmethod
    def operate(self, tableset: Tableset) -> Tableset:
        """Perform the operation on the given tableset."""
        raise NotImplementedError

    @abstractmethod
    def summary(self) -> str:
        """Provide a summary of the operation."""
        raise NotImplementedError


class Dataflow:
    """Organize parameters, tables and operations into a data pipeline."""

    def __init__(
        self,
        parameters: list[ParameterSpec] | None = None,
        operations: list[Operation] | None = None,
    ) -> None:
        """Initialize dataflow with optional parameters and operations."""
        self._current_tableset = Tableset([])
        self._parameters = parameters or []
        self._parameters_values: dict[str, Any] = {}
        self._operations = operations or []

    @property
    def current_tableset(self) -> Tableset:
        """Get current tableset."""
        return self._current_tableset

    @property
    def parameters(self) -> list[ParameterSpec]:
        """Get parameter specs configured for this dataflow."""
        return self._parameters

    @property
    def operations(self) -> list[Operation]:
        """Get operations."""
        return self._operations

    def set_parameter_value(self, name: str, value: Any) -> None:
        """Set parameter value."""
        if name not in [p.name for p in self.parameters]:
            raise KeyError(f"Parameter {name} not found")
        self._parameters_values[name] = value

    def set_parameters_values(self, values: dict[str, Any]) -> None:
        """Set a dictionary with parameter values."""
        for name, value in values.items():
            self.set_parameter_value(name, value)

    def get_current_context(self) -> dict[str, Any]:
        """Get the current context for the dataflow."""
        return {"parameters": self._parameters_values}

    def run(self) -> None:
        """Run dataflow by executing all enabled operations."""
        self._current_tableset = Tableset([])
        LOG.debug("Initialized empty tableset")

        for i, operation in enumerate(self.operations, 1):
            if not operation.is_enabled:
                LOG.debug(
                    f"Skipping disabled operation {i}/{len(self.operations)}: {operation.title}"
                )
                continue

            LOG.info(f"Executing operation {i}/{len(self.operations)}: {operation.title}")

            context = self.get_current_context()
            operation.update_template_context(context)

            with OperationLogger(operation.name, operation.title, LOG):
                self._current_tableset = operation.operate(self._current_tableset)

            # Log tableset state after operation
            table_names = list(self._current_tableset)
            LOG.debug(f"Tableset after operation {i}: {table_names}")
