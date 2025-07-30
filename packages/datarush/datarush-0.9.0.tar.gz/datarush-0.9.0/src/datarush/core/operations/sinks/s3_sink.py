"""S3 object sink."""

from __future__ import annotations

from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ContentType, TableStr
from datarush.utils.misc import to_file
from datarush.utils.s3_client import S3Client


class S3SinkModel(BaseOperationModel):
    """Pydantic model for S3 sink operation."""

    bucket: str = Field(title="Bucket")
    object_key: str = Field(title="Object Key")
    content_type: ContentType = Field(title="Content Type")
    table: TableStr = Field(title="Table to write")


class S3ObjectSink(Operation):
    """Operation that writes a table to an S3 object."""

    name = "write_s3_object"
    title = "Write S3 Object"
    description = "S3 Object Sink"
    model: S3SinkModel

    def summary(self) -> str:
        """Return a short summary of the operation."""
        return (
            f"Write `{self.model.table}` to S3 {self.model.bucket}/{self.model.object_key}"
            f" as {self.model.content_type.value}"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Write table to S3 and return unmodified tableset."""
        df = tableset.get_df(self.model.table)
        file = to_file(df, self.model.content_type)
        S3Client().put_object(self.model.bucket, self.model.object_key, file)
        return tableset
