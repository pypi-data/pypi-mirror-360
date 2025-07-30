"""S3 dataset source operation."""

from __future__ import annotations

import re
from typing import Callable

import pandas as pd
from pydantic import BaseModel, Field

from datarush.config import get_datarush_config
from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import (
    ConditionOperator,
    ContentType,
    PartitionFilter,
    PartitionFilterGroup,
)
from datarush.utils.s3_client import DatasetDoesNotExistError, S3Dataset


class S3DatasetSourceModel(BaseModel):
    """S3 dataset Source model."""

    bucket: str = Field(title="Bucket")
    path: str = Field(title="Dataset Path")
    content_type: ContentType = Field(title="Content Type")
    table_name: str = Field(title="Table Name", default="s3_table")
    partition_filter: PartitionFilterGroup = Field(
        title="Partition Filter",
        default=None,  # type: ignore
        description="Filter partitions by conditions",
    )
    error_on_empty: bool = Field(
        title="Error on empty",
        default=True,
        description="Raise an error if the dataset is empty",
    )


class S3DatasetSource(Operation):
    """S3 dataset source operation."""

    name = "read_s3_dataset"
    title = "Read S3 Dataset"
    description = "Download dataset from S3"
    model: S3DatasetSourceModel

    def summary(self) -> str:
        """Provide operation summary."""
        return f"Load S3 dataset as `{self.model.table_name}` table"

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        dataset = S3Dataset(
            bucket=self.model.bucket,
            prefix=self.model.path,
            content_type=self.model.content_type,
            config=get_datarush_config().s3,
        )
        try:
            df = dataset.read(
                partition_filter=(
                    _make_partitions_filter(self.model.partition_filter)
                    if self.model.partition_filter
                    else None
                ),
            )
        except DatasetDoesNotExistError:
            if self.model.error_on_empty:
                raise
            df = pd.DataFrame()
        tableset.set_df(self.model.table_name, df)
        return tableset


def _make_partitions_filter(
    group: PartitionFilterGroup,
) -> Callable[[dict], bool]:
    filters = group.filters or []
    combine = group.combine

    def _evaluate(cond: PartitionFilter, partition: dict) -> bool:
        val = partition.get(cond.column)
        if val is None:
            raise ValueError(f"Partition `{cond.column}` does not exist")

        result = False
        op = cond.operator

        if op == ConditionOperator.EQ:
            result = val == cond.value
        elif op == ConditionOperator.LT:
            result = val < cond.value
        elif op == ConditionOperator.LTE:
            result = val <= cond.value
        elif op == ConditionOperator.GT:
            result = val > cond.value
        elif op == ConditionOperator.GTE:
            result = val >= cond.value
        elif op == ConditionOperator.REGEX:
            result = re.fullmatch(cond.value, val) is not None

        return not result if cond.negate else result

    def _filter(partition: dict) -> bool:
        results = (_evaluate(f, partition) for f in filters)
        return all(results) if combine == "and" else any(results)

    return _filter
