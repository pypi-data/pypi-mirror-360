"""Parse JSON column operation."""

import json
from typing import Literal

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class ParseJSONColumnModel(BaseOperationModel):
    """Parse JSON column model."""

    table: TableStr = Field(title="Table", description="Table to process")
    column: ColumnStr = Field(title="Column", description="Column containing JSON strings")
    on_error: Literal["null", "error"] = Field(
        title="On Error", description="What to do if JSON parsing fails", default="error"
    )


class ParseJSONColumn(Operation):
    """Convert JSON strings in a column into Python dictionaries."""

    name = "parse_json_column"
    title = "Parse JSON Column"
    description = "Convert stringified JSON column into actual dictionaries"
    model: ParseJSONColumnModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Parse column **{self.model.column}** as JSON in `{self.model.table}` "
            f"(on_error = {self.model.on_error})"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        on_error = self.model.on_error

        def safe_parse(val: str) -> dict | list | None:
            try:
                return json.loads(val)  # type: ignore
            except (TypeError, json.JSONDecodeError):
                if on_error == "error":
                    raise ValueError(f"Failed to parse JSON value: {val}")
                return None

        df[self.model.column] = df[self.model.column].apply(safe_parse)
        tableset.set_df(self.model.table, df)
        return tableset
