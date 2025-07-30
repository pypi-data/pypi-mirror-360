"""S3 client wrapper for basic file and folder operations."""

import logging
from enum import StrEnum
from io import BytesIO
from typing import Any, Sequence

import awswrangler as wr
import boto3
import pandas as pd
from botocore.client import Config

from datarush.config import S3Config, get_datarush_config
from datarush.core.types import ContentType

LOG = logging.getLogger(__name__)


class DatasetDoesNotExistError(Exception):
    """Exception raised when a dataset does not exist."""


class S3Client:
    """S3 Client."""

    def __init__(self, config: S3Config | None = None) -> None:
        """Initialize the S3 client with configuration."""
        config = config or get_datarush_config().s3
        LOG.debug(f"Initializing S3 client with endpoint: {config.endpoint}")
        self._client = boto3.client(
            "s3",
            endpoint_url=config.endpoint,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key.reveal(),
            aws_session_token=(config.session_token.reveal() if config.session_token else None),
            region_name=config.region_name,
            aws_account_id=config.account_id,
            config=Config(signature_version="s3v4"),
        )
        LOG.debug("S3 client initialized successfully")

    def get_object(self, bucket: str, key: str) -> BytesIO:
        """Retrieve an object from S3 as BytesIO."""
        LOG.debug(f"Retrieving object from S3: {bucket}/{key}")
        obj = self._client.get_object(Bucket=bucket, Key=key)
        LOG.debug(f"Successfully retrieved object: {bucket}/{key}")
        return BytesIO(obj["Body"].read())

    def put_object(self, bucket: str, key: str, body: BytesIO) -> None:
        """Upload an object to S3."""
        LOG.debug(f"Uploading object to S3: {bucket}/{key}")
        self._client.put_object(Bucket=bucket, Key=key, Body=body)
        LOG.debug(f"Successfully uploaded object: {bucket}/{key}")

    def delete_object(self, bucket: str, key: str) -> None:
        """Delete an object from S3."""
        self._client.delete_object(Bucket=bucket, Key=key)

    def list_object_keys(self, bucket: str, prefix: str) -> list[str]:
        """List object keys under a prefix in an S3 bucket."""
        prefix = prefix.strip("/")
        response = self._client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        objects = response.get("Contents", [])
        return [obj["Key"] for obj in objects]

    def list_folders(self, bucket: str, prefix: str) -> list[str]:
        """List folder names under a prefix in an S3 bucket."""
        prefix = prefix.strip("/") + "/"
        keys = self.list_object_keys(bucket, prefix)
        if prefix == "/":
            return list({key.split("/")[0] for key in keys})
        return list({key.split(prefix)[1].split("/")[0] for key in keys})


class DatasetWriteMode(StrEnum):
    """Write mode for S3 dataset sink."""

    OVERWRITE = "overwrite"
    OVERWRITE_PARTITIONS = "overwrite_partitions"
    APPEND = "append"


class S3Dataset:
    """S3 Dataset Client."""

    def __init__(
        self,
        bucket: str,
        prefix: str,
        content_type: ContentType,
        partition_columns: Sequence[str] | None = None,
        unique_ids: Sequence[str] | None = None,
        write_mode: DatasetWriteMode = DatasetWriteMode.APPEND,
        config: S3Config | None = None,
    ) -> None:
        """Initialize the S3 dataset client with configuration."""
        self._content_type = content_type
        self._path = f"s3://{bucket}/{prefix.strip('/')}"
        LOG.debug(f"Initializing S3 dataset client for path: {self._path}")

        self._write_mode = write_mode.value
        self._partition_columns = partition_columns or []
        self._unique_ids = unique_ids or []
        LOG.debug(
            f"Dataset configuration: content_type={content_type}, write_mode={write_mode}, "
            f"partition_columns={self._partition_columns}, unique_ids={self._unique_ids}"
        )

        self._config = config or get_datarush_config().s3
        self._session = boto3.Session(
            aws_access_key_id=self._config.access_key,
            aws_secret_access_key=self._config.secret_key.reveal(),
            aws_session_token=(
                self._config.session_token.reveal() if self._config.session_token else None
            ),
            region_name=self._config.region_name,
            aws_account_id=self._config.account_id,
            profile_name=self._config.profile_name,
        )
        wr.config.s3_endpoint_url = self._config.endpoint
        LOG.debug("S3 dataset client initialized successfully")

    def read(self, **kwargs: Any) -> pd.DataFrame:
        """Read a dataset from S3."""
        LOG.info(f"Reading dataset from S3: {self._path} (content_type: {self._content_type})")

        common_kwargs = dict(
            boto3_session=self._session,
            path=self._path,
            dataset=True,
        )

        try:
            if self._content_type == ContentType.JSON:
                LOG.debug("Reading JSON dataset")
                df = wr.s3.read_json(**common_kwargs, **kwargs)
            elif self._content_type == ContentType.CSV:
                LOG.debug("Reading CSV dataset")
                df = wr.s3.read_csv(**common_kwargs, **kwargs)
            elif self._content_type == ContentType.PARQUET:
                LOG.debug("Reading Parquet dataset")
                df = wr.s3.read_parquet(**common_kwargs, **kwargs)
            else:
                raise ValueError(f"Unsupported content type: {self._content_type}")
        except wr.exceptions.NoFilesFound:
            LOG.error(f"Dataset does not exist at {self._path}")
            raise DatasetDoesNotExistError(f"Dataset does not exist at {self._path}")

        LOG.info(f"Successfully read dataset with shape: {df.shape}")
        return df

    def write(self, df: pd.DataFrame, **kwargs: Any) -> None:
        """Write a DataFrame to S3."""
        LOG.info(
            f"Writing DataFrame to S3: {self._path} (shape: {df.shape}, content_type: {self._content_type})"
        )

        if df.empty:
            LOG.warning("DataFrame is empty, skipping write operation")
            return

        if self._unique_ids and self._write_mode != DatasetWriteMode.APPEND:
            LOG.error("unique_ids are only supported in APPEND mode")
            raise ValueError("unique_ids are only supported in APPEND mode")

        if self._unique_ids:
            LOG.debug("Writing with unique IDs deduplication")
            self._write_unique(df, **kwargs)
        else:
            LOG.debug("Writing without unique IDs")
            self._write(df, **kwargs)

    def _write(self, df: pd.DataFrame, **kwargs: Any) -> None:
        if df.empty:
            return

        common_kwargs = dict(
            df=df,
            path=self._path,
            dataset=True,
            boto3_session=self._session,
            partition_cols=self._partition_columns,
            mode=self._write_mode,
            index=False,
        )

        if self._content_type == ContentType.JSON:
            wr.s3.to_json(orient="records", lines=True, **common_kwargs)
        elif self._content_type == ContentType.CSV:
            wr.s3.to_csv(**common_kwargs)
        elif self._content_type == ContentType.PARQUET:
            wr.s3.to_parquet(**common_kwargs)
        else:
            raise ValueError(f"Unsupported content type: {self._content_type}")

    def _write_unique(self, df: pd.DataFrame, **kwargs: Any) -> None:
        """Write a DataFrame to S3 with unique IDs."""
        unique_ids = list(self._partition_columns) + list(self._unique_ids)

        missing_columns = [col for col in unique_ids if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns {missing_columns} not found in DataFrame columns.")

        if self._partition_columns:
            unique_partitions = df[self._partition_columns].drop_duplicates().to_dict("records")
            unique_partitions_set = set(frozenset(d.items()) for d in unique_partitions)

            def partition_filter(row: dict[str, str]) -> bool:
                return frozenset(row.items()) in unique_partitions_set

        else:
            partition_filter = None  # type: ignore

        try:
            current_df = self.read(partition_filter=partition_filter)
            df = df.merge(current_df[unique_ids], on=unique_ids, how="left", indicator=True)
            df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])
        except DatasetDoesNotExistError:
            pass

        self._write(df, **kwargs)
