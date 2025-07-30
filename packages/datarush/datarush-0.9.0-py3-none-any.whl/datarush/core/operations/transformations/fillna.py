"""Fill NA operation."""

from typing import Literal

import pandas as pd
from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, ColumnStr, TableStr


class FillnaModel(BaseOperationModel):
    """Fill NA operation model."""

    table: TableStr = Field(title="Table", description="Table to modify")
    columns: list[ColumnStr] = Field(
        title="Columns",
        description="Columns to fill. If empty, all columns are used.",
        default_factory=list,
    )
    method: Literal["ffill", "bfill", "mean", "median", "mode", "constant"] = Field(
        title="Fill Method",
        description="Method to use for filling missing values",
        default="constant",
    )
    value: str = Field(
        title="Fill Value",
        description="Value to use when method is 'constant'. For numeric columns, use numbers like '0' or '1.5'",
        default="",
    )
    limit: int = Field(
        title="Limit",
        description="Maximum number of consecutive fills for ffill/bfill methods",
        default=None,  # type: ignore
    )
    axis: Literal["rows", "columns"] = Field(
        title="Axis",
        description="Axis along which to fill (for ffill/bfill methods)",
        default="rows",
    )


class FillNa(Operation):
    """Fill missing values in DataFrame columns."""

    name = "fillna"
    title = "Fill NA"
    description = "Fill missing values in selected columns using various methods"
    model: FillnaModel

    def summary(self) -> str:
        """Provide operation summary."""
        cols = (
            ", ".join(f"**{col}**" for col in self.model.columns)
            if self.model.columns
            else "all columns"
        )
        method = self.model.method
        if method == "constant":
            method_str = f"constant value '{self.model.value}'"
        else:
            method_str = method
        return f"Fill NA values in {cols} of `{self.model.table}` using {method_str}"

    def operate(self, tableset: Tableset) -> Tableset:
        """Apply the fillna operation."""
        df = tableset.get_df(self.model.table)
        target_columns = self.model.columns or df.columns.tolist()

        # Convert axis to pandas format
        pandas_axis = 0 if self.model.axis == "rows" else 1

        # Apply fillna based on method
        if self.model.method == "ffill":
            df[target_columns] = df[target_columns].ffill(limit=self.model.limit, axis=pandas_axis)
        elif self.model.method == "bfill":
            df[target_columns] = df[target_columns].bfill(limit=self.model.limit, axis=pandas_axis)
        elif self.model.method == "mean":
            for col in target_columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].mean())
                else:
                    # For non-numeric columns, use mode as fallback
                    mode_values = df[col].mode()
                    if not mode_values.empty:
                        df[col] = df[col].fillna(mode_values.iloc[0])
        elif self.model.method == "median":
            for col in target_columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    # For non-numeric columns, use mode as fallback
                    mode_values = df[col].mode()
                    if not mode_values.empty:
                        df[col] = df[col].fillna(mode_values.iloc[0])
        elif self.model.method == "mode":
            for col in target_columns:
                mode_values = df[col].mode()
                if not mode_values.empty:
                    df[col] = df[col].fillna(mode_values.iloc[0])
        elif self.model.method == "constant":
            # Try to convert value to appropriate type for each column
            for col in target_columns:
                if self.model.value == "":
                    continue

                # Try to convert value to the column's data type
                try:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        # For numeric columns, try to convert to float first, then int
                        try:
                            val = float(self.model.value)
                            if float(self.model.value).is_integer():
                                val = int(float(self.model.value))
                            df[col] = df[col].fillna(val)
                        except ValueError:
                            # If we can't convert the string to numeric, convert the column to string type
                            # This allows filling numeric columns with string values
                            # First convert to string, then replace 'nan' strings with the fill value
                            df[col] = df[col].astype(str)
                            df[col] = df[col].replace("nan", self.model.value)
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        # For datetime columns, try to parse the value
                        try:
                            val = pd.to_datetime(self.model.value)
                            df[col] = df[col].fillna(val)
                        except ValueError:
                            raise ValueError(
                                f"Cannot convert '{self.model.value}' to datetime for column '{col}'. "
                                f"Consider converting the column to string type first using the 'astype' operation."
                            )
                    else:
                        # For string/object columns, use as-is
                        df[col] = df[col].fillna(self.model.value)
                except Exception as e:
                    raise ValueError(f"Error filling column '{col}': {e}")

        tableset.set_df(self.model.table, df)
        return tableset
