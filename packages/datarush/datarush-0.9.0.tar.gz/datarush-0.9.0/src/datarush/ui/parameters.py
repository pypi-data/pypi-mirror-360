"""Parameters page and components."""

import json

import streamlit as st
from pydantic import ValidationError
from streamlit_ace import st_ace

from datarush.core.types import ParameterSpec
from datarush.ui.form import model_from_streamlit
from datarush.ui.state import get_dataflow


def parameters_page() -> None:
    """Render the parameters page layout."""
    st.subheader("Parameters")
    show_parameters()
    show_add_parameter_ui()

    st.markdown("---")

    st.write("##### Mock input parameters")
    show_context_mocker()

    # default_json = {"some_key": "some value"}
    # jinja2_input = "{{ some_key }}"

    # st.markdown("##### Jinja2 playground")
    # left, right = st.columns(2)
    # with left:
    #     st.write("Template")
    #     jinja2_input = st_ace(
    #         jinja2_input,
    #         placeholder="Jinja2 template",
    #         language="django",
    #         theme="twilight",
    #         keybinding="vscode",
    #         auto_update=True,
    #     )
    # with right:
    #     st.write("Result")
    #     try:
    #         rendered_template = render_jinja2_template(jinja2_input, parameters)
    #         st.code(rendered_template)
    #     except jinja2.exceptions.TemplateSyntaxError:
    #         st.error("Invalid Jinja2 template syntax")


def show_parameters() -> None:
    """Display and manage the list of parameters."""
    dataflow = get_dataflow()

    to_remove = []
    for i, param in enumerate(dataflow.parameters):
        with st.expander(f"`{param.name}`  -  {param.description}", expanded=False):
            new_param = model_from_streamlit(
                ParameterSpec, key=f"parameter_{i}", current_model=param
            )
            if new_param != param:
                dataflow._parameters[i] = new_param
                st.rerun()

            cols = st.columns([10, 1])

            if cols[-1].button("Delete", key=f"delete_parameter_{i}"):
                to_remove.append(i)

    for index in reversed(to_remove):
        dataflow.remove_parameter(index)
        st.rerun()


def show_add_parameter_ui() -> None:
    """Provide UI for adding new parameters."""
    dataflow = get_dataflow()
    with st.expander("Add New Parameter", expanded=False):
        try:
            parameter_future_index = len(dataflow.parameters)
            param = model_from_streamlit(
                ParameterSpec,
                key=f"parameter_{parameter_future_index}",
            )
        except ValidationError:
            param = None

        if st.button("Add"):
            if not param:
                st.error("Fill in the new parameter form")
                return

            dataflow.add_parameter(param)
            st.rerun()


def show_context_mocker() -> None:
    """Provide mock input parameter editor."""
    dataflow = get_dataflow()

    if "context_params_mock" not in st.session_state:
        st.session_state.context_params_mock = {}

    current_mock_params = st.session_state.context_params_mock
    mock_params = {
        param.name: current_mock_params.get(param.name, param.default or "mock value")
        for param in dataflow.parameters
    }

    edited_mock_params_str = st_ace(
        json.dumps(mock_params, indent=4),
        language="json",
        theme="twilight",
        keybinding="vscode",
        min_lines=5,
        auto_update=False,
    )

    try:
        edited_mock_params = json.loads(edited_mock_params_str)
        if edited_mock_params != current_mock_params:
            for name, value in edited_mock_params.items():
                dataflow.set_parameter_value(name, value)

            st.session_state.context_params_mock = edited_mock_params

    except json.decoder.JSONDecodeError:
        st.error("Invalid JSON input")
