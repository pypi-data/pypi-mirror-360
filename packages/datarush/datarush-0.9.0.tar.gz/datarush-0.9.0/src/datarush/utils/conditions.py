"""Utility functions for handling conditions in DataFrame."""

from datetime import date, datetime
from typing import Literal

import pandas as pd

from datarush.core.types import ConditionOperator, RowCondition
from datarush.utils.type_utils import convert_to_type


def match_conditions(
    df: pd.DataFrame, conditions: list[RowCondition], combine: Literal["and", "or"] = "and"
) -> pd.Series:
    """
    Match conditions against DataFrame and return a boolean mask.

    Args:
        df (pd.DataFrame): DataFrame to filter.
        conditions (list[Condition]): List of conditions to apply.
        combine (Literal["and", "or"]): How to combine conditions. Defaults to "and".
    Returns:
        pd.Series: Boolean mask indicating rows that match the conditions.
    """
    if not conditions:
        return pd.Series(True, index=df.index)

    def apply_condition(cond: RowCondition) -> pd.Series:
        series = df[cond.column]
        value = _parsed_value(cond)

        if cond.operator == ConditionOperator.EQ:
            mask = series == value
        elif cond.operator == ConditionOperator.LT:
            mask = series < value
        elif cond.operator == ConditionOperator.LTE:
            mask = series <= value
        elif cond.operator == ConditionOperator.GT:
            mask = series > value
        elif cond.operator == ConditionOperator.GTE:
            mask = series >= value
        elif cond.operator == ConditionOperator.REGEX:
            mask = series.astype(str).str.contains(value, na=False, regex=True)
        else:
            raise ValueError(f"Unsupported operator: {cond.operator}")

        return ~mask if cond.negate else mask

    masks = [apply_condition(cond) for cond in conditions]

    combined_mask = masks[0]
    for mask in masks[1:]:
        if combine == "and":
            combined_mask &= mask
        elif combine == "or":
            combined_mask |= mask
        else:
            raise ValueError(f"Unsupported combine logic: {combine}")

    return combined_mask


def _parsed_value(condition: RowCondition) -> str | int | float | date | datetime | bool:
    """Parse the value based on its type."""
    value_type = condition.value_type.get_type()
    return convert_to_type(condition.value, value_type)  # type: ignore
