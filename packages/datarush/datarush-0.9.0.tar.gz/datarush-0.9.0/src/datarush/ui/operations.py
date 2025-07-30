"""Operation page and components."""

from typing import cast

import streamlit as st

from datarush.core.operations import get_operation_type_by_title, list_operation_types
from datarush.exceptions import OperationError
from datarush.ui.form import operation_from_streamlit, update_operation_from_streamlit
from datarush.ui.state import get_dataflow
from datarush.utils.misc import crossed_out, truncate


def operations_page() -> None:
    """Render the operations page layout."""
    left_section, right_section = st.columns([2, 2])

    with left_section:
        show_tables()

    with right_section:
        show_operations()
        show_add_operation_ui()

        if st.button("Run Operations"):
            try:
                get_dataflow().run()
                st.rerun()
            except OperationError as e:
                st.error(e.summary())


def show_tables() -> None:
    """Display the currently loaded tables."""
    st.subheader("Tables")
    dataflow = get_dataflow()

    if not dataflow.current_tableset:
        st.write("No tables loaded, use operations to load tables")
        return

    selected_table_name = st.selectbox(
        "Select Table to Display",
        options=list(dataflow.current_tableset),
    )

    if selected_table_name:
        table = dataflow.current_tableset[selected_table_name]
        st.dataframe(table.df, height=800)


def show_operations() -> None:
    """Display and manage the list of operations."""
    st.subheader("Operations")
    dataflow = get_dataflow()

    for i, op in enumerate(dataflow.operations):
        # TODO: fix summary() for advanced mode
        op_summary = (
            truncate(op.summary(), max_len=200) if not op.advanced_mode else op.description
        )

        relevant_tableset = (
            dataflow.get_tableset_after_operation(i - 1) if i > 0 else dataflow.current_tableset
        ) or dataflow.current_tableset

        with st.expander(op_summary if op.is_enabled else crossed_out(op_summary), expanded=False):
            if update_operation_from_streamlit(op, tableset=relevant_tableset, key=i):
                st.rerun()

            cols = st.columns([8, 1, 1, 1, 1, 1])

            if cols[1].button(
                "",
                key=f"manmode_{i}",
                help=(
                    "Switch to UI input mode"
                    if op.advanced_mode
                    else "Switch to advanced input mode"
                ),
                icon=":material/view_list:" if op.advanced_mode else ":material/data_object:",
            ):
                op.advanced_mode = not op.advanced_mode
                st.rerun()

            if cols[2].button(
                "", key=f"up_{i}", help="Move up", icon=":material/arrow_upward:", disabled=i == 0
            ):
                dataflow.move_operation(i, i - 1)
                st.rerun()

            if cols[3].button(
                "",
                key=f"down_{i}",
                help="Move down",
                icon=":material/arrow_downward:",
                disabled=i == len(dataflow.operations) - 1,
            ):
                dataflow.move_operation(i, i + 1)
                st.rerun()

            if cols[4].button(
                "",
                key=f"toggle_{i}",
                help="Disable operation" if op.is_enabled else "Enable operation",
                icon=":material/toggle_on:" if op.is_enabled else ":material/toggle_off:",
            ):
                op.is_enabled = not op.is_enabled
                st.rerun()

            if cols[5].button("", key=f"remove_{i}", help="Remove", icon=":material/close:"):
                dataflow.remove_operation(i)
                st.rerun()


def show_add_operation_ui() -> None:
    """Provide UI for adding new operations."""
    dataflow = get_dataflow()
    with st.expander("Add New Operation", expanded=False):
        selected_op_title = cast(
            str,
            st.selectbox(
                "Choose an operation to add", [op_type.title for op_type in list_operation_types()]
            ),
        )
        if not selected_op_title:
            return

        operation_type = get_operation_type_by_title(selected_op_title)
        operation_future_index = len(dataflow.operations)

        new_operation = operation_from_streamlit(
            operation_type=operation_type,
            tableset=dataflow.current_tableset,
            key=operation_future_index,
        )

        if st.button("Add Operation"):
            if not new_operation:
                st.error("Fill in required operation params")
                return

            dataflow.add_operation(new_operation)
            st.rerun()
