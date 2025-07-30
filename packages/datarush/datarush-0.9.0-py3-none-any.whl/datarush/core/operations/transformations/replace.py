"""Replace values in selected columns."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, StringMap, TableStr


class ReplaceModel(BaseOperationModel):
    """Model for Replace operation."""

    table: TableStr = Field(title="Table", description="Table to modify")
    columns: list[ColumnStr] = Field(
        title="Columns",
        description="Columns to apply replacement. If empty, all columns are used.",
        default_factory=list,
    )
    to_replace: StringMap = Field(
        title="Replacements Map (old -> new)",
        description="Map of values to replace: {old: new}",
        default_factory=StringMap,
    )
    regex: bool = Field(
        title="Use Regex",
        description="If true, treat keys as regular expressions",
        default=False,
    )


class Replace(Operation):
    """Replace values in DataFrame columns."""

    name = "replace"
    title = "Replace"
    description = "Replace values or regex patterns in selected columns"
    model: ReplaceModel

    def summary(self) -> str:
        """Provide operation summary."""
        cols = (
            ", ".join(f"**{col}**" for col in self.model.columns)
            if self.model.columns
            else "all columns"
        )
        mode = "regex" if self.model.regex else "exact match"
        return f"Replace values in {cols} of `{self.model.table}` ({mode})"

    def operate(self, tableset: Tableset) -> Tableset:
        """Apply the replacement."""
        df = tableset.get_df(self.model.table)
        target_columns = self.model.columns or df.columns.tolist()

        df[target_columns] = df[target_columns].replace(
            to_replace=self.model.to_replace, regex=self.model.regex
        )

        tableset.set_df(self.model.table, df)
        return tableset
