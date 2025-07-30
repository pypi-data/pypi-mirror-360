"""Join operation."""

from typing import Annotated, Literal

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, ColumnStrMeta, TableStr


class JoinModel(BaseOperationModel):
    """Join operation model."""

    left_table: TableStr = Field(
        title="Left Table",
        description="Left table for join",
    )
    right_table: TableStr = Field(
        title="Right Table",
        description="Right table for join",
    )
    left_on: Annotated[
        ColumnStr,
        ColumnStrMeta(table_field="left_table"),
    ] = Field(
        title="Left Column",
        description="Column in left table to join on",
    )
    right_on: Annotated[
        ColumnStr,
        ColumnStrMeta(table_field="right_table"),
    ] = Field(
        title="Right Column",
        description="Column in right table to join on",
    )
    join_type: Literal["inner", "left", "right", "outer"] = Field(
        title="Join Type",
        description="Type of join to perform",
        default="inner",
    )
    output_table: str = Field(
        title="Output Table",
        description="Name of resulting table",
        default="joined_table",
    )


class JoinTables(Operation):
    """Join two tables operation."""

    name = "join"
    title = "Join Tables"
    description = "Join two tables on specified columns"
    model: JoinModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Join `{self.model.left_table}` and `{self.model.right_table}` "
            f"on {self.model.left_on} = {self.model.right_on} "
            f"with {self.model.join_type} join as `{self.model.output_table}`"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        left_df = tableset.get_df(self.model.left_table)
        right_df = tableset.get_df(self.model.right_table)

        joined_df = left_df.merge(
            right_df,
            how=self.model.join_type,
            left_on=self.model.left_on,
            right_on=self.model.right_on,
        )

        tableset.set_df(self.model.output_table, joined_df)
        return tableset
