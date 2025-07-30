"""Page for saving the dataflow as a JSON template."""

import json

import streamlit as st
from streamlit_ace import st_ace

from datarush.core.templates import dataflow_to_template, template_to_dataflow
from datarush.ui.state import get_dataflow, set_dataflow


def raw_template_page() -> None:
    """Render the save page with template JSON viewer."""
    st.subheader("Template JSON")

    dataflow_ui = get_dataflow()
    template = dataflow_to_template(dataflow_ui)

    raw_template_str = st_ace(
        json.dumps(template, indent=4),
        language="json",
        theme="twilight",
    )

    new_template = json.loads(raw_template_str)

    if new_template != template:
        dataflow = template_to_dataflow(new_template)
        set_dataflow(dataflow)
        st.info("The template has been modified.")
