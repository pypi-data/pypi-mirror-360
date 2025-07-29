"""
This module contains the Ingestor class, which is responsible for discovering,
parsing, and consolidating BibTeX files from a directory.
"""

import logging
from pathlib import Path

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase


class Ingestor:
    """
    Finds and parses all .bib files from a directory into a single database.

    This class encapsulates all file system I/O and initial parsing logic.
    It is designed to be robust against common issues like unreadable files
    or varied BibTeX formats.
    """

    @staticmethod
    def ingest_from_directory(input_dir: Path) -> (BibDatabase, int):
        """
        Scans a directory for .bib files, parses them, and merges them.

        For each entry found, it adds a 'source_file' field to track its
        origin, which is crucial for the audit trail.

        Args:
            input_dir: The path to the directory to scan for .bib files.

        Returns:
            A tuple containing:
                - A single BibDatabase object with all entries from all found files.
                - An integer count of the number of .bib files processed.
        """
        database = BibDatabase()
        bib_files = list(input_dir.glob("*.bib"))

        logging.info(f"Found {len(bib_files)} .bib files in '{input_dir}'.")

        for file_path in bib_files:
            try:
                with open(file_path, "r", encoding="utf-8") as bibtex_file:
                    # Use a robust parser configuration
                    parser = bibtexparser.bparser.BibTexParser(
                        common_strings=True,
                        ignore_nonstandard_types=False
                        # CORRECTED: Removed `homogenise_fields=True` as it was causing
                        # downstream KeyErrors by lowercasing all field names.
                    )
                    db = bibtexparser.load(bibtex_file, parser=parser)

                    # Tag each entry with its source file for auditability
                    for entry in db.entries:
                        entry["source_file"] = str(file_path.name)

                    database.entries.extend(db.entries)
                    logging.info(f"Successfully ingested {len(db.entries)} entries from '{file_path.name}'.")

            except Exception as e:
                # Log errors for specific files but continue processing others.
                logging.error(f"Failed to parse '{file_path}': {e}")

        return database, len(bib_files)
