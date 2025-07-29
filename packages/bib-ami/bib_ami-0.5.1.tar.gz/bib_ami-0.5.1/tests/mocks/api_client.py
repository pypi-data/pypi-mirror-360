# ==============================================================================
# File: tests/mocks/api_client.py
# Contains the mock for the CrossRefClient.
# ==============================================================================
from typing import Dict, Any, Optional

from fuzzywuzzy import fuzz

from bib_ami.cross_ref_client import CrossRefClient


class MockCrossRefClient(CrossRefClient):
    """A mock client that simulates CrossRef API responses for testing."""

    def __init__(self, email: str):
        super().__init__(email)
        self.doi_database = {"attention is all you need": "10.5555/attention"}

    def get_doi_for_entry(self, entry: Dict[str, Any]) -> Optional[str]:
        title = entry.get("title", "").lower()
        for key, doi in self.doi_database.items():
            if fuzz.ratio(title, key) > 95:
                return doi
        return None
