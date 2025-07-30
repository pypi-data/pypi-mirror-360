"""Set Header operation."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, TableStr


class SetHeaderModel(BaseOperationModel):
    """Set header row operation model."""

    table: TableStr = Field(title="Table", description="Table to update header for")
    row_index: int = Field(title="Row Index", description="Row index to use as header (0-based)")


class SetHeader(Operation):
    """Set header row from data row."""

    name = "set_header"
    title = "Set Header"
    description = "Replace the column headers with values from a specified row"
    model: SetHeaderModel

    def summary(self) -> str:
        """Provide operation summary."""
        return f"Set header of `{self.model.table}` using row {self.model.row_index}"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        header_row = df.iloc[self.model.row_index].astype(str).tolist()
        new_df = df.drop(index=self.model.row_index).copy()
        new_df.columns = header_row
        new_df.reset_index(drop=True, inplace=True)
        tableset.set_df(self.model.table, new_df)
        return tableset
