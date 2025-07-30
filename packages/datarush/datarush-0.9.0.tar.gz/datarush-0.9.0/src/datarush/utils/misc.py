"""Miscellaneous utility functions."""

from io import BytesIO

import pandas as pd

from datarush.core.types import ContentType


def read_file(file: BytesIO, content_type: ContentType) -> pd.DataFrame:
    """Read file content into a DataFrame based on content type."""
    if content_type == ContentType.CSV:
        return pd.read_csv(file)
    elif content_type == ContentType.JSON:
        return pd.read_json(file)
    elif content_type == ContentType.PARQUET:
        return pd.read_parquet(file)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")


def to_file(df: pd.DataFrame, content_type: ContentType) -> BytesIO:
    """Convert a DataFrame to a BytesIO file based on content type."""
    file = BytesIO()
    if content_type == ContentType.CSV:
        df.to_csv(file, index=False)
    elif content_type == ContentType.JSON:
        df.to_json(file, orient="records")
    elif content_type == ContentType.PARQUET:
        df.to_parquet(file, index=False)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")
    file.seek(0)
    return file


def truncate(text: str, max_len: int) -> str:
    """Truncate text to a maximum length with ellipsis."""
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def crossed_out(text: str) -> str:
    """Cross out text for display."""
    return f"~~{text}~~" if text else ""
