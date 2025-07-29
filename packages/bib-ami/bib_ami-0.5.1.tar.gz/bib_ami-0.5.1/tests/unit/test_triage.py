# ==============================================================================
# File: tests/unit/test_triage.py
# Unit tests for the Triage class.
# ==============================================================================

import unittest

from bibtexparser.bibdatabase import BibDatabase

from tests.fixtures.record_builder import RecordBuilder
from bib_ami.triage import Triage


class TestTriage(unittest.TestCase):
    def setUp(self):
        self.triage = Triage()

    def test_triage_logic(self):
        """Tests the classification of records into verified, accepted, and suspect."""
        db = BibDatabase()
        db.entries = [
            RecordBuilder("rec1").with_title("Verified Article").build(),
            RecordBuilder("rec2").with_title("Accepted Book").as_book().build(),
            RecordBuilder("rec3").with_title("Suspect Article").build(),
        ]
        db.entries[0]['verified_doi'] = "10.1/verified"
        db.entries[1]['verified_doi'] = None  # A book without a DOI is accepted
        db.entries[2]['verified_doi'] = None  # An article without a DOI is suspect

        # CORRECTED: Pass the required 'filter_validated' argument.
        verified_db, suspect_db = self.triage.run_triage(db, filter_validated=False)

        self.assertEqual(len(verified_db.entries), 2)
        self.assertEqual(len(suspect_db.entries), 1)
        self.assertEqual(suspect_db.entries[0]['ID'], 'rec3')
