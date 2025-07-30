"""Concatenate tables either by rows or columns."""

from typing import Literal

import pandas as pd
from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, TableStr


class ConcatenateTablesModel(BaseOperationModel):
    """Model for ConcatenateTables."""

    tables: list[TableStr] = Field(title="Tables", description="Tables to concatenate")
    output_table: str = Field(title="Output Table", description="Name of the resulting table")
    how: Literal["rows", "columns"] = Field(
        title="How to Concatenate", description="Concatenate by rows or columns", default="rows"
    )
    drop: bool = Field(
        title="Drop Original Tables",
        description="Whether to remove the original tables after concatenation",
        default=False,
    )


class ConcatenateTables(Operation):
    """Concatenate multiple tables by rows or columns."""

    name = "concatenate_tables"
    title = "Concatenate Tables"
    description = "Concatenate multiple tables into one (by rows or columns)"
    model: ConcatenateTablesModel

    def summary(self) -> str:
        """Provide operation summary."""
        how = self.model.how
        drop = " and drop originals" if self.model.drop else ""
        return (
            f"Concatenate {', '.join(f'`{tbl}`' for tbl in self.model.tables)} "
            f"by {how} into `{self.model.output_table}`{drop}"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run the concatenate operation."""
        dfs = [tableset.get_df(name) for name in self.model.tables]

        if self.model.how == "columns":
            lengths = [len(df) for df in dfs]
            if len(set(lengths)) > 1:
                raise ValueError(
                    "All tables must have the same number of rows to concatenate by columns"
                )

            # Check for duplicate column names
            all_columns = [col for df in dfs for col in df.columns]
            duplicates = [col for col in set(all_columns) if all_columns.count(col) > 1]
            if duplicates:
                raise ValueError(f"Duplicate column names found across tables: {duplicates}")

            result_df = pd.concat(dfs, axis=1)

        else:
            result_df = pd.concat(dfs, axis=0, ignore_index=True)

        tableset.set_df(self.model.output_table, result_df)

        if self.model.drop:
            for name in self.model.tables:
                del tableset[name]

        return tableset
