"""Local file source."""

from __future__ import annotations

from io import BytesIO

from pydantic import BaseModel, Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import ContentType
from datarush.utils.misc import read_file


class LocalFileModel(BaseModel):
    """Local file source model."""

    content_type: ContentType = Field(title="Content Type")
    file: bytes = Field(title="File")
    table_name: str = Field(title="Table Name", default="local_table")


class LocalFileSource(Operation):
    """Local file source operation."""

    name = "local_file"
    title = "Local File"
    description = "Local File Source"
    model: LocalFileModel

    def summary(self) -> str:
        """Provide operation summary."""
        return f"Load local file as `{self.model.table_name}` table"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = read_file(BytesIO(self.model.file), self.model.content_type)
        tableset.set_df(self.model.table_name, df)
        return tableset
