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
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# noinspection SpellCheckingInspection
class TestE2EWorkflow(unittest.TestCase):
    def test_full_run_with_fuzzy_dedupe(self):
        with BibTexTestDirectory("e2e_test") as manager_dir:
            rec1 = (
                RecordBuilder("rec1")
                .with_title("Attention Is All You Need")
                .with_note("Note A")
                .build()
            )
            rec2 = (
                RecordBuilder("rec2")
                .with_title("Attention is ALL you need")
                .with_note("Note B")
                .build()
            )
            rec3 = (
                RecordBuilder("rec3")
                .with_title("A paper about fuzzy logic")
                .build()
            )
            rec4 = (
                RecordBuilder("rec4")
                .with_title("A paper about fuzzy logic!!")
                .build()
            )
            rec5 = (
                RecordBuilder("rec5")
                .with_title("A truly unique paper")
                .build()
            )
            manager_dir.add_bib_file("source1.bib", [rec1, rec3, rec5])
            manager_dir.add_bib_file("source2.bib", [rec2, rec4])
            settings = argparse.Namespace(
                input_dir=manager_dir.path,
                output_file=manager_dir.path / "final.bib",
                suspect_file=manager_dir.path / "suspect.bib",
                email="test@example.com",
                filter_validated=False,
                merge_only=False,
            )
            mock_client = MockCrossRefClient(settings.email)
            main_manager = BibTexManager(settings, client=mock_client)
            main_manager.process_bibliography()
            with open(settings.output_file, "r") as f:
                final_db = bibtexparser.load(f)
            with open(settings.suspect_file, "r") as f:
                suspect_db = bibtexparser.load(f)
            self.assertEqual(len(final_db.entries), 1)
            self.assertEqual(len(suspect_db.entries), 2)
            merged_entry = final_db.entries[0]
            self.assertIn("Note A", merged_entry["note"])
            self.assertIn("Note B", merged_entry["note"])

    def test_merge_only_flag(self):
        """Tests that --merge-only stops the workflow after ingestion."""
        with BibTexTestDirectory("merge_only_test") as manager_dir:
            rec1 = RecordBuilder("rec1").with_title("Title A").build()
            rec2 = RecordBuilder("rec2").with_title("Title B").build()
            manager_dir.add_bib_file("source1.bib", [rec1])
            manager_dir.add_bib_file("source2.bib", [rec2])
            settings = argparse.Namespace(
                input_dir=manager_dir.path,
                output_file=manager_dir.path / "merged.bib",
                suspect_file=None,
                email="test@example.com",
                filter_validated=False,
                merge_only=True,
            )
            main_manager = BibTexManager(settings, client=None)
            main_manager.process_bibliography()
            with open(settings.output_file, "r") as f:
                final_db = bibtexparser.load(f)
            # Should contain both entries, unprocessed
            self.assertEqual(len(final_db.entries), 2)
            # No 'doi' field should have been added
            self.assertNotIn("doi", final_db.entries[0])

    def test_filter_validated_flag(self):
        with BibTexTestDirectory("filter_validated_test") as manager_dir:
            rec1 = (
                RecordBuilder("rec1")
                .with_title("Attention Is All You Need")
                .with_author("Vaswani")
                .build()
            )
            rec2 = (
                RecordBuilder("rec2")
                .with_title("A Study of Deep Learning")
                .with_author("LeCun")
                .build()
            )
            rec3 = (
                RecordBuilder("rec3")
                .with_title("Accepted Book")
                .as_book()
                .build()
            )
            rec4 = RecordBuilder("rec4").with_title("Suspect Article").build()
            manager_dir.add_bib_file("source.bib", [rec1, rec2, rec3, rec4])
            settings = argparse.Namespace(
                input_dir=manager_dir.path,
                output_file=manager_dir.path / "final.bib",
                suspect_file=manager_dir.path / "suspect.bib",
                email="test@example.com",
                filter_validated=True,
                merge_only=False,
            )
            mock_client = MockCrossRefClient(settings.email)
            main_manager = BibTexManager(settings, client=mock_client)
            main_manager.process_bibliography()
            with open(settings.output_file, "r") as f:
                final_db = bibtexparser.load(f)
            with open(settings.suspect_file, "r") as f:
                suspect_db = bibtexparser.load(f)
            self.assertEqual(len(final_db.entries), 2)
            self.assertEqual(len(suspect_db.entries), 2)

    def test_full_run_with_metadata_refresh(self):
        """Tests the full pipeline including metadata refreshing."""
        with BibTexTestDirectory("e2e_refresh_test") as manager_dir:
            rec1 = (
                RecordBuilder("rec1")
                .with_title("Attention Is All You Need")
                .with_author("A. Vaswani et al.")
                .build()
            )
            rec2 = (
                RecordBuilder("rec2").with_title("A paper with no DOI").build()
            )
            manager_dir.add_bib_file("source.bib", [rec1, rec2])

            settings = argparse.Namespace(
                input_dir=manager_dir.path,
                output_file=manager_dir.path / "final.bib",
                suspect_file=manager_dir.path / "suspect.bib",
                email="test@example.com",
                filter_validated=False,
                merge_only=False,
            )
            mock_client = MockCrossRefClient(settings.email)
            main_manager = BibTexManager(settings, client=mock_client)
            main_manager.process_bibliography()

            with open(settings.output_file, "r") as f:
                final_db = bibtexparser.load(f)

            self.assertEqual(len(final_db.entries), 1)
            verified_entry = final_db.entries[0]

            self.assertEqual(
                verified_entry["title"],
                "Attention Is All You Need (Canonical)",
            )


if __name__ == "__main__":
    unittest.main()
