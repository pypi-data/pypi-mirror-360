"""Assert that certain columns exist."""

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class AssertHasColumnsModel(BaseOperationModel):
    """Model for AssertHasColumns."""

    table: TableStr = Field(title="Table", description="Table to check")
    columns: list[ColumnStr] = Field(
        title="Expected Columns", description="Columns that must be present"
    )
    allow_extra: bool = Field(
        title="Allow Extra Columns",
        description="Allow columns beyond the listed ones",
        default=True,
    )


class AssertHasColumns(Operation):
    """Ensure table has specific columns."""

    name = "assert_has_columns"
    title = "Assert Has Columns"
    description = "Assert that a table contains specified columns"
    model: AssertHasColumnsModel

    def summary(self) -> str:
        """Return a summary of the operation."""
        suffix = (
            " (extra columns allowed)" if self.model.allow_extra else " (no extra columns allowed)"
        )
        return (
            f"Assert that `{self.model.table}` contains columns "
            f"{', '.join(f'**{col}**' for col in self.model.columns)}{suffix}"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Check that the specified table has the required columns."""
        df = tableset.get_df(self.model.table)
        actual = set(df.columns)
        expected = set(self.model.columns)

        missing = expected - actual
        if missing:
            raise ValueError(f"Missing columns in `{self.model.table}`: {sorted(missing)}")

        if not self.model.allow_extra:
            extra = actual - expected
            if extra:
                raise ValueError(
                    f"Unexpected extra columns in `{self.model.table}`: {sorted(extra)}"
                )

        return tableset
