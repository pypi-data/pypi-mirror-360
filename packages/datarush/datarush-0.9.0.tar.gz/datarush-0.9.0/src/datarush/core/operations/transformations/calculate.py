"""Calculate operation - apply math expression to columns."""

import pandas as pd
from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, TableStr


class CalculateModel(BaseOperationModel):
    """Calculate operation model."""

    table: TableStr = Field(title="Table", description="Table to apply the calculation to")
    target_column: str = Field(title="Target Column", description="Name of column to store result")
    expression: str = Field(
        title="Expression",
        description=(
            "Math expression using existing columns. The following arithmetic operations are supported:"
            " +, -, *, /, **, %, along with the following boolean operations: | (or), & (and), and ~ (not)"
        ),
    )


class Calculate(Operation):
    """Apply math expression to table columns."""

    name = "calculate"
    title = "Calculate"
    description = "Compute new column using a math expression involving existing columns"
    model: CalculateModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Calculate {self.model.target_column} in `{self.model.table}` "
            f"as `{self.model.expression}`"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        df[self.model.target_column] = pd.eval(self.model.expression, local_dict=df)
        tableset.set_df(self.model.table, df)
        return tableset
