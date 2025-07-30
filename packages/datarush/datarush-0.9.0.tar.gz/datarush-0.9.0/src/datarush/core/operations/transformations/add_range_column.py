"""Add range column operation."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, TableStr


class AddRangeColumnModel(BaseOperationModel):
    """Add range column model."""

    table: TableStr = Field(title="Table", description="Table to modify")
    column: str = Field(
        title="Target Column", description="Name of the new column", default="index"
    )
    start: int = Field(title="Start", description="Start value (inclusive)", default=0)
    step: int = Field(title="Step", description="Step between values", default=1)


class AddRangeColumn(Operation):
    """Add a range-based column to a table."""

    name = "add_range_column"
    title = "Add Range Column"
    description = "Add a column generated from a Python-style range into the table"
    model: AddRangeColumnModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Add column **{self.model.column}** with values from "
            f"`range({self.model.start}, ..., step={self.model.step})` "
            f"in `{self.model.table}`"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        stop = self.model.start + self.model.step * len(df)
        df[self.model.column] = list(range(self.model.start, stop, self.model.step))
        tableset.set_df(self.model.table, df)
        return tableset
