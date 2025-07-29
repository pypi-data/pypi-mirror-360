import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Self

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ==============================================================================
# File: tests/fixtures/bibtex_test_directory.py
# A context manager to handle temporary test directories.
# ==============================================================================

class BibTexTestDirectory:
    def __init__(self, base_dir: str = "temp_test_env"):
        self.path = Path(base_dir)

    def __enter__(self) -> Self:
        if self.path.exists():
            shutil.rmtree(self.path)
        self.path.mkdir(parents=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.path.exists():
            shutil.rmtree(self.path)

    def add_bib_file(self, filename: str, entries: list[Dict[str, Any]]):
        db = BibDatabase()
        db.entries = entries
        writer = BibTexWriter()
        with open(self.path / filename, 'w', encoding='utf-8') as f:
            bibtexparser.dump(db, f, writer)

    def add_non_bib_file(self, filename: str, content: str = "This is not a bib file."):
        self.path.joinpath(filename).write_text(content)
