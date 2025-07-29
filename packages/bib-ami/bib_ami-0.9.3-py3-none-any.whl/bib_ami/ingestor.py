# ==============================================================================
# File: bib_ami/ingestor.py
# New class responsible for file discovery and parsing.
# ==============================================================================
import logging
from pathlib import Path

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase


class Ingestor:
    """Finds and parses all .bib files from a directory."""

    @staticmethod
    def ingest_from_directory(input_dir: Path) -> (BibDatabase, int):
        database = BibDatabase()
        bib_files = list(input_dir.glob("*.bib"))
        for file_path in bib_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as bibtex_file:
                    db = bibtexparser.load(bibtex_file)
                    database.entries.extend(db.entries)
            except Exception as e:
                logging.error(f"Failed to parse '{file_path}': {e}")
        return database, len(bib_files)
