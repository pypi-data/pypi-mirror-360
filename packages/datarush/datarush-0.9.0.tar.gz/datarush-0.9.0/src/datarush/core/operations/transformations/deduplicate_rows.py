"""Deduplicate rows operation."""

from typing import Literal

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class DeduplicateRowsModel(BaseOperationModel):
    """Model for deduplicating rows."""

    table: TableStr = Field(title="Table", description="Table to deduplicate")
    columns: list[ColumnStr] = Field(
        title="Columns",
        description="Columns to consider for identifying duplicates",
    )
    keep: Literal["first", "last", "none"] = Field(
        title="Keep",
        description="Which duplicate to keep: 'first', 'last', or 'none' to drop all",
        default="first",
    )


class DeduplicateRows(Operation):
    """Remove duplicate rows from a table."""

    name = "deduplicate_rows"
    title = "Deduplicate Rows"
    description = "Remove duplicate rows from a table based on selected columns"
    model: DeduplicateRowsModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Deduplicate rows in `{self.model.table}` based on columns "
            f"{', '.join(f'**{col}**' for col in self.model.columns)} "
            f"(keep = {self.model.keep})"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        keep_arg = False if self.model.keep == "none" else self.model.keep
        df = tableset.get_df(self.model.table)
        df = df.drop_duplicates(subset=self.model.columns, keep=keep_arg)
        tableset.set_df(self.model.table, df)
        return tableset
