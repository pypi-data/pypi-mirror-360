import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Self

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ==============================================================================
# File: tests/fixtures/directory_manager.py
# A context manager to handle temporary test directories.
# ==============================================================================

class BibTexTestDirectory:
    """
    A context manager to create and automatically clean up temporary directories for testing.

    Example:
        with BibTexTestDirectory("my_test") as manager:
            manager.add_bib_file("file1.bib", [record1, record2])
            # ... run test on the directory manager.path ...
        # The directory is automatically removed upon exiting the 'with' block.
    """

    def __init__(self, base_dir: str = "temp_test_env"):
        self.path = Path(base_dir)

    def __enter__(self) -> Self:
        """Creates the temporary directory when entering the 'with' block."""
        if self.path.exists():
            shutil.rmtree(self.path)
        self.path.mkdir(parents=True)
        logging.info(f"Created test directory: {self.path.resolve()}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleans up the temporary directory when exiting the 'with' block."""
        if self.path.exists():
            shutil.rmtree(self.path)
            logging.info(f"Cleaned up test directory: {self.path.resolve()}")

    def add_bib_file(self, filename: str, entries: list[Dict[str, Any]]):
        """
        Creates a .bib file in the test directory with the given entries.

        Args:
            filename (str): The name of the .bib file to create.
            entries (list): A list of record dictionaries (created with RecordBuilder).
        """
        from bibtexparser.bwriter import BibTexWriter
        from bibtexparser.bibdatabase import BibDatabase
        import bibtexparser

        db = BibDatabase()
        db.entries = entries
        writer = BibTexWriter()

        file_path = self.path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            bibtexparser.dump(db, f, writer)
        logging.info(f"Created test file '{file_path}' with {len(entries)} entries.")

    def add_non_bib_file(self, filename: str, content: str = "This is not a bib file."):
        """Adds a non-bibliographic file to the test directory."""
        file_path = self.path / filename
        file_path.write_text(content, encoding='utf-8')
        logging.info(f"Created non-bib file '{file_path}'.")
