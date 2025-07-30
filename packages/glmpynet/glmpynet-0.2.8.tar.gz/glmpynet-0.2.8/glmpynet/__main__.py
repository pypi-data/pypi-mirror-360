"""
Main entry point for the glmpynet command-line tool.

This script is executed when the `glmpynet` command is run from the terminal.
Its primary responsibilities are:
1.  Setting up basic logging for the application.
2.  Parsing command-line arguments and configuration settings using the CLIParser.
3.  Initializing the main BibTexManager with the final settings.
4.  Executing the bibliography processing workflow.
5.  Catching and logging any critical, unhandled exceptions that occur during the process.
"""

import logging
from .cli import CLIParser
from .bibtex_manager import BibTexManager


def main():
    """
    Initializes and runs the glmpynet application workflow.

    This function orchestrates the entire process by parsing arguments,
    instantiating the manager, running the workflow, and handling top-level
    exceptions.
    """
    # Configure the root logger for the application.
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Parse command-line arguments and load any configuration files.
    parser = CLIParser()
    settings = parser.get_settings()

    try:
        # Instantiate the main manager with the user-provided settings.
        manager = BibTexManager(settings=settings)
        # Execute the full bibliography processing pipeline.
        manager.process_bibliography()
    except Exception as e:
        # A top-level catch-all to ensure that any unexpected critical error
        # during the workflow is logged to the console instead of crashing silently.
        logging.error(
            f"A critical error occurred during the workflow: {e}",
            exc_info=True,  # Set to True to include the full traceback in the log.
        )


if __name__ == "__main__":
    # This allows the script to be run directly, e.g., `python -m bib_ami.__main__`.
    # The `entry_points` in setup.py makes this the target for the `glmpynet` command.
    main()
