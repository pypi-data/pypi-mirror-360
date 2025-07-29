import logging
from pathlib import Path

from tests.fixtures.directory_manager import BibTexTestDirectory
from tests.fixtures.record_builder import RecordBuilder

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ==============================================================================
# --- Example Usage Demonstration ---
# This block shows how these helper classes would be used in a real test script.
# ==============================================================================
if __name__ == '__main__':
    print("--- Demonstrating Test Infrastructure Helpers ---")

    # 1. Use the RecordBuilder to create clear, readable test data
    print("\nStep 1: Building test records with RecordBuilder...")
    # noinspection SpellCheckingInspection
    record1 = RecordBuilder("vaswani2017").with_title("Attention Is All You Need").with_doi("10.1/attention").build()
    record2 = RecordBuilder("lecun1998").with_title("Gradient-Based Learning").build()
    record3_book = RecordBuilder("aho2006").with_title("Compilers: Principles, Techniques, & Tools").as_book().build()

    print("Successfully created 3 record objects.")

    # 2. Use the BibTexTestDirectory to create a temporary test environment
    print("\nStep 2: Setting up a temporary test environment with BibTexTestDirectory...")
    try:
        with BibTexTestDirectory("my_integration_test") as temp_dir:
            # 3. Populate the environment with test files
            temp_dir.add_bib_file("source1.bib", [record1, record2])
            temp_dir.add_bib_file("source2.bib", [record3_book])
            temp_dir.add_non_bib_file("notes.txt")

            print(f"\nTest environment created at: {temp_dir.path.resolve()}")
            print("Directory contents:")
            for item in temp_dir.path.iterdir():
                print(f"- {item.name}")

            # In a real test, you would now run BibTexManager on `temp_dir.path`
            # and assert that its outputs are correct.
            print("\n(At this point, you would run the main application logic on the test directory.)")

        # 4. The context manager automatically cleans up the directory
        print("\nStep 3: Test complete. The temporary directory has been automatically removed.")
        assert not Path("my_integration_test").exists()

    except Exception as e:
        print(f"An error occurred during the demonstration: {e}")
