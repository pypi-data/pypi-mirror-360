"""Calculate Hash operation."""

from hashlib import blake2b, md5, sha1, sha256
from typing import Callable, Literal

import pandas as pd
from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr

_HASH_FUNC_MAP: dict[str, Callable] = {
    "md5": md5,
    "sha1": sha1,
    "sha256": sha256,
    "blake2b": blake2b,
}


class CalculateHashModel(BaseOperationModel):
    """CalculateHash operation model."""

    table: TableStr = Field(title="Table", description="Table to modify")
    columns: list[ColumnStr] = Field(
        title="Columns", description="Columns to combine before hashing"
    )
    target_column: str = Field(title="Target Column", description="Where to store the hash")
    hash_func: Literal["md5", "sha1", "sha256", "blake2b"] = Field(
        title="Hash Function", default="md5", description="Hash function to use"
    )


class CalculateHash(Operation):
    """Calculate deterministic hash of selected columns."""

    name = "calculate_hash"
    title = "Calculate Hash"
    description = "Combine values from multiple columns and calculate a deterministic hash"
    model: CalculateHashModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Hash columns {', '.join(f'**{c}**' for c in self.model.columns)} in `{self.model.table}` "
            f"using **{self.model.hash_func}** into **{self.model.target_column}**"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)

        hasher = _HASH_FUNC_MAP[self.model.hash_func]

        def row_hash(row: pd.Series) -> str:
            # Convert values to string and join with '|'
            raw = "|".join(str(row[col]) for col in self.model.columns)
            return hasher(raw.encode("utf-8")).hexdigest()  # type: ignore

        df[self.model.target_column] = df.apply(row_hash, axis=1)
        tableset.set_df(self.model.table, df)
        return tableset
