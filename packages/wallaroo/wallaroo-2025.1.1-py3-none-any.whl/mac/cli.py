"""This module features the CLI for serving a custom PythonStep."""

import logging
from pathlib import Path

import typer
from pydata_util.nats import (
    parse_nats_message_from_model_json,
)
from pydata_util.types import (
    SupportedNATSMessages,
)

from mac.entrypoints.serving import serve_custom_step_from_nats_message
from mac.types import SupportedServices

app = typer.Typer()


logger = logging.getLogger(__name__)


@app.command()
def serve(
    config_path: Path = typer.Option(..., "--config-path", exists=True),
    service: SupportedServices = SupportedServices.FLIGHT,
    host: str = "0.0.0.0",
    port: int = 8080,
):
    """Serve a custom PythonStep with a specified service.

    :param config_path: Path to the JSON config file.
    :param service: Service to use for serving the PythonStep.
    :param host: Host to serve the PythonStep on.
    :param port: Port to serve the PythonStep on.
    """
    nats_message = parse_nats_message_from_model_json(
        file_path=config_path,
        message_type=SupportedNATSMessages.PACKAGING,
    )
    logger.debug(f"Parsed NATS message: {nats_message}")
    serve_custom_step_from_nats_message(
        nats_message=nats_message, service_type=service, host=host, port=port
    )


@app.command()
def compile_qaic(
    config_path: Path = typer.Option(..., "--config-path", exists=True),
) -> None:
    """Export and compile model to qaic.

    :param config_path: Path to the JSON config file.
    """
    from mac.qaic_utils import load_and_compile

    nats_message = parse_nats_message_from_model_json(
        file_path=config_path,
        message_type=SupportedNATSMessages.PACKAGING,
    )
    logger.debug(f"Parsed NATS message: {nats_message}")

    load_and_compile(nats_message)
