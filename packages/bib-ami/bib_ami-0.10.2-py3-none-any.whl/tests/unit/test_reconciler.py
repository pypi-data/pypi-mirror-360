# ==============================================================================
# File: tests/unit/test_reconciler.py
# Unit tests for the Reconciler class.
# ==============================================================================
import unittest

from bibtexparser.bibdatabase import BibDatabase

from tests.fixtures.record_builder import RecordBuilder

# Assuming the Reconciler class is in bib_ami.reconciler
from bib_ami.reconciler import Reconciler


class TestReconciler(unittest.TestCase):
    def setUp(self):
        self.reconciler = Reconciler()

    def test_deduplication_by_doi(self):
        db = BibDatabase()
        db.entries = [
            RecordBuilder("rec1")
            .with_title("Title A")
            .with_note("Note 1")
            .build(),
            RecordBuilder("rec2").with_title("Title B").build(),
            RecordBuilder("rec3")
            .with_title("Title A Prime")
            .with_note("Note 3")
            .build(),
        ]
        # Simulate that the Validator has run
        for entry in db.entries:
            entry["audit_info"] = {"changes": []}
        db.entries[0]["verified_doi"] = "10.1/test"
        db.entries[1]["verified_doi"] = "10.2/another"
        db.entries[2]["verified_doi"] = "10.1/test"
        reconciled_db, removed_count = self.reconciler.deduplicate(db)
        self.assertEqual(removed_count, 1)
        self.assertEqual(len(reconciled_db.entries), 2)
        merged_entry = next(
            e
            for e in reconciled_db.entries
            if e.get("verified_doi") == "10.1/test"
        )
        self.assertIn("Note 1", merged_entry["note"])
        self.assertIn("Note 3", merged_entry["note"])
