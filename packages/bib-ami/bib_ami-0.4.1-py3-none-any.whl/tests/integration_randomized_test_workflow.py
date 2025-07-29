import logging
import random
import shutil
import string
import unittest
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

# --- Assume these classes are in their respective files ---
# This self-contained example includes all necessary class definitions.

# --- DEPENDENCIES AND HELPER CLASSES ---

# 1. Logging and Libraries
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


# 2. The BibTexSimulator Class
class BibTexSimulator:
    def __init__(self, base_dir: str = "temp_test_bib_data"):
        self.base_dir = Path(base_dir)
        self.cleanup()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _generate_random_string(length: int = 8) -> str:
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def create_test_files(self, num_files: int, entries_per_file: int):
        logging.info(f"Populating '{self.base_dir}' with {num_files} files...")
        for i in range(num_files):
            file_path = self.base_dir / f"source_{i + 1}.bib"
            content = []
            for _ in range(entries_per_file):
                entry_id = f"entry_{uuid.uuid4().hex[:8]}"
                title = f"A Study of {self._generate_random_string(5).capitalize()}"
                author = f"{self._generate_random_string(6).capitalize()}, {self._generate_random_string(1).upper()}."
                year = random.randint(2000, 2024)
                entry_str = f"""@article{{{entry_id},
    title = {{{title}}},
    author = {{{author}}},
    year = {{{year}}}
}}"""
                content.append(entry_str)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(content))

    def get_directory_path(self) -> Path:
        return self.base_dir

    def cleanup(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)


# 3. The Mock API Client
# noinspection PyUnusedLocal
class MockCrossRefClient:
    @staticmethod
    def get_doi_for_entry(entry: Dict[str, Any]) -> Optional[str]:
        # Simulate a 75% chance of finding a DOI for any given entry
        if random.random() < 0.75:
            return f"10.9999/{uuid.uuid4().hex[:6]}"
        return None


# 4. The BibTexManager (with the fix from the last interaction)
class BibTexManager:
    def __init__(self, input_dir: str, output_file: str, suspect_file: str, client: Any):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.suspect_file = Path(suspect_file)
        self.crossref_client = client
        self.database = BibDatabase()
        self.summary = {}

    def _ingest_files(self):
        for file_path in self.input_dir.glob("*.bib"):
            with open(file_path, 'r', encoding='utf-8') as bibtex_file:
                db = bibtexparser.load(bibtex_file)
                self.database.entries.extend(db.entries)
        self.summary["entries_ingested"] = len(self.database.entries)

    def _validate_and_enrich_all(self):
        for entry in self.database.entries:
            entry['verified_doi'] = self.crossref_client.get_doi_for_entry(entry)

    def _reconcile_and_deduplicate(self):
        # This is a simplified version for the stress test
        # A full implementation would merge notes, etc.
        unique_entries = {e.get('verified_doi'): e for e in self.database.entries if e.get('verified_doi')}
        no_doi_entries = [e for e in self.database.entries if not e.get('verified_doi')]
        self.database.entries = list(unique_entries.values()) + no_doi_entries
        self.summary["duplicates_removed"] = self.summary["entries_ingested"] - len(self.database.entries)

    def _triage_and_write(self):
        verified_db, suspect_db = BibDatabase(), BibDatabase()
        for entry in self.database.entries:
            if entry.get('verified_doi'):
                verified_db.entries.append(entry)
            else:
                suspect_db.entries.append(entry)

        def clean_and_dump(db, file_path):
            for e in db.entries:
                if 'verified_doi' in e and e['verified_doi']:
                    e['doi'] = e['verified_doi']
                if 'verified_doi' in e:
                    del e['verified_doi']
            writer = BibTexWriter()
            with open(file_path, 'w', encoding='utf-8') as f:
                bibtexparser.dump(db, f, writer)

        clean_and_dump(verified_db, self.output_file)
        if suspect_db.entries:
            clean_and_dump(suspect_db, self.suspect_file)

        self.summary["final_verified_count"] = len(verified_db.entries)
        self.summary["final_suspect_count"] = len(suspect_db.entries)

    def process_bibliography(self):
        self._ingest_files()
        self._validate_and_enrich_all()
        self._reconcile_and_deduplicate()
        self._triage_and_write()
        logging.info(f"Run complete. Summary: {self.summary}")


# --- THE RANDOMIZED STRESS TEST ---

# noinspection PyTypeChecker
class TestWorkflowRobustness(unittest.TestCase):
    """
    A test suite to stress-test the BibTexManager with randomly generated data.
    """

    def test_repeated_runs_with_random_data(self):
        """
        Runs the full workflow multiple times with different, randomly
        generated sets of BibTeX files to test for robustness.
        """
        num_runs = 5  # Number of times to repeat the test
        logging.info(f"\n\n--- Starting Randomized Stress Test ({num_runs} runs) ---")

        for i in range(num_runs):
            test_run_dir = f"temp_stress_test_run_{i + 1}"
            simulator = BibTexSimulator(base_dir=test_run_dir)

            try:
                logging.info(f"\n--- Test Run {i + 1}/{num_runs} ---")

                # 1. Create a new set of random files
                num_files = random.randint(2, 5)
                entries_per_file = random.randint(5, 10)
                total_entries = num_files * entries_per_file
                simulator.create_test_files(num_files, entries_per_file)

                # 2. Instantiate manager with mock client
                mock_client = MockCrossRefClient()
                manager = BibTexManager(
                    input_dir=simulator.get_directory_path(),
                    output_file=Path(test_run_dir) / "final_library.bib",
                    suspect_file=Path(test_run_dir) / "suspect.bib",
                    client=mock_client
                )

                # 3. Run the process
                manager.process_bibliography()

                # 4. Assert basic integrity checks
                self.assertEqual(manager.summary['entries_ingested'], total_entries)
                self.assertLessEqual(manager.summary['final_verified_count'] + manager.summary['final_suspect_count'],
                                     total_entries)
                self.assertTrue(Path(test_run_dir, "final_library.bib").exists())

            finally:
                # 5. Clean up for the next run
                simulator.cleanup()

        logging.info("\n--- Randomized Stress Test Completed Successfully ---")


if __name__ == '__main__':
    unittest.main()
