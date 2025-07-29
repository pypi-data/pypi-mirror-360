import json
import logging
import os
import sys
import tomllib
from pathlib import Path
from typing import Callable

import yaml

from exosphere import app_config, cli, context
from exosphere.config import Configuration
from exosphere.inventory import Inventory

logger = logging.getLogger(__name__)

# List of configuration file paths to check, in order of precedence
# The search stops at first match, so ordering matters.
# TODO: SETTLE ON A STANDARD CONFIG PATH + ~/.exosphere.xyz
CONFPATHS: list[Path] = [
    Path.home() / ".config" / "exosphere" / "config.yaml",
    Path.home() / ".config" / "exosphere" / "config.yml",
    Path.home() / ".config" / "exosphere" / "config.toml",
    Path.home() / ".config" / "exosphere" / "config.json",
    Path.cwd() / "config.yaml",
    Path.cwd() / "config.yml",
    Path.cwd() / "config.toml",
    Path.cwd() / "config.json",
]

LOADERS: dict[str, Callable] = {
    "yaml": yaml.safe_load,
    "yml": yaml.safe_load,
    "toml": tomllib.load,
    "json": json.load,
}


def setup_logging(log_level: str, log_file: str | None = None) -> None:
    """
    Set up logging configuration.
    This function initializes the logging system with a specified log level
    and optional log file. If no log file is specified, logs will be printed
    to the console. This is useful for debugging and running in the REPL.

    :param log_file: Optional log file path to write logs to.
    :param log_level: The logging level to set.
    """
    handler: logging.Handler

    if log_file:
        handler = logging.FileHandler(log_file, encoding="utf-8")
    else:
        handler = logging.StreamHandler()
        handler.setLevel(log_level)

    logging.basicConfig(
        level=logging.WARN,  # Default to WARN for root logger, avoid library noise
        handlers=[handler],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logging.getLogger("exosphere").setLevel(log_level)
    logging.getLogger(__name__).info("Logging initialized with level: %s", log_level)


def load_first_config(config: Configuration) -> bool:
    """
    Load the first configuration file found in either:

    - Environment variable EXOSPHERE_CONFIG_FILE (if set)
    - The list of predefined paths (CONFPATHS).

    Those two are mutually exclusive, meaning if the environment variable
    is set, it will be used instead of the predefined paths.

    Brutally exits with non-zero status in case of issues beyond
    ENOENT and EISDIR.

    :param config: The configuration object to populate.

    :return: True if a configuration file was loaded, False otherwise.
    """

    env_config_file = os.environ.get("EXOSPHERE_CONFIG_FILE")
    env_config_path = os.environ.get("EXOSPHERE_CONFIG_PATH")

    if env_config_file:
        logger.info(
            "Using configuration file from environment variable: %s", env_config_file
        )
        paths = [Path(env_config_file)]
    elif env_config_path:
        logger.info(
            "Using configuration path from environment variable: %s", env_config_path
        )
        paths = [
            # FIXME: Refactor this shit and CONFPATHS
            Path(env_config_path) / "config.yaml",
            Path(env_config_path) / "config.yml",
            Path(env_config_path) / "config.toml",
            Path(env_config_path) / "config.json",
        ]
    else:
        logger.debug("Using default configuration paths")
        paths = CONFPATHS

    for confpath in paths:
        logger.debug("Trying config file at %s", confpath)
        if not confpath.exists():
            continue

        logger.debug("Loading config file from %s", confpath)
        ext = confpath.suffix[1:].lower()
        loader = LOADERS.get(ext)

        if not loader:
            logger.error("No working loaders for extension: %s, skipping.", ext)
            continue

        try:
            if config.from_file(filepath=str(confpath), loader=loader, silent=True):
                context.confpath = str(confpath)
                logger.info("Loaded config file from %s", confpath)
                return True
            else:
                logger.warning("Failed to load config file from %s", confpath)
        except Exception as e:
            # Abort brutally in case of non-standard load failure
            # Exception will contain the actual error message
            logger.error("Startup error: %s", e)
            sys.exit(1)

    return False


def main() -> None:
    """
    Program Entry Point
    """
    # Load the first configuration file found
    if not load_first_config(app_config):
        logger.warning("No configuration file found. Using defaults.")

    logger.info("Configuration loaded from: %s", context.confpath)

    # Override configuration options with environment variables, if any
    app_config.from_env()

    # initialize logging and setup handlers depending on config
    log_file: str | None = app_config["options"].get("log_file")
    debug_mode: bool = app_config["options"].get("debug")

    if debug_mode:
        logger.warning("Debug mode enabled! Logs may flood console!")
        setup_logging(app_config["options"]["log_level"])
    else:
        setup_logging(app_config["options"]["log_level"], log_file)

    # Initialize the inventory
    try:
        context.inventory = Inventory(app_config)
    except Exception as e:
        logger.error("Startup Error loading inventory: %s", e)
        sys.exit(1)

    # Launch CLI application
    cli.app()


if __name__ == "__main__":
    main()
