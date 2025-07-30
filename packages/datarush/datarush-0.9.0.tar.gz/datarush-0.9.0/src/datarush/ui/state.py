"""State management for the Dataflow object in Streamlit session."""

from __future__ import annotations

from typing import Any, NamedTuple, cast

import streamlit as st

from datarush.core.dataflow import Dataflow, Operation, Tableset
from datarush.core.types import ParameterSpec
from datarush.exceptions import OperationError


def get_dataflow() -> DataflowUI:
    """Get the dataflow object from the session state."""
    if "dataflow" not in st.session_state:
        set_dataflow(DataflowUI())
    return cast(DataflowUI, st.session_state["dataflow"])


def set_dataflow(dataflow: Dataflow) -> None:
    """Set the dataflow object in the session state."""
    st.session_state["dataflow"] = DataflowUI.from_dataflow(dataflow)


class DataflowUI(Dataflow):
    """Dataflow with UI-specific methods and properties."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize DataflowUI with optional parameters."""
        super().__init__(*args, **kwargs)
        self._operation_cache: dict[int, _CacheTuple] = {}

    @classmethod
    def from_dataflow(cls, dataflow: Dataflow) -> DataflowUI:
        """Create DataflowUI from an existing Dataflow."""
        return cls(parameters=dataflow.parameters, operations=dataflow.operations)

    def add_parameter(self, parameter: ParameterSpec) -> None:
        """Add parameter spec to this dataflow."""
        self._parameters.append(parameter)

    def remove_parameter(self, position: int) -> None:
        """Remove parameter from this dataflow."""
        if position < 0 or position >= len(self.parameters):
            raise IndexError("position is out of range")
        self._parameters.pop(position)

    def add_operation(self, operation: Operation) -> None:
        """Add operation to this dataflow."""
        self._operations.append(operation)

    def insert_operation(self, index: int, operation: Operation) -> None:
        """Insert operation at the specified index."""
        self._operations.insert(index, operation)
        self._invalidate_cache_from(index)

    def move_operation(self, from_position: int, to_position: int) -> None:
        """Move operation from one position to another."""
        if from_position < 0 or from_position >= len(self.operations):
            raise IndexError("from_position is out of range")
        if to_position < 0 or to_position >= len(self.operations):
            raise IndexError("to_position is out of range")

        item = self._operations.pop(from_position)
        self._operations.insert(to_position, item)
        self._invalidate_cache_from(min(from_position, to_position))

    def remove_operation(self, position: int) -> None:
        """Remove operation."""
        if position < 0 or position >= len(self.operations):
            raise IndexError("position is out of range")
        self._operations.pop(position)
        self._invalidate_cache_from(position)

    def get_tableset_after_operation(self, operation_index: int) -> Tableset | None:
        """Get tableset computed after operation at index or None if not computed yet."""
        if operation_index < 0 or operation_index >= len(self._operations):
            raise IndexError("operation_index is out of range")

        if operation_index not in self._operation_cache:
            return None

        return self._operation_cache[operation_index].tableset

    def run(self) -> None:
        """Run dataflow with caching of operation results.

        This is useful for UI experience where some operations can be expensive to run.
        """
        self._current_tableset = Tableset([])

        cache_valid = True

        for idx, operation in enumerate(self.operations):
            if not operation.is_enabled:
                continue

            context = self.get_current_context()
            operation.update_template_context(context)

            input_hash = operation.input_hash()

            cache_info = self._operation_cache.get(idx)

            if cache_valid and cache_info and cache_info.cache == input_hash:
                self._current_tableset = cache_info.tableset.copy()
            else:
                try:
                    self._current_tableset = operation.operate(self._current_tableset)
                    self._operation_cache[idx] = _CacheTuple(
                        input_hash, self._current_tableset.copy()
                    )
                    cache_valid = False
                except Exception as e:
                    raise OperationError(str(e), operation) from e

    def _invalidate_cache_from(self, start_index: int) -> None:
        keys_to_delete = [i for i in self._operation_cache if i >= start_index]
        for k in keys_to_delete:
            del self._operation_cache[k]


class _CacheTuple(NamedTuple):
    """Named tuple to store cache data."""

    cache: str
    tableset: Tableset
