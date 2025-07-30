"""Dict to Columns operation."""

import pandas as pd
from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class DictToColumnsModel(BaseOperationModel):
    """Dict to Columns model."""

    table: TableStr = Field(title="Table", description="Table to modify")
    column: ColumnStr = Field(
        title="Source Column",
        description="Column containing dictionaries to expand",
    )
    drop: bool = Field(
        title="Drop Source Column",
        description="Whether to drop the original dictionary column",
        default=False,
    )


class DictToColumns(Operation):
    """Expand a dictionary column into separate columns."""

    name = "dict_to_columns"
    title = "Dict to Columns"
    description = "Expand dictionary column into multiple columns"
    model: DictToColumnsModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Expand column **{self.model.column}** in `{self.model.table}` "
            f"into separate columns "
            f"({'drop source' if self.model.drop else 'keep source'})"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        dict_col = df[self.model.column]

        if not all(isinstance(val, dict) or pd.isna(val) for val in dict_col):
            raise ValueError(f"All values in `{self.model.column}` must be dicts or null")

        # Create a DataFrame from dicts, using column_key = colname_keyname
        expanded = dict_col.apply(lambda d: {} if pd.isna(d) else d).apply(pd.Series)
        expanded.columns = [f"{self.model.column}_{key}" for key in expanded.columns]

        df = pd.concat([df, expanded], axis=1)

        if self.model.drop:
            df.drop(columns=[self.model.column], inplace=True)

        tableset.set_df(self.model.table, df)
        return tableset
