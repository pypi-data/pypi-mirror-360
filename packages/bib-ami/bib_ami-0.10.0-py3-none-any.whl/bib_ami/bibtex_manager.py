# ==============================================================================
# File: bib_ami/bibtex_test_directory.py
# Updated orchestrator that uses the CLI settings and reporter.
# ==============================================================================

import argparse
import logging
from typing import Optional

import bibtexparser
from bibtexparser.bwriter import BibTexWriter

from .cross_ref_client import CrossRefClient
from .ingestor import Ingestor
from .metadata_refresher import MetadataRefresher
from .reconciler import Reconciler
from .triage import Triage
from .validator import Validator
from .writer import Writer


class BibTexManager:
    """Orchestrates the bibliography processing workflow."""

    def __init__(self, settings: argparse.Namespace, client: Optional[CrossRefClient] = None):
        self.settings = settings
        self.client = client if client else CrossRefClient(email=self.settings.email)
        self.ingestor = Ingestor()
        self.validator = Validator(client=self.client)
        self.refresher = MetadataRefresher(client=self.client)
        self.reconciler = Reconciler()
        self.triage = Triage()
        self.writer = Writer()

    def process_bibliography(self):
        database, num_files = self.ingestor.ingest_from_directory(self.settings.input_dir)
        # CORRECTED: Handle --merge-only flag at the beginning.
        if self.settings.merge_only:
            simple_writer = BibTexWriter()
            with open(self.settings.output_file, 'w', encoding='utf-8') as f:
                bibtexparser.dump(database, f, simple_writer)
            logging.info("Merge-only complete.")
            return
        database, validated_count = self.validator.validate_all(database)
        database = self.refresher.refresh_all(database)
        database, duplicates_removed = self.reconciler.deduplicate(database)
        verified_db, suspect_db = self.triage.run_triage(database, self.settings.filter_validated)
        self.writer.write_files(verified_db, suspect_db, self.settings.output_file, self.settings.suspect_file)
        logging.info("Workflow complete.")
