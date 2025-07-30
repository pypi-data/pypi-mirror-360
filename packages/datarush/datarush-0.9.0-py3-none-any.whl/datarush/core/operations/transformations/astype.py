"""Astype operation."""

from typing import Literal

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class AstypeModel(BaseOperationModel):
    """Astype operation model."""

    table: TableStr = Field(title="Table", description="Table to modify")
    column: ColumnStr = Field(title="Column", description="Column to convert type")
    dtype: Literal[
        "int",
        "float",
        "string",
        "boolean",
        "category",
    ] = Field(title="Target Type", description="Target data type for the column")
    errors: Literal["raise", "ignore"] = Field(
        title="Error Handling",
        description="Whether to raise or ignore conversion errors",
        default="raise",
    )


class AsType(Operation):
    """Convert column data type using pandas astype."""

    name = "astype"
    title = "Cast Column Type"
    description = "Change the data type of a column using pandas astype"
    model: AstypeModel

    def summary(self) -> str:
        """Provide operation summary."""
        return f"Convert {self.model.column} in `{self.model.table}` to {self.model.dtype}"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        df[self.model.column] = df[self.model.column].astype(
            self.model.dtype, errors=self.model.errors
        )
        tableset.set_df(self.model.table, df)
        return tableset
