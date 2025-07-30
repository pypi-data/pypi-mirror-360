"""Pivot Table operation."""

from typing import Literal

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class PivotTableModel(BaseOperationModel):
    """Pivot table operation model."""

    table: TableStr = Field(title="Table", description="Table to pivot")
    index: list[ColumnStr] = Field(title="Index", description="Columns to group by")
    columns: list[ColumnStr] = Field(title="Columns", description="Columns to spread across")
    values: list[ColumnStr] = Field(title="Values", description="Columns to aggregate")
    aggfunc: Literal["sum", "mean", "count", "min", "max"] = Field(
        title="Aggregation Function", default="sum"
    )
    output_table: str = Field(
        title="Output Table", description="Name of resulting table", default="pivot_table"
    )


class PivotTable(Operation):
    """Pivot table operation."""

    name = "pivot_table"
    title = "Pivot Table"
    description = "Create pivot table from a DataFrame"
    model: PivotTableModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Pivot `{self.model.table}` using index {', '.join(self.model.index)}, "
            f"columns {', '.join(self.model.columns)}, and values {', '.join(self.model.values)} "
            f"aggregated with {self.model.aggfunc} into `{self.model.output_table}`"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        pivoted = df.pivot_table(
            index=self.model.index,
            columns=self.model.columns,
            values=self.model.values,
            aggfunc=self.model.aggfunc,
        ).reset_index()
        tableset.set_df(self.model.output_table, pivoted)
        return tableset
