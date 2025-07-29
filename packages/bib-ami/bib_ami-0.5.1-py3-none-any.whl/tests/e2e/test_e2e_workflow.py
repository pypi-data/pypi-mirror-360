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
    def test_full_run(self):
        """Tests the full pipeline from input files to final output."""
        with BibTexTestDirectory("e2e_test") as manager_dir:
            rec1 = RecordBuilder("rec1").with_title("Attention Is All You Need").with_note("Note A").build()
            rec2 = RecordBuilder("rec2").with_title("Attention is ALL you need").with_note("Note B").build()
            rec3 = RecordBuilder("rec3").with_title("A paper with no DOI").build()
            manager_dir.add_bib_file("source1.bib", [rec1, rec3])
            manager_dir.add_bib_file("source2.bib", [rec2])

            settings = argparse.Namespace(
                input_dir=manager_dir.path,
                output_file=manager_dir.path / "final.bib",
                suspect_file=manager_dir.path / "suspect.bib",
                email="test@example.com",
                filter_validated=False
            )

            # This is the simplified, transparent way to test:
            # 1. Create the mock client explicitly.
            mock_client = MockCrossRefClient(settings.email)
            # 2. Pass it directly to the manager during initialization.
            main_manager = BibTexManager(settings, client=mock_client)

            main_manager.process_bibliography()

            self.assertTrue(settings.output_file.exists())
            self.assertTrue(settings.suspect_file.exists(), "Suspect file was not created.")

            with open(settings.output_file, 'r') as f:
                final_db = bibtexparser.load(f)
            with open(settings.suspect_file, 'r') as f:
                suspect_db = bibtexparser.load(f)

            self.assertEqual(len(final_db.entries), 1)
            self.assertEqual(len(suspect_db.entries), 1)
            merged_entry = final_db.entries[0]
            self.assertIn("Note A", merged_entry['note'])
            self.assertIn("Note B", merged_entry['note'])
            self.assertEqual(merged_entry['doi'], '10.5555/attention')


if __name__ == '__main__':
    unittest.main()
