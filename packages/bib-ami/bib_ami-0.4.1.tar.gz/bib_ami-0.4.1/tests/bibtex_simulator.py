import logging
import random
import string
from pathlib import Path
import shutil
import uuid

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# noinspection PyUnusedLocal
class BibTexSimulator:
    """
    Generates synthetic BibTeX files and directories for testing purposes.

    This class can create well-formed, duplicate, and pathological .bib files
    within a temporary directory structure, providing a controlled environment
    for testing the ingestion phase of a bibliography manager.
    """

    def __init__(self, base_dir: str = "temp_test_bib_data"):
        """
        Initializes the simulator.

        Args:
            base_dir (str): The root directory where test data will be created.
        """
        self.base_dir = Path(base_dir)
        self.cleanup()  # Ensure a clean state on initialization
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created temporary directory: {self.base_dir.resolve()}")

    @staticmethod
    def _generate_random_string(length: int = 8) -> str:
        """Generates a random alphanumeric string."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def _create_well_formed_entry(self, entry_id: str) -> str:
        """Generates a single, well-formed BibTeX entry string."""
        title = f"A Study of {self._generate_random_string(5).capitalize()} and Its Effects"
        author = f"{self._generate_random_string(6).capitalize()}, {self._generate_random_string(1).upper()}."
        year = random.randint(2000, 2024)
        journal = f"Journal of Synthetic Results {random.randint(1, 100)}"
        return f"""@article{{{entry_id},
            title = {{{title}}},
            author = {{{author}}},
            journal = {{{journal}}},
            year = {{{year}}},
            doi = {{10.1000/{self._generate_random_string()}}}
        }}"""

    @staticmethod
    def _create_duplicate_entry(original_entry: str) -> str:
        """Creates a slightly modified duplicate of an existing entry."""
        # Simulate common variations: case changes, extra braces, slight author changes
        duplicate = original_entry.replace("Study", "study")
        duplicate = duplicate.replace("{A Study", "{{A Study")  # Add extra braces
        return duplicate

    def _create_pathological_entry(self) -> str:
        """Generates a BibTeX entry with common syntax errors."""
        return f"""@article{{{self._generate_random_string()},
            title = {{"A Broken Entry with Missing Comma"}},
            author = "Malfoy D."
            year = 2023
        }}"""  # Missing comma after author

    def populate_directory(self, num_files: int, entries_per_file: int, duplicate_ratio: float = 0.2,
                           broken_ratio: float = 0.1):
        """
        Populates the test directory with a mix of .bib and other files.

        Args:
            num_files (int): The number of .bib files to create.
            entries_per_file (int): The number of entries to generate for each file.
            duplicate_ratio (float): The proportion of entries that should be duplicates.
            broken_ratio (float): The proportion of entries that should be syntactically broken.
        """
        logging.info(f"Populating directory with {num_files} files...")
        all_entries = []

        for i in range(num_files):
            file_path = self.base_dir / f"source_{i + 1}.bib"
            file_content = []

            for _ in range(entries_per_file):
                if random.random() < broken_ratio:
                    entry_str = self._create_pathological_entry()
                else:
                    entry_id = f"entry_{uuid.uuid4().hex[:8]}"
                    entry_str = self._create_well_formed_entry(entry_id)
                    all_entries.append(entry_str)

            # Add some duplicates
            num_duplicates = int(entries_per_file * duplicate_ratio)
            if all_entries and num_duplicates > 0:
                for _ in range(num_duplicates):
                    original = random.choice(all_entries)
                    file_content.append(self._create_duplicate_entry(original))

            file_content.extend(random.sample(all_entries, min(len(all_entries), entries_per_file - num_duplicates)))

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(file_content))

        # Add some non-bib files to ensure they are ignored
        (self.base_dir / "notes.txt").write_text("This is not a bib file.")
        (self.base_dir / "README.md").write_text("# Readme")
        logging.info("Population complete.")

    def get_directory_path(self) -> Path:
        """Returns the path to the created test directory."""
        return self.base_dir

    def cleanup(self):
        """Removes the temporary directory and all its contents."""
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)
            logging.info(f"Cleaned up temporary directory: {self.base_dir.resolve()}")


# --- Example Usage ---
if __name__ == "__main__":
    # This demonstrates how the simulator can be used in a test script

    # 1. Create a simulator instance
    simulator = BibTexSimulator(base_dir="my_temp_bib_files")

    try:
        # 2. Populate the directory with test data
        simulator.populate_directory(num_files=3, entries_per_file=5)

        # In a real test, you would now run your BibTexManager
        # on the directory returned by simulator.get_directory_path()
        input_path = simulator.get_directory_path()
        print(f"\nTest directory created at: {input_path.resolve()}")
        print("You can now run your ingestion logic on this directory.")
        print("\nContents of a sample file (source_1.bib):")
        with open(input_path / "source_1.bib", "r") as f:
            print(f.read())

    finally:
        # 3. Clean up the directory after the test
        simulator.cleanup()
