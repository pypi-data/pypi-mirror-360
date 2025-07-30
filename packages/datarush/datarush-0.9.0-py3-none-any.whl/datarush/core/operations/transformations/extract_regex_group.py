"""Extract regex group operation."""

import re
from typing import Literal

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class ExtractRegexGroupModel(BaseOperationModel):
    """Extract regex group model."""

    table: TableStr = Field(title="Table", description="Table to modify")
    column: ColumnStr = Field(
        title="Source Column",
        description="Column with string data to apply regex to",
    )
    regex: str = Field(title="Regex", description="Regex pattern with capture groups")
    group: str = Field(
        title="Group",
        description="Capture group to extract (either name or number as string)",
        default="1",
    )
    target_column: str = Field(
        title="Target Column",
        description="Column to store extracted values",
    )
    on_missing: Literal["null", "error"] = Field(
        title="Missing Behavior",
        description="What to do if regex doesn't match",
        default="null",
    )


class ExtractRegexGroup(Operation):
    """Extract regex group from a text column."""

    name = "extract_regex_group"
    title = "Extract Regex Group"
    description = "Extract a named or numbered group from a column using regex"
    model: ExtractRegexGroupModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Extract group **{self.model.group}** from column **{self.model.column}** "
            f"using regex into **{self.model.target_column}** in `{self.model.table}`"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        pattern = re.compile(self.model.regex)
        group_key = int(self.model.group) if self.model.group.isdigit() else self.model.group
        missing = self.model.on_missing

        def extract(value: str) -> str | None:
            match = pattern.search(str(value))
            if match:
                try:
                    return match.group(group_key)
                except (IndexError, KeyError):
                    if missing == "error":
                        raise ValueError(f"Group '{group_key}' not found in regex match.")
                    return None
            else:
                if missing == "error":
                    raise ValueError(f"No match for value: {value}")
                return None

        df[self.model.target_column] = df[self.model.column].apply(extract)
        tableset.set_df(self.model.table, df)
        return tableset
