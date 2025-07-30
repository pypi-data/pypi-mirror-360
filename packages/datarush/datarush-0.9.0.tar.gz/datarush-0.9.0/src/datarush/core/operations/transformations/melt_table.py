"""Melt operation."""

import pandas as pd
from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class MeltModel(BaseOperationModel):
    """Melt operation model."""

    table: TableStr = Field(title="Table", description="Table to melt")
    id_vars: list[ColumnStr] = Field(
        title="ID Variables", description="Columns to use as identifier variables"
    )
    value_vars: list[ColumnStr] = Field(title="Value Variables", description="Columns to unpivot")
    var_name: str = Field(
        title="Variable Name", description="Name of the variable column", default="variable"
    )
    value_name: str = Field(
        title="Value Name", description="Name of the value column", default="value"
    )
    output_table: str = Field(
        title="Output Table", description="Name of resulting table", default="melted_table"
    )


class Melt(Operation):
    """Melt (unpivot) a DataFrame."""

    name = "melt"
    title = "Melt Table"
    description = "Unpivot a DataFrame from wide to long format"
    model: MeltModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Melt `{self.model.table}` using id_vars={self.model.id_vars} and "
            f"value_vars={self.model.value_vars} into `{self.model.output_table}`"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        melted = pd.melt(
            df,
            id_vars=self.model.id_vars,
            value_vars=self.model.value_vars,
            var_name=self.model.var_name,
            value_name=self.model.value_name,
        )
        tableset.set_df(self.model.output_table, melted)
        return tableset
