# ==============================================================================
# File: bib_ami/bibtex_test_directory.py
# Updated orchestrator that uses the CLI settings and reporter.
# ==============================================================================

# ==============================================================================
# File: bib_ami/bibtex_test_directory.py
# Updated orchestrator that now uses the full reporting capabilities.
# ==============================================================================

import argparse
import logging
from typing import Optional

from .cross_ref_client import CrossRefClient
from .ingestor import Ingestor
from .reconciler import Reconciler
from .triage import Triage
from .validator import Validator
from .writer import Writer


class BibTexManager:
    """Orchestrates the bibliography processing workflow."""

    def __init__(self, settings: argparse.Namespace, client: Optional[CrossRefClient] = None):
        self.settings = settings
        # Use the injected client if provided, otherwise create a real one.
        self.client = client if client else CrossRefClient(email=self.settings.email)
        self.ingestor = Ingestor()
        self.validator = Validator(client=self.client)
        self.reconciler = Reconciler()
        self.triage = Triage()
        self.writer = Writer()

    def process_bibliography(self):
        database, num_files = self.ingestor.ingest_from_directory(self.settings.input_dir)
        database, validated_count = self.validator.validate_all(database)
        database, duplicates_removed = self.reconciler.deduplicate(database)
        verified_db, suspect_db = self.triage.run_triage(database, self.settings.filter_validated)
        self.writer.write_files(verified_db, suspect_db, self.settings.output_file, self.settings.suspect_file)
        logging.info("Workflow complete.")
