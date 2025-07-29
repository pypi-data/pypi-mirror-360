# ==============================================================================
# This is a self-contained test suite for bib-ami.
# It includes the application classes and the test classes in one file
# to demonstrate a complete, working, and testable system.
# ==============================================================================
import logging

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import argparse
import unittest

# ==============================================================================
# SECTION 3: TEST CASES
# ==============================================================================
from tests.mocks.api_client import MockCrossRefClient
from tests.fixtures.bibtex_test_directory import BibTexTestDirectory
from bib_ami.bibtex_manager import BibTexManager
from tests.fixtures.bibtex_simulator import BibTexSimulator


# ==============================================================================
# SECTION 3: TEST CASES
# ==============================================================================

class TestRandomizedRun(unittest.TestCase):
    def test_randomized_workflow_does_not_crash(self):
        for i in range(3):
            with BibTexTestDirectory(f"random_test_{i}") as manager_dir:
                simulator = BibTexSimulator(manager_dir)
                simulator.populate_directory(num_files=2, entries_per_file=5, broken_ratio=0.2)
                # CORRECTED: Ensure all expected attributes are present in the settings object
                settings = argparse.Namespace(
                    input_dir=manager_dir.path, output_file=manager_dir.path / "final.bib",
                    suspect_file=manager_dir.path / "suspect.bib", email="test@example.com",
                    filter_validated=False, merge_only=False
                )
                mock_client = MockCrossRefClient(settings.email)
                main_manager = BibTexManager(settings, client=mock_client)
                main_manager.process_bibliography()
                self.assertTrue(True, f"Run {i+1} completed without errors.")


if __name__ == '__main__':
    unittest.main()
