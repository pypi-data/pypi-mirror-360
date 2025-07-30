"""Filer row operation."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, RowConditionGroup, TableStr
from datarush.utils.conditions import match_conditions


class FilterRowModel(BaseOperationModel):
    """Filter row operation model."""

    table: TableStr = Field(title="Table", description="Table to filter")
    conditions: RowConditionGroup = Field(
        title="Conditions",
        description="Group of conditions to filter rows by",
    )


class FilterByColumn(Operation):
    """Filter row by column value operation."""

    name = "filter_rows"
    title = "Filter Rows"
    description = "Filter table rows by column value"
    model: FilterRowModel

    def summary(self) -> str:
        """Provide operation summary."""
        cols = {c.column for c in self.model.conditions.conditions}
        return f"Filter `{self.model.table}` by {', '.join(cols)}"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        table = self.model.table
        df = tableset.get_df(table)

        mask = match_conditions(
            df=df,
            conditions=self.model.conditions.conditions,
            combine=self.model.conditions.combine,
        )

        tableset.set_df(table, df[mask])
        return tableset
