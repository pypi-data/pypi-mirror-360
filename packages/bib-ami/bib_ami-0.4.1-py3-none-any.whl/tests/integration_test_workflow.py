import logging
import shutil
import unittest
from pathlib import Path
from typing import Dict, Any, Optional, List

# 1. The Real CrossRefClient (for type hinting and interface matching)
from fuzzywuzzy import fuzz


# --- Assume these classes are in their respective files ---
# from bib_ami.manager import BibTexManager
# from bib_ami.crossref import CrossRefClient
# For this self-contained example, we'll include the necessary classes here.
# --- DEPENDENCIES (Pasted from previous responses for a runnable example) ---


class CrossRefClient:
    def __init__(self, email: str, timeout: int = 10, max_retries: int = 3):
        pass  # The mock will replace the implementation

    def get_doi_for_entry(self, entry: Dict[str, Any]) -> Optional[str]:
        raise NotImplementedError


# 2. The BibTexManager
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


class BibTexManager:
    """Orchestrator class from the previous step."""

    def __init__(self, input_dir: str, output_file: str, suspect_file: str, email: str, client: Any):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.suspect_file = Path(suspect_file)
        self.crossref_client = client  # Use the provided client (real or mock)
        self.database = BibDatabase()
        self.summary = {
            "files_processed": 0, "entries_ingested": 0, "dois_validated_or_added": 0,
            "duplicates_removed": 0, "final_verified_count": 0, "final_suspect_count": 0,
        }

    def _ingest_files(self):
        logging.info(f"--- Phase 1: Ingesting files from '{self.input_dir}' ---")
        for file_path in self.input_dir.glob("*.bib"):
            with open(file_path, 'r', encoding='utf-8') as bibtex_file:
                db = bibtexparser.load(bibtex_file)
                # Tag each entry with its source for auditability
                for entry in db.entries:
                    entry['source_file'] = str(file_path.name)
                self.database.entries.extend(db.entries)
                self.summary['files_processed'] += 1
        self.summary["entries_ingested"] = len(self.database.entries)

    def _validate_and_enrich_all(self):
        logging.info("--- Phase 2: Validating and Enriching All Entries with DOIs ---")
        for entry in self.database.entries:
            verified_doi = self.crossref_client.get_doi_for_entry(entry)
            if verified_doi:
                entry['verified_doi'] = verified_doi
                self.summary["dois_validated_or_added"] += 1
            else:
                entry['verified_doi'] = None

    def _reconcile_and_deduplicate(self):
        logging.info("--- Phase 3: Reconciling and Deduplicating Entries ---")
        initial_count = len(self.database.entries)
        doi_map: Dict[str, List[Dict]] = {}
        no_doi_entries: List[Dict] = []
        for entry in self.database.entries:
            doi = entry.get('verified_doi')
            if doi:
                doi_key = doi.lower()
                if doi_key not in doi_map: doi_map[doi_key] = []
                doi_map[doi_key].append(entry)
            else:
                no_doi_entries.append(entry)
        reconciled_entries: List[Dict] = []
        for group in doi_map.values():
            winner = max(group, key=len)
            # Simple merge of 'note' field for demonstration
            notes = {e.get('note') for e in group if e.get('note')}
            if notes:
                winner['note'] = " | ".join(sorted(list(notes)))
            reconciled_entries.append(winner)
        reconciled_entries.extend(no_doi_entries)
        self.database.entries = reconciled_entries
        self.summary["duplicates_removed"] = initial_count - len(self.database.entries)

    def _triage_and_write(self):
        logging.info("--- Phase 4: Triaging and Writing Output Files ---")
        verified_db = BibDatabase()
        suspect_db = BibDatabase()
        for entry in self.database.entries:
            if entry.get('verified_doi'):
                verified_db.entries.append(entry)
            else:
                suspect_db.entries.append(entry)

        self.summary['final_verified_count'] = len(verified_db.entries)
        self.summary['final_suspect_count'] = len(suspect_db.entries)

        def clean_entry_for_writing(entry: Dict[str, Any]) -> Dict[str, Any]:
            """Removes internal fields before writing to a .bib file."""
            cleaned_entry = entry.copy()
            # Promote verified_doi to the main doi field if it exists
            if 'verified_doi' in cleaned_entry and cleaned_entry['verified_doi']:
                cleaned_entry['doi'] = cleaned_entry['verified_doi']

            # Remove internal processing fields to avoid writing them
            internal_fields = ['verified_doi', 'source_file']
            for field in internal_fields:
                if field in cleaned_entry:
                    del cleaned_entry[field]

            return cleaned_entry

        # Clean entries before writing to prevent errors with non-string fields
        verified_db.entries = [clean_entry_for_writing(e) for e in verified_db.entries]
        suspect_db.entries = [clean_entry_for_writing(e) for e in suspect_db.entries]

        writer = BibTexWriter()
        with open(self.output_file, 'w', encoding='utf-8') as f:
            bibtexparser.dump(verified_db, f, writer)
        if suspect_db.entries:
            with open(self.suspect_file, 'w', encoding='utf-8') as f:
                bibtexparser.dump(suspect_db, f, writer)

    def process_bibliography(self):
        self._ingest_files()
        self._validate_and_enrich_all()
        self._reconcile_and_deduplicate()
        self._triage_and_write()
        logging.info(f"--- Workflow Complete ---\nSummary: {self.summary}")


# --- TEST-SPECIFIC CLASSES ---

class MockCrossRefClient(CrossRefClient):
    """A mock client that simulates CrossRef API responses for testing."""

    DOI_DATABASE = {
        "attention is all you need": "10.5555/attention",
        "a study of deep learning": "10.5555/deeplearn",
    }

    def get_doi_for_entry(self, entry: Dict[str, Any]) -> Optional[str]:
        title = entry.get("title", "").lower()
        for key, doi in self.DOI_DATABASE.items():
            if fuzz.ratio(title, key) > 95:
                logging.info(f"MOCK: Found DOI {doi} for title '{entry.get('title')}'")
                return doi
        logging.info(f"MOCK: No DOI found for title '{entry.get('title')}'")
        return None


class TestManagerValidationAndReconciliation(unittest.TestCase):
    """
    A test suite to demonstrate that the BibTexManager correctly validates,
    enriches, and deduplicates entries.
    """

    def setUp(self):
        """Create a temporary directory and test files."""
        self.test_dir = Path("temp_test_dir")
        self.test_dir.mkdir(exist_ok=True)
        self.output_file = self.test_dir / "final_library.bib"
        self.suspect_file = self.test_dir / "suspect.bib"

        file1_content = """@article{vaswani2017,
            title = {Attention Is All You Need},
            author = {Vaswani, Ashish},
            doi = {10.5555/attention},
            note = {User note from file 1}
        }"""
        file2_content = """@article{vaswani_duplicate,
            title = {Attention is all you need!},
            author = {Vaswani, A.},
            doi = {10.WRONG/DOI},
            note = {A second note to be merged}
        }
        @article{lecun_deep,
            title = {A Study of Deep Learning},
            author = {LeCun, Yann}
        }"""
        file3_content = """@misc{unknown_paper,
            title = {A Paper on Obscure Topics},
            author = {Nobody, N.}
        }"""

        (self.test_dir / "file1.bib").write_text(file1_content)
        (self.test_dir / "file2.bib").write_text(file2_content)
        (self.test_dir / "file3.bib").write_text(file3_content)

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_workflow(self):
        """Demonstrates the validation and reconciliation workflow."""
        mock_client = MockCrossRefClient(email="test@example.com")
        manager = BibTexManager(
            input_dir=str(self.test_dir),
            output_file=str(self.output_file),
            suspect_file=str(self.suspect_file),
            email="test@example.com",
            client=mock_client
        )

        manager.process_bibliography()

        with open(self.output_file, 'r') as f:
            final_content = f.read()

        with open(self.suspect_file, 'r') as f:
            suspect_content = f.read()

        print("\n--- DEMONSTRATION RESULTS ---")
        print("\n[SUMMARY REPORT]")
        for key, value in manager.summary.items():
            print(f"{key.replace('_', ' ').title():<25}: {value}")

        print("\n[FINAL VERIFIED LIBRARY (final_library.bib)]")
        print(final_content)

        print("\n[SUSPECT ENTRIES (suspect.bib)]")
        print(suspect_content)
        print("---------------------------\n")

        self.assertEqual(manager.summary['duplicates_removed'], 1)
        self.assertEqual(manager.summary['dois_validated_or_added'], 3)
        self.assertEqual(manager.summary['final_verified_count'], 2)
        self.assertEqual(manager.summary['final_suspect_count'], 1)
        self.assertIn("A second note to be merged | User note from file 1", final_content)
        self.assertIn("A Paper on Obscure Topics", suspect_content)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
