"""Copy Table operation."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, TableStr


class CopyTableModel(BaseOperationModel):
    """Model for Copy Table operation."""

    source_table: TableStr = Field(title="Source Table", description="Table to copy")
    target_table: str = Field(title="Target Table", description="Name of the new copied table")


class CopyTable(Operation):
    """Operation to copy a table to a new table name."""

    name = "copy_table"
    title = "Copy Table"
    description = "Create a copy of a table under a new name"
    model: CopyTableModel

    def summary(self) -> str:
        """Provide operation summary."""
        return f"Copy `{self.model.source_table}` to `{self.model.target_table}`"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        source_df = tableset.get_df(self.model.source_table)
        tableset.set_df(self.model.target_table, source_df.copy())
        return tableset
