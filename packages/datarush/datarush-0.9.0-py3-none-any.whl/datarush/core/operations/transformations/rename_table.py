"""Rename table operation."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, TableStr


class RenameTableModel(BaseOperationModel):
    """Rename table model."""

    table: TableStr = Field(title="Current Table", description="Current table name")
    new_name: str = Field(title="New Name", description="New name for the table")


class RenameTable(Operation):
    """Rename a table in the tableset."""

    name = "rename_table"
    title = "Rename Table"
    description = "Rename a table in the tableset"
    model: RenameTableModel

    def summary(self) -> str:
        """Provide operation summary."""
        return f"Rename `{self.model.table}` to `{self.model.new_name}`"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        del tableset[self.model.table]
        tableset.set_df(self.model.new_name, df)
        return tableset
