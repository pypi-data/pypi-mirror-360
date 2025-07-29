"""
This module contains the CLIParser class, responsible for handling all
command-line argument parsing and configuration file loading for the bib-ami tool.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any


class CLIParser:
    """
    Parses command-line arguments and configuration for bib-ami.

    This class uses argparse to define the application's command-line interface
    and includes logic to load default settings from a JSON configuration file.
    It ensures that all required settings are present and valid before returning
    a unified configuration object to the main application manager.
    """

    def __init__(self):
        """Initializes the ArgumentParser with a description and default formatter."""
        self.parser = argparse.ArgumentParser(
            description="Clean, merge, and enrich BibTeX files.",
            # This formatter automatically adds default values to help text.
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        self._add_arguments()

    def _add_arguments(self):
        """Defines all command-line arguments for the application."""
        self.parser.add_argument(
            "--input-dir",
            required=True,
            type=Path,
            help="Directory containing input .bib files.",
        )
        self.parser.add_argument(
            "--output-file",
            required=True,
            type=Path,
            help="Path for the main output file of verified/accepted entries.",
        )
        self.parser.add_argument(
            "--suspect-file",
            type=Path,
            help="Path for the output file of suspect entries. Required if using --filter-validated.",
        )
        self.parser.add_argument(
            "--config-file",
            type=Path,
            default="bib_ami_config.json",
            help="Path to a JSON configuration file.",
        )
        self.parser.add_argument(
            "--email",
            type=str,
            help="Email for CrossRef API Polite Pool. Overrides config file.",
        )
        self.parser.add_argument(
            "--merge-only",
            action="store_true",
            help="If set, only merge files without further processing.",
        )
        self.parser.add_argument(
            "--filter-validated",
            action="store_true",
            help="If set, only save fully validated entries to the main output file.",
        )

    def get_settings(self) -> argparse.Namespace:
        """
        Parses args, loads config, and returns a unified settings object.

        This method orchestrates the configuration loading process. It first
        parses the command-line arguments, then loads settings from a JSON
        config file, and finally merges them, with command-line arguments
        taking precedence. It also performs final validation checks.

        Returns:
            An argparse.Namespace object containing all settings for the run.
        """
        args = self.parser.parse_args()
        config = self._load_config(args.config_file)

        # Combine args and config, with command-line args taking precedence.
        settings = vars(args)
        for key, value in config.items():
            if settings.get(key) is None:
                settings[key] = value

        # Final validation to ensure the application can run correctly.
        if not settings.get("email"):
            self.parser.error(
                "An email address is required. Provide it via --email or in the config file."
            )

        if settings.get("filter_validated") and not settings.get(
            "suspect_file"
        ):
            self.parser.error(
                "--suspect-file is required when using --filter-validated."
            )

        return argparse.Namespace(**settings)

    @staticmethod
    def _load_config(config_path: Path) -> Dict[str, Any]:
        """
        Loads settings from a JSON config file if it exists.

        Args:
            config_path: The path to the JSON configuration file.

        Returns:
            A dictionary of settings from the file, or an empty dictionary
            if the file does not exist or cannot be parsed.
        """
        if config_path and config_path.exists():
            logging.info(f"Loading configuration from '{config_path}'")
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(
                    f"Could not read or parse config file '{config_path}': {e}"
                )
        return {}
