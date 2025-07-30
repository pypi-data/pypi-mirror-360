"""GroupBy operation."""

from typing import Literal

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class GroupByModel(BaseOperationModel):
    """GroupBy operation model."""

    table: TableStr = Field(title="Table", description="Table to group")
    group_by: list[ColumnStr] = Field(title="Group By", description="Columns to group by")
    aggregation_column: ColumnStr = Field(
        title="Aggregation Column", description="Column to aggregate"
    )
    agg_func: Literal["sum", "mean", "min", "max", "count"] = Field(
        title="Aggregation Function",
        description="Function to apply on grouped column",
        default="count",
    )
    output_table: str = Field(
        title="Output Table", description="Name of resulting table", default="grouped_table"
    )


class GroupBy(Operation):
    """GroupBy operation."""

    name = "groupby"
    title = "Group By"
    description = "Group table by one or more columns and apply aggregation"
    model: GroupByModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Group `{self.model.table}` by {', '.join(self.model.group_by)} "
            f"and compute {self.model.agg_func} on `{self.model.aggregation_column}` "
            f"as `{self.model.output_table}`"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        grouped_df = (
            df.groupby(self.model.group_by)[self.model.aggregation_column]
            .agg(self.model.agg_func)
            .reset_index()
        )
        tableset.set_df(self.model.output_table, grouped_df)
        return tableset
