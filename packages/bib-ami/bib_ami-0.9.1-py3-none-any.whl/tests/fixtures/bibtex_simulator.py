import logging
import random
import string
import uuid

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from tests.fixtures.bibtex_test_directory import BibTexTestDirectory


# noinspection PyUnusedLocal,SpellCheckingInspection
class BibTexSimulator:
    """Generates synthetic BibTeX files and directories for testing."""

    def __init__(self, test_dir_manager: BibTexTestDirectory):
        self.manager = test_dir_manager

    @staticmethod
    def _generate_random_string(length: int = 8) -> str:
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def _create_well_formed_entry_str(self) -> str:
        entry_id = f"entry_{uuid.uuid4().hex[:8]}"
        title = f"A Study of {self._generate_random_string(5).capitalize()}"
        return f'@article{{{entry_id}, title={{{title}}}}}'

    def _create_pathological_entry_str(self) -> str:
        return f'@article{{{self._generate_random_string()}, title="Broken Entry"'  # Missing brace and comma

    def populate_directory(self, num_files: int, entries_per_file: int, broken_ratio: float = 0.1):
        logging.info(f"Populating directory with {num_files} files...")
        for i in range(num_files):
            file_path = self.manager.path / f"source_{i + 1}.bib"
            content = []
            for _ in range(entries_per_file):
                if random.random() < broken_ratio:
                    content.append(self._create_pathological_entry_str())
                else:
                    content.append(self._create_well_formed_entry_str())

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(content))
        self.manager.add_non_bib_file("notes.txt")
