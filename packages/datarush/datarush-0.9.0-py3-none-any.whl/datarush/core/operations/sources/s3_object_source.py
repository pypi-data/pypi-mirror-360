"""S3 object source operation."""

from __future__ import annotations

from pydantic import BaseModel, Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import ContentType
from datarush.utils.misc import read_file
from datarush.utils.s3_client import S3Client


class S3SourceModel(BaseModel):
    """S3 object Source model."""

    bucket: str = Field(title="Bucket")
    object_key: str = Field(title="Object Key")
    content_type: ContentType = Field(title="Content Type")
    table_name: str = Field(title="Table Name", default="s3_table")


class S3ObjectSource(Operation):
    """S3 object source operation."""

    name = "read_s3_object"
    title = "Read S3 Object"
    description = "S3 Object Source"
    model: S3SourceModel

    def summary(self) -> str:
        """Provide operation summary."""
        return f"Load S3 object as `{self.model.table_name}` table"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        obj = S3Client().get_object(self.model.bucket, self.model.object_key)
        df = read_file(obj, self.model.content_type)
        tableset.set_df(self.model.table_name, df)
        return tableset
