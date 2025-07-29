# ==============================================================================
# This is a self-contained test suite for bib-ami.
# It includes the application classes and the test classes in one file
# to demonstrate a complete, working, and testable system.
# ==============================================================================
import argparse
import logging
import unittest

import bibtexparser

from bib_ami.bibtex_manager import BibTexManager
from tests.fixtures.bibtex_test_directory import BibTexTestDirectory
from tests.fixtures.record_builder import RecordBuilder
from tests.mocks.api_client import MockCrossRefClient

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestE2EWorkflow(unittest.TestCase):
    def test_full_run_with_fuzzy_dedupe(self):
        """Tests the full pipeline, including the fuzzy matching fallback."""
        with BibTexTestDirectory("e2e_test") as manager_dir:
            # Case 1: DOI duplicates
            rec1 = RecordBuilder("rec1").with_title("Attention Is All You Need").with_note("Note A").build()
            rec2 = RecordBuilder("rec2").with_title("Attention is ALL you need").with_note("Note B").build()
            # Case 2: Fuzzy duplicates without DOIs
            rec3 = RecordBuilder("rec3").with_title("A paper about fuzzy logic").build()
            rec4 = RecordBuilder("rec4").with_title("A paper about fuzzy logic!!").build()
            # Case 3: A unique suspect entry
            rec5 = RecordBuilder("rec5").with_title("A truly unique paper").build()

            manager_dir.add_bib_file("source1.bib", [rec1, rec3, rec5])
            manager_dir.add_bib_file("source2.bib", [rec2, rec4])

            settings = argparse.Namespace(
                input_dir=manager_dir.path, output_file=manager_dir.path / "final.bib",
                suspect_file=manager_dir.path / "suspect.bib", email="test@example.com", filter_validated=False
            )
            mock_client = MockCrossRefClient(settings.email)
            main_manager = BibTexManager(settings, client=mock_client)
            main_manager.process_bibliography()

            with open(settings.output_file, 'r') as f:
                final_db = bibtexparser.load(f)
            with open(settings.suspect_file, 'r') as f:
                suspect_db = bibtexparser.load(f)

            # Expected: 1 merged DOI entry
            self.assertEqual(len(final_db.entries), 1)
            # Expected: 1 fuzzy-deduped entry + 1 unique entry
            self.assertEqual(len(suspect_db.entries), 2)

            # Verify DOI merge
            merged_entry = final_db.entries[0]
            self.assertIn("Note A", merged_entry['note'])
            self.assertIn("Note B", merged_entry['note'])

            # Verify fuzzy dedupe result
            suspect_titles = {e['title'] for e in suspect_db.entries}
            self.assertIn("A paper about fuzzy logic", suspect_titles)
            self.assertIn("A truly unique paper", suspect_titles)


if __name__ == '__main__':
    unittest.main()
