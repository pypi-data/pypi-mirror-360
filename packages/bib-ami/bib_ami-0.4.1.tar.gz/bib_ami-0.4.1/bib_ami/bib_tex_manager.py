import logging
from pathlib import Path
from typing import Dict, List

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

from .cross_ref_client import CrossRefClient


# Assuming the CrossRefClient class is in a file named crossref_client.py
# from crossref_client import CrossRefClient

# For a single file example, we can paste the CrossRefClient class here or assume it's available.
# For this example, let's assume CrossRefClient is defined in the same scope.

# noinspection SpellCheckingInspection
class BibTexManager:
    """
    Orchestrates the workflow for cleaning and enriching a BibTeX library.

    This class implements the integrity-first workflow:
    1. Ingest all source files.
    2. Validate and enrich every entry with an authoritative DOI.
    3. Deduplicate using the verified DOIs as the primary key.
    4. Triage entries and write the final, clean files.
    """

    def __init__(self, input_dir: str, output_file: str, suspect_file: str, email: str):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.suspect_file = Path(suspect_file)

        self.crossref_client = CrossRefClient(email=email)
        self.database = BibDatabase()
        self.summary = {
            "files_processed": 0,
            "entries_ingested": 0,
            "dois_validated_or_added": 0,
            "duplicates_removed": 0,
            "final_verified_count": 0,
            "final_suspect_count": 0,
        }

    def _ingest_files(self):
        """Phase 1: Ingests all .bib files from the input directory."""
        logging.info(f"--- Phase 1: Ingesting files from '{self.input_dir}' ---")
        bib_files = list(self.input_dir.glob("*.bib"))

        for file_path in bib_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as bibtex_file:
                    # Using a robust parser configuration
                    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                    parser.ignore_nonstandard_types = False
                    parser.homogenise_fields = True
                    db = bibtexparser.load(bibtex_file, parser=parser)

                    # Tag each entry with its source for auditability
                    for entry in db.entries:
                        entry['source_file'] = str(file_path.name)

                    self.database.entries.extend(db.entries)
                    self.summary["files_processed"] += 1
            except Exception as e:
                logging.error(f"Failed to load or parse '{file_path}': {e}")

        self.summary["entries_ingested"] = len(self.database.entries)
        logging.info(
            f"Ingested {self.summary['entries_ingested']} entries from {self.summary['files_processed']} files.")

    def _validate_and_enrich_all(self):
        """Phase 2: Validates every entry against CrossRef to get a canonical DOI."""
        logging.info("--- Phase 2: Validating and Enriching All Entries with DOIs ---")
        for entry in self.database.entries:
            # Query CrossRef for a DOI based on metadata, regardless of existing DOI
            verified_doi = self.crossref_client.get_doi_for_entry(entry)

            if verified_doi:
                if 'doi' in entry and entry['doi'].lower() != verified_doi.lower():
                    logging.warning(
                        f"Corrected DOI for '{entry.get('ID')}': was '{entry['doi']}', now '{verified_doi}'")

                entry['verified_doi'] = verified_doi  # Use a new field for the canonical ID
                self.summary["dois_validated_or_added"] += 1
            else:
                entry['verified_doi'] = None  # Mark as unverified

        logging.info(f"Validated or added DOIs for {self.summary['dois_validated_or_added']} entries.")

    def _reconcile_and_deduplicate(self):
        """Phase 3: Deduplicates entries, prioritizing verified DOIs."""
        logging.info("--- Phase 3: Reconciling and Deduplicating Entries ---")
        initial_count = len(self.database.entries)

        # First pass: Deduplicate by verified DOI
        doi_map: Dict[str, List[Dict]] = {}
        no_doi_entries: List[Dict] = []

        for entry in self.database.entries:
            doi = entry.get('verified_doi')
            if doi:
                if doi.lower() not in doi_map:
                    doi_map[doi.lower()] = []
                doi_map[doi.lower()].append(entry)
            else:
                no_doi_entries.append(entry)

        reconciled_entries: List[Dict] = []
        for doi, group in doi_map.items():
            # Choose the "winner" (e.g., the one with the most fields)
            winner = max(group, key=len)
            # You could add logic here to merge user notes from other entries in the group
            reconciled_entries.append(winner)

        # You could add a fuzzy matching fallback for no_doi_entries here if desired
        # For now, we assume no fuzzy matching to keep it simple
        reconciled_entries.extend(no_doi_entries)

        self.database.entries = reconciled_entries
        self.summary["duplicates_removed"] = initial_count - len(self.database.entries)
        logging.info(f"Removed {self.summary['duplicates_removed']} duplicates.")

    def _triage_and_write(self):
        """Phase 4: Triages records and writes final output files."""
        logging.info("--- Phase 4: Triaging and Writing Output Files ---")
        verified_db = BibDatabase()
        suspect_db = BibDatabase()

        for entry in self.database.entries:
            entry_type = entry.get('ENTRYTYPE', 'misc').lower()
            if entry.get('verified_doi'):
                verified_db.entries.append(entry)
            elif entry_type in ['book', 'techreport', 'misc']:
                # Accept entries that often don't have DOIs
                verified_db.entries.append(entry)
            else:
                # Flag modern articles without DOIs as suspect
                suspect_db.entries.append(entry)

        self.summary['final_verified_count'] = len(verified_db.entries)
        self.summary['final_suspect_count'] = len(suspect_db.entries)

        writer = BibTexWriter()
        writer.indent = '  '
        writer.comma_first = True

        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                bibtexparser.dump(verified_db, f, writer)
            logging.info(
                f"Wrote {self.summary['final_verified_count']} verified/accepted entries to '{self.output_file}'")

            if suspect_db.entries:
                with open(self.suspect_file, 'w', encoding='utf-8') as f:
                    bibtexparser.dump(suspect_db, f, writer)
                logging.info(f"Wrote {self.summary['final_suspect_count']} suspect entries to '{self.suspect_file}'")
        except Exception as e:
            logging.error(f"Failed to write output files: {e}")

    def process_bibliography(self):
        """Executes the full, integrity-first workflow."""
        self._ingest_files()
        self._validate_and_enrich_all()
        self._reconcile_and_deduplicate()
        self._triage_and_write()

        logging.info("--- Workflow Complete ---")
        logging.info(f"Summary: {self.summary}")


# Example of how to run this
if __name__ == '__main__':
    # This is a placeholder for the real CLI runner
    # Setup dummy directories and files for a quick test
    dummy_input = Path("test_bib_input")
    dummy_input.mkdir(exist_ok=True)
    (dummy_input / "test1.bib").write_text("""
    @article{key1, title="A Title to Test", author="Doe, John"}
    """)
    (dummy_input / "test2.bib").write_text("""
    @article{key2, title="A Title to Test", author="Doe, J.", doi="10.1109/5.771073"}
    """)

    # IMPORTANT: Replace with your actual email
    user_email = "name@example.com"

    if user_email == "name1@example.com":
        print("Please set a valid email to run the example.")
    else:
        manager = BibTexManager(
            input_dir=str(dummy_input),
            output_file="final_library.bib",
            suspect_file="suspect_entries.bib",
            email=user_email
        )
        manager.process_bibliography()
