"""Functions for executing DataRush templates."""

import argparse
import logging
from typing import Any

from datarush.config import DatarushConfig, set_datarush_config
from datarush.core.operations import register_operation_type
from datarush.core.templates import get_template_manager, template_to_dataflow
from datarush.core.types import ParameterSpec
from datarush.utils.logging import DataflowLogger, setup_logging
from datarush.utils.type_utils import convert_to_type

LOG = logging.getLogger(__name__)


def run_template(
    name: str,
    version: str,
    parameters: dict[str, Any] | None = None,
    config: DatarushConfig | None = None,
) -> None:
    """Run a template by its name and version.

    Args:
        name: Name of the template to run.
        version: Version of the template to run.
        parameters: Optional dictionary of parameter values to set for the template.
        config: Optional DatarushConfig to use. If not provided, the default configuration is loaded from environment variables.
    """
    # Setup logging if not already configured
    if not logging.getLogger().handlers:
        setup_logging(level="INFO")

    LOG.info(f"Starting template execution: {name} {version}")

    _setup(config)

    LOG.info(f"Loading template: {name} {version}")
    template = get_template_manager().read_template(name, version)
    LOG.debug("Template loaded successfully")

    dataflow = template_to_dataflow(template)

    if parameters:
        LOG.info(f"Setting {len(parameters)} parameter values")
        parameter_values = _parse_parameter_values_from_specs(
            parameter_specs=dataflow.parameters, parameter_values=parameters
        )
        dataflow.set_parameters_values(parameter_values)
        LOG.debug(f"Parameters set: {list(parameter_values.keys())}")

    with DataflowLogger(name, version, LOG):
        dataflow.run()


def run_template_from_command_line(config: DatarushConfig | None = None) -> None:
    """Run a template using command-line arguments.

    Args:
        config: Optional DatarushConfig to use. If not provided, the default configuration is loaded from environment variables.
    """
    # Setup logging if not already configured
    if not logging.getLogger().handlers:
        setup_logging(level="INFO")

    LOG.info("Starting DataRush template runner from command line")

    _setup(config)

    argparser = argparse.ArgumentParser(description="Datarush Template Runner")

    argparser.add_argument(
        "--template", type=str, required=True, help="Name of the template to run"
    )
    argparser.add_argument(
        "--version", type=str, required=True, help="Version of the template to run"
    )

    args, _ = argparser.parse_known_args()

    LOG.info(f"Loading template: {args.template} {args.version}")
    template = get_template_manager().read_template(args.template, args.version)
    dataflow = template_to_dataflow(template)

    for param in dataflow.parameters:
        argparser.add_argument(
            f"--{param.name}",
            type=str,
            default=param.default or None,
            help=param.description,
            required=param.required,
        )

    args = argparser.parse_args()

    LOG.info(f"Parsing {len(dataflow.parameters)} parameters from command line")
    parameter_values = _parse_parameter_values_from_specs(dataflow.parameters, vars(args))
    dataflow.set_parameters_values(parameter_values)
    LOG.debug(f"Parameters set: {list(parameter_values.keys())}")

    with DataflowLogger(args.template, args.version, LOG):
        dataflow.run()


def _parse_parameter_values_from_specs(
    parameter_specs: list[ParameterSpec], parameter_values: dict[str, str]
) -> dict[str, Any]:
    """Convert parameter values to their specified types."""
    LOG.debug(f"Parsing {len(parameter_specs)} parameter specifications")

    for spec in parameter_specs:
        if spec.name not in parameter_values and spec.required:
            LOG.error(f"Required parameter '{spec.name}' not found in provided values")
            raise ValueError(f"Parameter {spec.name} not found in the provided values")

    result = {}
    for spec in parameter_specs:
        value = parameter_values.get(spec.name, spec.default)
        converted_value = convert_to_type(value=value, to_type=spec.type.get_type())
        result[spec.name] = converted_value
        LOG.debug(f"Parameter '{spec.name}': {value} -> {type(converted_value).__name__}")

    return result


def _setup(config: DatarushConfig | None = None) -> None:
    """Initialize the Datarush configuration as contextvar and register operations."""
    LOG.info("Setting up DataRush configuration")

    config = config or DatarushConfig()
    LOG.debug("Configuration initialized")

    set_datarush_config(config)
    LOG.debug("Configuration set as context variable")

    if config.custom_operations:
        LOG.info(f"Registering {len(config.custom_operations)} custom operations")
        for operation in config.custom_operations:
            register_operation_type(operation)
            LOG.debug(f"Registered custom operation: {operation.name}")
    else:
        LOG.debug("No custom operations to register")
