"""Columns to Dict operation."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class ColumnsToDictModel(BaseOperationModel):
    """Columns to Dict model."""

    table: TableStr = Field(title="Table", description="Table to modify")
    columns: list[ColumnStr] = Field(
        title="Columns",
        description="Columns to combine into a dictionary",
    )
    output_column: str = Field(
        title="Output Column",
        description="Column to store the resulting dictionary",
    )
    drop: bool = Field(
        title="Drop Original Columns",
        description="Whether to drop the source columns after combining",
        default=False,
    )


class ColumnsToDict(Operation):
    """Combine columns into a dictionary column."""

    name = "columns_to_dict"
    title = "Columns to Dict"
    description = "Combine several columns into a dictionary"
    model: ColumnsToDictModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Create **{self.model.output_column}** in `{self.model.table}` from columns "
            f"{', '.join(f'**{c}**' for c in self.model.columns)} "
            f"({'drop originals' if self.model.drop else 'keep originals'})"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        df[self.model.output_column] = df[self.model.columns].to_dict(orient="records")

        if self.model.drop:
            df.drop(columns=self.model.columns, inplace=True)

        tableset.set_df(self.model.table, df)
        return tableset
