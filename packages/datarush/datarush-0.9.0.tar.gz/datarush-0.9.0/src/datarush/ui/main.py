"""Main streamlit entrypoint."""

from typing import Callable

import streamlit as st

from datarush.config import DatarushConfig, set_datarush_config
from datarush.core.operations import register_operation_type
from datarush.ui import operations, parameters, raw_template, sidebar


def run_ui(config_factory: Callable[[], DatarushConfig] | None = None) -> None:
    """Run DataRush UI.

    Args:
        config_factory: Optional callable returning a DatarushConfig.
    """
    st.set_page_config(layout="wide")

    # Not initialized yet, set config and register operations
    if "datarush_config" not in st.session_state:
        config = config_factory() if config_factory is not None else DatarushConfig()
        st.session_state["datarush_config"] = config
        for operation in config.custom_operations:
            register_operation_type(operation)

    set_datarush_config(st.session_state["datarush_config"])

    pages = [
        st.Page(parameters.parameters_page, title="Parameters"),
        st.Page(operations.operations_page, title="Operations"),
        st.Page(raw_template.raw_template_page, title="Raw"),
    ]

    main_page = st.navigation(pages, position="hidden")
    sidebar.sidebar_section(pages)
    main_page.run()
