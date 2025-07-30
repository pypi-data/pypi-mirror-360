"""Normalize empty values operation."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class NormalizeEmptyValuesModel(BaseOperationModel):
    """Normalize empty values operation model."""

    table: TableStr = Field(title="Table", description="Table to modify")
    columns: list[ColumnStr] = Field(
        title="Columns",
        description="Columns to normalize. If empty, all columns are used.",
        default_factory=list,
    )
    custom_empty_values: list[str] = Field(
        title="Custom Empty Values",
        description="Additional strings to treat as empty values (e.g., ['N.A.', 'NA', 'Unknown', ' '])",
        default_factory=list,
    )


class NormalizeEmptyValues(Operation):
    """Normalize empty values in DataFrame columns."""

    name = "normalize_empty_values"
    title = "Normalize Empty Values"
    description = "Convert all empty-like values to null (None/NaN) for consistency"
    model: NormalizeEmptyValuesModel

    def summary(self) -> str:
        """Provide operation summary."""
        cols = (
            ", ".join(f"**{col}**" for col in self.model.columns)
            if self.model.columns
            else "all columns"
        )
        custom_count = len(self.model.custom_empty_values)
        custom_str = f" and {custom_count} custom values" if custom_count > 0 else ""
        return f"Normalize empty values in {cols} of `{self.model.table}`{custom_str}"

    def operate(self, tableset: Tableset) -> Tableset:
        """Apply the normalize empty values operation."""
        df = tableset.get_df(self.model.table)
        target_columns = self.model.columns or df.columns.tolist()

        for col in target_columns:
            if col in df.columns:
                empty_value_mask = df[col].isna()

                empty_values = ["", *self.model.custom_empty_values]
                for custom_value in empty_values:
                    empty_value_mask |= df[col].astype(str) == custom_value

                # Apply the mask
                df.loc[empty_value_mask, col] = None

        tableset.set_df(self.model.table, df)
        return tableset
