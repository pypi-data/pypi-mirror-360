"""Form rendering functions."""

# flake8: noqa: D103
from __future__ import annotations

import json
from typing import Any, Literal, Type, cast, get_args

import jinja2
import pandas as pd
import streamlit as st
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined
from streamlit_ace import st_ace

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import (
    ColumnStr,
    ColumnStrMeta,
    ContentType,
    PartitionFilter,
    PartitionFilterGroup,
    RowConditionGroup,
    StringMap,
    TableStr,
    TextStr,
    ValueType,
)
from datarush.ui.state import get_dataflow
from datarush.utils.conditions import ConditionOperator, RowCondition
from datarush.utils.jinja2 import render_jinja2_template
from datarush.utils.type_utils import convert_to_type, is_literal, is_string_enum, types_are_equal


def operation_from_streamlit[T: Operation](
    operation_type: Type[T], tableset: Tableset | None = None, key: int | str | None = None
) -> T | None:
    """Render a streamlit form for a given operation type and return the operation instance."""
    try:
        model_dict = model_dict_from_streamlit(
            operation_type.schema(),
            tableset=tableset,
            key=key,
        )
        return operation_type(model_dict)
    except ValidationError as e:
        return None


def update_operation_from_streamlit(
    operation: Operation, tableset: Tableset | None = None, key: int | str | None = None
) -> bool:
    """Update the operation instance from a streamlit form."""
    model_dict = model_dict_from_streamlit(
        operation.schema(),
        tableset=tableset,
        key=key,
        current_model_dict=operation.model_dict,
        advanced_mode=operation.advanced_mode,
    )
    if operation.model_dict == model_dict:
        return False

    if st.button("Update", f"operation_update_button_{key}"):
        operation._model_dict = model_dict
        return True

    return False


def model_from_streamlit[T: BaseModel](
    schema: Type[T],
    tableset: Tableset | None = None,
    key: str | int | None = None,
    current_model: T | None = None,
) -> T:
    """Render a streamlit form based on a Pydantic model and return the model instance.

    Args:
        schema : The Pydantic model class.
        tableset: Optional tableset for table-related fields.
        key: Optional key for Streamlit widgets.
        current_model_dict: Optional current model dictionary to pre-fill values.
    Returns:
        T: The Pydantic model instance with the values from the Streamlit widgets.
    """
    model_dict = model_dict_from_streamlit(
        schema=schema,
        tableset=tableset,
        key=key,
        current_model_dict=current_model.model_dump() if current_model else None,
        advanced_mode=False,
    )
    return schema.model_validate(model_dict)


def model_dict_from_streamlit[T: BaseModel](
    schema: Type[T],
    tableset: Tableset | None = None,
    key: str | int | None = None,
    current_model_dict: dict[str, Any] | None = None,
    advanced_mode: bool = False,
) -> dict[str, Any]:
    """
    Render a streamlit form based on a Pydantic model and return the values as a dictionary.

    Args:
        schema : The Pydantic model class.
        tableset: Optional tableset for table-related fields.
        key: Optional key for Streamlit widgets.
        current_model_dict: Optional current model dictionary to pre-fill values.
        advanced_mode: Flag to enable advanced mode with Jinja2 template rendering.
    Returns:
        dict[str, Any]: The dictionary containing the values from the Streamlit widgets.
    """
    model_dict: dict[str, Any] = {}

    for name, field in schema.model_fields.items():
        kwargs: dict[str, Any] = {
            "label": field.title or name,
            "key": f"{schema.__name__}_{advanced_mode}_{name}_{key or ''}",
            "help": field.description,
        }
        default = field.default if field.default is not PydanticUndefined else None
        current_value = current_model_dict.get(name, None) if current_model_dict else None

        ################################
        ######### ADVANCED MODE ########
        ################################
        if advanced_mode:
            # Display the editor for jinja2 template
            st.write(f"{kwargs['label']} template")
            value = st_ace(
                (
                    str(current_value)
                    if not isinstance(current_value, dict)
                    else json.dumps(current_value)
                ),
                language="django",
                theme="twilight",
                keybinding="vscode",
                # height=70,
                min_lines=3,
                # max_lines=1,
                show_gutter=False,
                auto_update=False,
                key=kwargs["key"] + "_ace",
            )

            # Try to render the template and display the result
            try:
                dataflow_context = get_dataflow().get_current_context()
                rendered_value = render_jinja2_template(value, context=dataflow_context)
                # validate by trying to convert
                convert_to_type(rendered_value, to_type=field.annotation)
                # Display the rendered value
                st.write(f"{kwargs['label']} value")
                st.code(rendered_value)
                st.write("___")
            except jinja2.exceptions.TemplateSyntaxError as e:
                st.error(f"Error rendering template: {e}")
            except ValueError as e:
                st.error(f"Error converting value: {e} to type {field.annotation}")

        ################################
        ############ UI MODE ###########
        ################################
        elif field.annotation is TableStr:
            if tableset:
                options = list(tableset)
                index = options.index(current_value) if current_value is not None else 0
                value = st.selectbox(options=options, index=index, **kwargs)
            else:
                value = st.selectbox(
                    options=[current_value] if current_value is not None else [], **kwargs
                )

        elif types_are_equal(field.annotation, list[TableStr]):
            if tableset:
                options = list(tableset)
                value = st.multiselect(options=options, default=current_value or None, **kwargs)
            else:
                value = st.multiselect(
                    options=current_value or [], default=current_value, **kwargs
                )

        elif field.annotation is ColumnStr or types_are_equal(field.annotation, list[ColumnStr]):
            if tableset:
                relevant_columns = _get_relevant_columns(
                    tableset=tableset,
                    column_meta=ColumnStrMeta.from_pydantic_field(field),
                    model_dict=model_dict,
                )

                if field.annotation is ColumnStr:
                    if (
                        current_value is not None and current_value not in relevant_columns
                    ):  #  if header changes
                        relevant_columns = [current_value] + relevant_columns
                    index = (
                        relevant_columns.index(current_value) if current_value is not None else 0
                    )
                    value = st.selectbox(options=relevant_columns, index=index, **kwargs)
                else:
                    value = st.multiselect(
                        options=relevant_columns, default=current_value, **kwargs
                    )
            else:
                if field.annotation is ColumnStr:
                    value = st.selectbox(
                        options=[current_value] if current_value is not None else [], **kwargs
                    )
                else:
                    value = st.multiselect(
                        options=current_value or [], default=current_value, **kwargs
                    )
        elif types_are_equal(field.annotation, list[str]):
            value = st.multiselect(
                options=current_value or [],
                default=current_value,
                accept_new_options=True,
                **kwargs,
            )
        elif is_literal(field.annotation):
            options = list(get_args(field.annotation))
            value = st.selectbox(options=options, **kwargs)

        elif is_string_enum(field.annotation):
            value = st.selectbox(options=list(field.annotation), **kwargs)  # type: ignore

        elif field.annotation is bytes:
            content_type: ContentType | None = model_dict.get("content_type")
            extension = content_type.extension() if content_type else None
            file = st.file_uploader("Choose File", type=extension, key=f"local_file_file_df_{key}")
            value = file.getvalue() if file else None

        elif field.annotation is bool:
            value = st.checkbox(
                value=cast(bool, current_value if current_value is not None else default), **kwargs
            )

        elif issubclass(field.annotation, str):  # type: ignore
            value = st.text_input(
                value=current_value if current_value is not None else (default or ""), **kwargs
            )

        elif field.annotation is int:
            value = st.number_input(
                value=current_value if current_value is not None else default, step=1, **kwargs
            )

        elif field.annotation is float:
            value = st.number_input(
                value=current_value if current_value is not None else default, step=0.01, **kwargs
            )

        elif field.annotation is RowCondition:
            relevant_columns = _get_relevant_columns(
                tableset=tableset,
                column_meta=ColumnStrMeta.from_pydantic_field(field),
                model_dict=model_dict,
            )
            value = _condition_dict_from_streamlit(
                column_options=relevant_columns,
                current_dict=current_value,
                key=kwargs["key"] + "single_condition",
                advanced_mode=advanced_mode,
            )

        elif field.annotation is RowConditionGroup:
            relevant_columns = _get_relevant_columns(
                tableset=tableset,
                column_meta=ColumnStrMeta.from_pydantic_field(field),
                model_dict=model_dict,
            )
            value = _condition_group_dict_from_streamlit(
                column_options=relevant_columns,
                current_dict=current_value,
                key=kwargs["key"] + "_condition_group",
                advanced_mode=advanced_mode,
            )
        elif field.annotation is PartitionFilterGroup:
            value = _partition_filter_group_dict_from_streamlit(
                current_dict=current_value,
                key=kwargs["key"] + "_partition_filter_group",
            )
        elif field.annotation is TextStr:
            value = st.text_area(
                value=current_value if current_value is not None else (default or ""), **kwargs
            )
        elif field.annotation is StringMap:
            st.markdown(
                f"<div style='font-size:14px; font-weight:400; margin-bottom:6px'>{kwargs['label']}</div>",
                unsafe_allow_html=True,
            )
            value_df = st.data_editor(
                pd.DataFrame(
                    data=[(k, v) for k, v in current_value.items()] if current_value else None,
                    columns=["key", "value"],
                ),
                num_rows="dynamic",
                key=kwargs["key"],
                use_container_width=True,
                hide_index=True,
                column_order=("key", "value"),
                column_config={
                    "key": st.column_config.TextColumn("Key", max_chars=100),
                    "value": st.column_config.TextColumn("Value", max_chars=1000),
                },
            )
            value = dict(zip(value_df["key"], value_df["value"]))
        else:
            raise TypeError(
                f"Not supported BaseOperationModel type {field.annotation} for field {name}"
            )

        if value is not None:
            model_dict[name] = value

    # values in advanced mode are jinja2 templates strings, no point in validating them
    if not advanced_mode:
        schema.model_validate(model_dict)

    return model_dict


def _get_relevant_columns(
    tableset: Tableset | None = None,
    column_meta: ColumnStrMeta | None = None,
    model_dict: dict[str, Any] | None = None,
) -> list[str]:
    """Get relevant columns from the tableset based on the column metadata."""
    if not tableset:
        return []

    relevant_tables = []
    column_meta = column_meta or ColumnStrMeta()
    model_dict = model_dict or {}

    table = model_dict.get(column_meta.table_field)
    if table:
        relevant_tables.append(table)

    tables = model_dict.get(column_meta.tables_field, []) + [
        model_dict.get(table_field) for table_field in column_meta.table_fields or []
    ]
    if tables:
        relevant_tables.extend(tables)

    relevant_columns = sorted(
        {col for name in relevant_tables for col in tableset.get_df(name).columns},
        key=lambda x: str(x),
    )

    return relevant_columns


def _condition_dict_from_streamlit(
    column_options: list[str],
    current_dict: dict[str, Any] | None = None,
    key: int | str | None = None,
    advanced_mode: bool = False,
    show_remove_button: bool = False,
) -> dict | Literal[False] | None:
    """Render a condition form in Streamlit and return the condition dictionary.

    Returns:
        dict | Literal[False] | None: The condition dictionary if valid, False if removed, or None if invalid.
    """
    current_dict = current_dict or {}
    curr_column = current_dict.get("column")
    curr_operator = current_dict.get("operator")
    curr_value = current_dict.get("value")
    curr_value_type = current_dict.get("value_type")
    curr_negate = current_dict.get("negate", False)

    with st.container(border=True, key=key):
        st.write("Condition")

        # Layout
        col_area, operator_area = st.columns([2, 1])
        value_area, value_type_area = st.columns([2, 1])
        negate_area, remove_area = st.columns([8, 1])

        # Column
        column_options = column_options or [curr_column] if curr_column else []
        column = col_area.selectbox(
            "Column",
            options=column_options,
            key=f"{key}_column_select",
            index=column_options.index(curr_column) if curr_column else 0,
        )

        # Operator
        operator_options = list(ConditionOperator)
        operator = ConditionOperator(
            operator_area.selectbox(
                "Operator",
                options=operator_options,
                key=f"{key}_operator",
                index=operator_options.index(curr_operator) if curr_operator else 0,
            )
        )

        # Value
        value = value_area.text_input("Value", key=f"{key}_value", value=curr_value)

        # Value Type
        type_options = list(ValueType)
        value_type = ValueType(
            value_type_area.selectbox(
                "Type",
                options=type_options,
                key=f"{key}_value_type",
                index=type_options.index(curr_value_type) if curr_value_type else 0,
            )
        )

        # Negate
        negate = negate_area.checkbox("Negate", key=f"{key}_negate", value=curr_negate)

        # Remove button
        if show_remove_button:
            if remove_area.button(
                "", key=f"{key}_remove_condition", help="Remove", icon=":material/close:"
            ):
                return False

        try:
            res = RowCondition(
                column=column,
                operator=operator,
                value=value,  # type: ignore
                value_type=value_type,
                negate=negate,
            ).model_dump()
            return res
        except ValidationError as e:
            return None


def _condition_group_dict_from_streamlit(
    column_options: list[str],
    current_dict: dict[str, Any] | None = None,
    key: int | str | None = None,
    advanced_mode: bool = False,
) -> dict | None:
    """Render a condition group form in Streamlit and return the condition group dictionary.

    This currently utilizes st.session_state to store conditions state
    which has a few problems and should be refactored in the future.
    """
    current_dict = current_dict or {}

    if f"{key}_conditions" not in st.session_state:
        st.session_state[f"{key}_conditions"] = current_dict.get("conditions", [])

    current_combine = current_dict.get("combine", "and")
    conditions = st.session_state[f"{key}_conditions"]

    with st.container(border=True, key=f"{key}_container_conditions"):
        st.write("Conditions")
        combine: Literal["and", "or"] = st.selectbox(
            "Combine",
            options=["and", "or"],
            index=1 if current_combine == "or" else 0,
            key=f"{key}_combine",
        )

        updated_conditions = []
        for i, current_condition in enumerate(conditions):
            with st.container(key=f"{key}_condition_{i}_container"):
                condition = _condition_dict_from_streamlit(
                    column_options=column_options,
                    current_dict=current_condition,
                    key=f"{key}_condition_{i}",
                    advanced_mode=advanced_mode,
                    show_remove_button=True,
                )
                if condition:
                    updated_conditions.append(condition)

                if condition is False:
                    st.session_state[f"{key}_conditions"].pop(i)
                    st.rerun()

        # Update session state with modified conditions
        st.session_state[f"{key}_conditions"] = updated_conditions

        if st.button("Add Condition", key=f"{key}_add_condition"):
            # Add a new condition to the session state
            new_condition = RowCondition(
                column=column_options[0] if column_options else "",
                operator=ConditionOperator.EQ,
                value="",
                value_type=ValueType.STRING,
                negate=False,
            ).model_dump()
            st.session_state[f"{key}_conditions"].append(new_condition)
            st.rerun()

    try:
        res = RowConditionGroup(
            combine=combine,
            conditions=st.session_state[f"{key}_conditions"],
        ).model_dump()
        return res
    except ValidationError as e:
        return None


# PARTITIONS FILTERS


def _partition_filter_group_dict_from_streamlit(
    current_dict: dict[str, Any] | None = None,
    key: int | str | None = None,
) -> dict | None:
    """Render a partition filter group form in Streamlit and return the condition group dictionary.

    This currently utilizes st.session_state to store conditions state
    which has a few problems and should be refactored in the future.
    """
    current_dict = current_dict or {}

    if f"{key}_pt_filters" not in st.session_state:
        st.session_state[f"{key}_pt_filters"] = current_dict.get("filters", [])

    current_combine = current_dict.get("combine", "and")
    filters = st.session_state[f"{key}_pt_filters"]

    with st.container(border=True, key=f"{key}_container_pt_filters"):
        st.write("Partition Filters")
        combine: Literal["and", "or"] = st.selectbox(
            "Combine",
            options=["and", "or"],
            index=1 if current_combine == "or" else 0,
            key=f"{key}_combine",
        )

        updated_filters = []
        for i, current_filter in enumerate(filters):
            with st.container(key=f"{key}_condition_{i}_container"):
                partition_filter = _partition_filter_dict_from_streamlit(
                    current_dict=current_filter,
                    key=f"{key}_condition_{i}",
                )
                if partition_filter:
                    updated_filters.append(partition_filter)

                if partition_filter is False:
                    st.session_state[f"{key}_pt_filters"].pop(i)
                    st.rerun()

        # Update session state with modified conditions
        st.session_state[f"{key}_pt_filters"] = updated_filters

        if st.button("Add Filter", key=f"{key}_add_pt_filter"):
            # Add a new condition to the session state
            new_condition = PartitionFilter(
                column="",
                operator=ConditionOperator.EQ,
                value="",
                negate=False,
            ).model_dump()
            st.session_state[f"{key}_pt_filters"].append(new_condition)
            st.rerun()

    try:
        res = PartitionFilterGroup(
            combine=combine,
            filters=st.session_state[f"{key}_pt_filters"],
        ).model_dump()
        return res
    except ValidationError as e:
        return None


def _partition_filter_dict_from_streamlit(
    current_dict: dict[str, Any] | None = None,
    key: int | str | None = None,
) -> dict | Literal[False] | None:
    """Render a partition filter form in Streamlit and return the filter dictionary.

    Returns:
        dict | Literal[False] | None: The filter dictionary if valid, False if removed, or None if invalid.
    """
    current_dict = current_dict or {}
    curr_column = current_dict.get("column")
    curr_operator = current_dict.get("operator")
    curr_value = current_dict.get("value")
    curr_negate = current_dict.get("negate", False)

    with st.container(border=True, key=key):
        st.write("Condition")

        # Layout
        (
            col_area,
            operator_area,
            value_area,
        ) = st.columns([2, 2, 2])
        negate_area, remove_area = st.columns([8, 1])

        # Column
        column = col_area.text_input(
            "Column",
            value=curr_column if curr_column else "",
            key=f"{key}_column_input",
        )

        # Operator
        operator_options = list(ConditionOperator)
        operator = ConditionOperator(
            operator_area.selectbox(
                "Operator",
                options=operator_options,
                key=f"{key}_operator",
                index=operator_options.index(curr_operator) if curr_operator else 0,
            )
        )

        # Value
        value = value_area.text_input("Value", key=f"{key}_value", value=curr_value)

        # Negate
        negate = negate_area.checkbox("Negate", key=f"{key}_negate", value=curr_negate)

        # Remove button
        if remove_area.button(
            "", key=f"{key}_remove_pt_filter", help="Remove", icon=":material/close:"
        ):
            return False

        try:
            res = PartitionFilter(
                column=column,
                operator=operator,
                value=value,  # type: ignore
                negate=negate,
            ).model_dump()
            return res
        except ValidationError as e:
            return None
