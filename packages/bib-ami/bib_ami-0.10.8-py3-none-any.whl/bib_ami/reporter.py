"""
This module contains the SummaryReporter class, which is responsible for
tracking and reporting metrics about the bibliography processing workflow.
"""
import logging
from typing import Dict


class SummaryReporter:
    """
    Handles tracking and reporting of processing metrics.

    This class acts as a centralized counter for all key actions performed
    during the workflow, such as the number of files processed, duplicates
    removed, and DOIs added. At the end of the process, it can log a
    formatted summary to the console.
    """

    def __init__(self):
        """Initializes the reporter with a predefined set of summary metrics."""
        self.summary: Dict[str, int] = {
            "files_processed": 0,
            "entries_ingested": 0,
            "dois_validated_or_added": 0,
            "duplicates_removed": 0,
            "final_verified_count": 0,
            "final_suspect_count": 0,
        }

    def update_summary(self, action: str, count: int):
        """
        Updates a specific metric in the summary report.

        This method is called by the main orchestrator after each phase of
        the workflow to record the results of that phase.

        Args:
            action: The name of the metric to update (must be a key in the
                `self.summary` dictionary).
            count: The new value for the metric.
        """
        if action in self.summary:
            self.summary[action] = count
        else:
            logging.warning(f"Attempted to update an unknown summary metric: '{action}'")

    def log_summary(self):
        """Logs the final, formatted processing summary to the console."""
        logging.info("\n--- Processing Summary ---")
        for key, value in self.summary.items():
            # Format the key for readability (e.g., 'files_processed' -> 'Files Processed')
            formatted_key = key.replace('_', ' ').title()
            logging.info(f"{formatted_key:<25}: {value}")
        logging.info("--------------------------\n")

