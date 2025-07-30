"""S3 dataset sink operation."""

from __future__ import annotations

from pydantic import Field

from datarush.config import get_datarush_config
from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, ContentType, TableStr
from datarush.utils.s3_client import DatasetWriteMode, S3Dataset


class S3DatasetSinkModel(BaseOperationModel):
    """Pydantic model for S3 dataset sink operation."""

    bucket: str = Field(title="Bucket")
    path: str = Field(title="Dataset path")
    content_type: ContentType = Field(title="Content type")
    mode: DatasetWriteMode = Field(title="Write mode")
    table: TableStr = Field(title="Table to write")
    partition_columns: list[ColumnStr] = Field(
        title="Partition columns", default=None, description="List of columns to partition by"  # type: ignore
    )
    unique_ids: list[ColumnStr] = Field(
        title="Unique IDs",
        default=None,  # type: ignore
        description="List of columns to use as unique IDs for the dataset records deduplication. Only relevant for append mode.",
    )


class S3DatasetSink(Operation):
    """Operation that writes a table to an S3 dataset."""

    name = "write_s3_dataset"
    title = "Write S3 Dataset"
    description = "Write table as S3 dataset"
    model: S3DatasetSinkModel

    def summary(self) -> str:
        """Return a short summary of the operation."""
        path = f"{self.model.bucket}/{self.model.path.strip('/')}"
        return (
            f"Write `{self.model.table}` to S3 dataset {path}"
            f" as {self.model.content_type.value}"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Write table to S3 dataset and return unmodified tableset."""
        dataset = S3Dataset(
            bucket=self.model.bucket,
            prefix=self.model.path,
            content_type=self.model.content_type,
            partition_columns=self.model.partition_columns,
            unique_ids=self.model.unique_ids,
            write_mode=self.model.mode,
            config=get_datarush_config().s3,
        )
        df = tableset.get_df(self.model.table)
        dataset.write(df)
        return tableset
