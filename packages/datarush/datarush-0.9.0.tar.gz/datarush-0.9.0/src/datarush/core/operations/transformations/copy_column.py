"""Copy Column operation."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class CopyColumnModel(BaseOperationModel):
    """Model for Copy Column operation."""

    table: TableStr = Field(title="Table", description="Table to modify")
    source_column: ColumnStr = Field(title="Source Column", description="Column to copy")
    target_column: str = Field(title="Target Column", description="Name for the new copied column")


class CopyColumn(Operation):
    """Copy a column to a new column name in the same table."""

    name = "copy_column"
    title = "Copy Column"
    description = "Create a copy of a column under a new name in the same table"
    model: CopyColumnModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Copy column **{self.model.source_column}** in `{self.model.table}` "
            f"to new column **{self.model.target_column}**"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        df[self.model.target_column] = df[self.model.source_column].copy()
        tableset.set_df(self.model.table, df)
        return tableset
