"""Explode multiple columns into rows."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class ExplodeModel(BaseOperationModel):
    """Explode columns model."""

    table: TableStr = Field(title="Table", description="Table to modify")
    columns: list[ColumnStr] = Field(title="Columns", description="Columns to explode together")


class Explode(Operation):
    """Explode list-like columns together into multiple rows."""

    name = "explode"
    title = "Explode Columns"
    description = "Explode one or more list-like columns into multiple rows"
    model: ExplodeModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Explode {', '.join(f'**{col}**' for col in self.model.columns)} "
            f"in `{self.model.table}` into multiple rows"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run the explode operation."""
        df = tableset.get_df(self.model.table)
        df = df.explode(self.model.columns, ignore_index=True)
        tableset.set_df(self.model.table, df)
        return tableset
