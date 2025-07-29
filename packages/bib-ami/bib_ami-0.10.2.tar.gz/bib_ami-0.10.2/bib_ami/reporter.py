# ==============================================================================
# File: bib_ami/reporter.py
# New file to handle tracking and logging of metrics.
# ==============================================================================
import logging


class SummaryReporter:
    """Handles tracking and reporting of processing metrics."""

    def __init__(self):
        self.summary = {
            "files_processed": 0,
            "entries_ingested": 0,
            "dois_validated_or_added": 0,
            "duplicates_removed": 0,
            "final_verified_count": 0,
            "final_suspect_count": 0,
        }

    def update_summary(self, action: str, count: int):
        """Update summary metrics."""
        if action in self.summary:
            self.summary[action] = count

    def log_summary(self):
        """Log processing summary to console."""
        logging.info("\n--- Processing Summary ---")
        for key, value in self.summary.items():
            logging.info(f"{key.replace('_', ' ').title():<25}: {value}")
        logging.info("--------------------------\n")
