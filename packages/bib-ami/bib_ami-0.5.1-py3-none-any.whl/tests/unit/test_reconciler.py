# ==============================================================================
# File: tests/unit/test_reconciler.py
# Unit tests for the Reconciler class.
# ==============================================================================
import unittest

from bibtexparser.bibdatabase import BibDatabase

from tests.fixtures.record_builder import RecordBuilder


# Assuming the Reconciler class is in bib_ami.reconciler
# from bib_ami.reconciler import Reconciler

class TestReconciler(unittest.TestCase):
    def setUp(self):
        # In a real project, this would import the class
        from bib_ami.reconciler import Reconciler
        self.reconciler = Reconciler()

    def test_deduplication_by_doi(self):
        """Tests that records with the same verified DOI are merged."""
        db = BibDatabase()
        db.entries = [
            RecordBuilder("rec1").with_title("Title A").with_note("Note 1").build(),
            RecordBuilder("rec2").with_title("Title B").with_note("Note 2").build(),
            RecordBuilder("rec3").with_title("Title A Prime").with_note("Note 3").build(),
        ]
        db.entries[0]['verified_doi'] = "10.1/test"
        db.entries[1]['verified_doi'] = "10.2/another"
        db.entries[2]['verified_doi'] = "10.1/test"  # Duplicate DOI

        reconciled_db, removed_count = self.reconciler.deduplicate(db)

        self.assertEqual(removed_count, 1)
        self.assertEqual(len(reconciled_db.entries), 2)

        # Check that notes were merged
        merged_entry = next(e for e in reconciled_db.entries if e.get('verified_doi') == "10.1/test")
        self.assertIn("Note 1", merged_entry['note'])
        self.assertIn("Note 3", merged_entry['note'])
