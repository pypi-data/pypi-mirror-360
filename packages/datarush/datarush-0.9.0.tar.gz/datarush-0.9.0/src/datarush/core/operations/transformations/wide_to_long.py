"""Wide to long transformation."""

import pandas as pd
from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class WideToLongModel(BaseOperationModel):
    """Wide to long operation model."""

    table: TableStr = Field(title="Table", description="Table to reshape")
    index_columns: list[ColumnStr] = Field(
        title="Index Columns", description="Columns to keep fixed (identifier variables)"
    )
    value_column: str = Field(
        title="Value Column", description="Name of the resulting value column"
    )
    variable_column: str = Field(
        title="Variable Column",
        description="Name of the resulting variable column (suffix extracted from original column names)",
    )
    stubs: list[str] = Field(
        title="Stubnames",
        description="List of stubname prefixes used to identify wide-format columns",
    )


class WideToLong(Operation):
    """Reshape wide table to long format."""

    name = "wide_to_long"
    title = "Wide to Long"
    description = "Reshape table from wide format to long format using stubnames"
    model: WideToLongModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Reshape `{self.model.table}` from wide to long format "
            f"using stubs {', '.join(self.model.stubs)}; "
            f"new columns: **{self.model.variable_column}**, **{self.model.value_column}**"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        df_long = pd.wide_to_long(
            df,
            stubnames=self.model.stubs,
            i=self.model.index_columns,
            j=self.model.variable_column,
            sep="",
            suffix=r"\d+",
        ).reset_index(names=self.model.index_columns + [self.model.variable_column])
        tableset.set_df(self.model.table, df_long)
        return tableset
