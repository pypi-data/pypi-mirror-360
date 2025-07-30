#!/usr/bin/env python3
"""Main entry point for the prompt-to-bot service."""

import logging
import sys
from typing import Optional

import rasa.core.utils
from rasa.builder.logging_utils import collecting_logs_processor
from rasa.builder.service import PromptToBotService
from rasa.utils.common import configure_logging_and_warnings
from rasa.utils.log_utils import configure_structlog
from rasa.utils.sanic_error_handler import register_custom_sanic_error_handler


def setup_logging():
    """Setup logging configuration."""
    log_level = logging.DEBUG

    configure_logging_and_warnings(
        log_level=log_level,
        logging_config_file=None,
        warn_only_once=True,
        filter_repeated_logs=True,
    )

    configure_structlog(
        log_level,
        include_time=True,
        additional_processors=[collecting_logs_processor],
    )


def main(project_folder: Optional[str] = None):
    """Main entry point."""
    try:
        # Setup logging
        setup_logging()

        # Create and configure service

        service = PromptToBotService(project_folder)
        register_custom_sanic_error_handler(service.app)

        # Log available routes
        rasa.core.utils.list_routes(service.app)

        # Run the service
        service.run()

    except KeyboardInterrupt:
        print("\nService stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Failed to start service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    project_folder = sys.argv[1] if len(sys.argv) > 1 else None
    main(project_folder)
