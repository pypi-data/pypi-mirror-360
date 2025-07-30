"""Types definitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal, Type

from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic.fields import FieldInfo
from pydantic_core import CoreSchema, core_schema


class ContentType(StrEnum):
    """Enum representing content types."""

    CSV = "CSV"
    JSON = "JSON"
    PARQUET = "PARQUET"

    def extension(self) -> list[str]:
        """Get file extensions associated with the content type."""
        return {
            ContentType.CSV: [".csv"],
            ContentType.JSON: [".json"],
            ContentType.PARQUET: [".parquet"],
        }[self]


class ValueType(StrEnum):
    """Input parameters types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"

    def get_type(self) -> Type:
        """Get the corresponding Python type for the parameter type."""
        return {
            ValueType.STRING: str,
            ValueType.INTEGER: int,
            ValueType.FLOAT: float,
            ValueType.DATE: date,
            ValueType.DATETIME: datetime,
            ValueType.BOOLEAN: bool,
        }[self]


class ParameterSpec(BaseModel):
    """Parameter specification."""

    name: str
    type: ValueType
    description: str
    default: str
    required: bool


class TableStr(str):
    """Special string type to mark field that takes table name as input."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Get custom schema for Pydantic validation."""
        return core_schema.no_info_after_validator_function(
            lambda v: TableStr(v), core_schema.str_schema()
        )


class ColumnStr(str):
    """Special string type to mark field that takes column name as input."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Get custom schema for Pydantic validation."""
        return core_schema.no_info_after_validator_function(
            lambda v: ColumnStr(v), core_schema.str_schema()
        )


class TextStr(str):
    """Special string type to mark field that takes multiline text input."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Get custom schema for Pydantic validation."""
        return core_schema.no_info_after_validator_function(
            lambda v: TextStr(v), core_schema.str_schema()
        )


class StringMap(dict):
    """Special dict type to mark field that takes dict[str, str] as input."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Get custom schema for Pydantic validation."""
        return core_schema.no_info_after_validator_function(
            lambda v: StringMap(v),
            core_schema.dict_schema(
                keys_schema=core_schema.str_schema(), values_schema=core_schema.str_schema()
            ),
        )


@dataclass(frozen=True)
class ColumnStrMeta:
    """Metadata for ColumnStr type."""

    table_field: str = "table"
    tables_field: str = "tables"
    table_fields: list[str] | None = None

    @classmethod
    def from_pydantic_field(cls, field: FieldInfo) -> ColumnStrMeta:
        """Extract ColumnStrMeta from Pydantic field metadata."""
        for annotation in field.metadata or []:
            if isinstance(annotation, ColumnStrMeta):
                return annotation
        return ColumnStrMeta()


class ConditionOperator(StrEnum):
    """Operators for conditions."""

    EQ = "equals"
    LT = "is less than"
    LTE = "is less than or equals"
    GT = "is greater than"
    GTE = "is greater than or equals"
    REGEX = "matches regex"


class RowCondition(BaseModel):
    """Condition for filtering DataFrame."""

    column: str
    operator: ConditionOperator
    value: str
    value_type: ValueType = ValueType.STRING
    negate: bool = False

    def summary(self) -> str:
        """Provide a summary of the condition."""
        negate_str = "not " if self.negate else ""
        return f"{negate_str} {self.column} {self.operator.value} {self.value}"


class RowConditionGroup(BaseModel):
    """Group of conditions for filtering DataFrame."""

    conditions: list[RowCondition]
    combine: Literal["and", "or"] = "and"


class PartitionFilter(BaseModel):
    """Dataset partition filter."""

    column: str
    operator: ConditionOperator
    value: str
    negate: bool = False

    def summary(self) -> str:
        """Provide a summary of the condition."""
        negate_str = "not " if self.negate else ""
        return f"{negate_str}{self.column} {self.operator.value} {self.value}"


class PartitionFilterGroup(BaseModel):
    """Group of partition filters."""

    filters: list[PartitionFilter] | None = None
    combine: Literal["and", "or"] = "and"


class BaseOperationModel(BaseModel):
    """Base model for operations."""
