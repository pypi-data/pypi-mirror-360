"""Jinja2 utils."""

# flake8: noqa: D103

from typing import Any

from jinja2 import Template
from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from datarush.utils.type_utils import convert_to_type


def render_jinja2_template(template_str: str, context: dict) -> str:
    """Render a Jinja2 template with the given context.

    Args:
        template_str (str): The Jinja2 template string.
        context (dict): The context dictionary to render the template.

    Returns:
        str: The rendered template string.
    """
    template = Template(template_str)
    return template.render(context)


def model_validate_jinja2[T: BaseModel](
    model_type: type[T], model_dict: dict[str, str], context: dict[str, Any]
) -> T:
    """Validate a model using Jinja2 templates.

    Args:
        model_type (Type[_TModel]): The Pydantic model type to validate.
        model_dict (dict[str, Any]): The dictionary containing the model data where values can be Jinja2 templates.
        context (dict[str, Any]): The context for rendering Jinja2 templates.
    Returns:
        _TModel: The validated model instance.
    """
    rendered_dict = {}
    for name, field in model_type.model_fields.items():
        default = field.default if field.default is not PydanticUndefined else None
        template = model_dict.get(name, default)

        if not isinstance(template, str):
            rendered_dict[name] = template
            continue

        value = render_jinja2_template(template, context=context) if template else None
        if value is not None:
            rendered_dict[name] = convert_to_type(value, field.annotation)

    return model_type.model_validate(rendered_dict)
