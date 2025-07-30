"""Application exceptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datarush.core.dataflow import Operation


class DataRushError(Exception):
    """Base exception."""


class UnknownTableError(DataRushError):
    """Unknown table error."""


class TemplateAlreadyExistsError(DataRushError):
    """Template already exists error."""


class OperationError(DataRushError):
    """Operation errors."""

    def __init__(self, message: str, operation: Operation) -> None:
        """Initialize the operation."""
        super().__init__(message)
        self._operation = operation

    def summary(self) -> str:
        """Return a summary of the error."""
        return f"Operation {self._operation.name} ({self._operation.summary()}) failed: \n\n {self.args[0]}"
