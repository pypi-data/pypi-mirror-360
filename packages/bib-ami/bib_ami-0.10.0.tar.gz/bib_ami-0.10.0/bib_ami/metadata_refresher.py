# ==============================================================================
# This is a self-contained test suite for bib-ami.
# It includes the application classes and the test classes in one file
# to demonstrate a complete, working, and testable system.
# ==============================================================================
import logging
import random
import shutil
import string
import unittest
import uuid
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, Self, List

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter
from fuzzywuzzy import fuzz
from bib_ami.cross_ref_client import CrossRefClient


class MetadataRefresher:
    """Refreshes entry metadata using a verified DOI."""

    def __init__(self, client: CrossRefClient):
        self.client = client

    def refresh_all(self, database: BibDatabase) -> BibDatabase:
        logging.info("--- Phase 2b: Refreshing Metadata from CrossRef ---")
        refreshed_count = 0
        for entry in database.entries:
            if entry.get('verified_doi'):
                metadata = self.client.get_metadata_by_doi(entry['verified_doi'])
                if metadata:
                    changed = False
                    # CORRECTED: Only update fields if the new value is not None/empty
                    for field in ['title', 'author', 'year', 'journal']:
                        new_value = metadata.get(field)
                        if new_value and entry.get(field) != new_value:
                            entry[field] = new_value
                            changed = True

                    if changed:
                        entry['audit_info']['changes'].append("Refreshed metadata from CrossRef.")
                        refreshed_count += 1
        logging.info(f"Refreshed metadata for {refreshed_count} entries.")
        return database

