"""Transpose operation."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, TableStr


class TransposeModel(BaseOperationModel):
    """Transpose operation model."""

    table: TableStr = Field(title="Table", description="Table to transpose")


class Transpose(Operation):
    """Transpose a table (rows become columns and vice versa)."""

    name = "transpose"
    title = "Transpose Table"
    description = "Transpose a table in-place"
    model: TransposeModel

    def summary(self) -> str:
        """Provide operation summary."""
        return f"Transpose `{self.model.table}`"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        transposed_df = df.transpose()
        tableset.set_df(self.model.table, transposed_df)
        return tableset
