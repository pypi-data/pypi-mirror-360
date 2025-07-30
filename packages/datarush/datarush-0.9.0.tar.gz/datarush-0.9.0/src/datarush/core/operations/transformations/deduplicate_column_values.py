"""Deduplicate values inside each list-like cell of a column."""

from typing import Sequence

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class DeduplicateColumnValuesModel(BaseOperationModel):
    """Model for DeduplicateColumnValues operation."""

    table: TableStr = Field(title="Table", description="Table to modify")
    column: ColumnStr = Field(
        title="Target Column",
        description="Column containing list-like values to deduplicate",
    )


class DeduplicateColumnValues(Operation):
    """Remove duplicates from list-like values inside each cell of a column."""

    name = "deduplicate_column_values"
    title = "Deduplicate Column Values"
    description = "Remove duplicates from each list-like cell in the specified column"
    model: DeduplicateColumnValuesModel

    def summary(self) -> str:
        """Provide summary."""
        return (
            f"Deduplicate list values in column **{self.model.column}** "
            f"of `{self.model.table}`"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run the operation."""
        df = tableset.get_df(self.model.table)

        def dedup_list(lst: Sequence) -> Sequence:
            if not isinstance(lst, list):
                return lst
            seen: list = []
            for item in lst:
                if all(item != x for x in seen):
                    seen.append(item)
            return seen

        df[self.model.column] = df[self.model.column].apply(dedup_list)

        tableset.set_df(self.model.table, df)
        return tableset
