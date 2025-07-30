"""Unset Header operation for multiple tables."""

import pandas as pd
from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, TableStr


class UnsetHeaderModel(BaseOperationModel):
    """Unset header model for one or more tables."""

    tables: list[TableStr] = Field(title="Tables", description="Tables to unset header from")


class UnsetHeader(Operation):
    """Move current headers to the first row and reset headers to default integers."""

    name = "unset_header"
    title = "Unset Header"
    description = "Move column names to first row and replace headers with default integers"
    model: UnsetHeaderModel

    def summary(self) -> str:
        """Provide operation summary."""
        return f"Unset headers of {', '.join(f'`{t}`' for t in self.model.tables)}"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        for table_name in self.model.tables:
            df = tableset.get_df(table_name)
            header_row = pd.DataFrame([df.columns], columns=df.columns)
            new_df = pd.concat([header_row, df], ignore_index=True)
            new_df.columns = [str(i) for i in range(new_df.shape[1])]
            tableset.set_df(table_name, new_df)
        return tableset
