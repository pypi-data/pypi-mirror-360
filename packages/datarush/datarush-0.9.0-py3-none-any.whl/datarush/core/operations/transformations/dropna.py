"""Drop NA operation."""

from __future__ import annotations

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, TableStr


class DropnaModel(BaseOperationModel):
    """Drop NA operation model."""

    table: TableStr = Field(title="Table")


class DropNaValues(Operation):
    """Drop NA operation modules."""

    name = "dropna"
    title = "Drop NA"
    description = "Drop all rows with NA values"
    model: DropnaModel

    def summary(self) -> str:
        """Provide operation summary."""
        return f"Drop NA values in `{self.model.table}`"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        tableset[self.model.table].df.dropna(inplace=True)
        return tableset
