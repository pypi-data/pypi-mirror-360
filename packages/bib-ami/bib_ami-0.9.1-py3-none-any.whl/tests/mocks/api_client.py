# ==============================================================================
# File: tests/mocks/api_client.py
# Contains the mock for the CrossRefClient.
# ==============================================================================

import random
import uuid
from typing import Dict, Any, Optional

from fuzzywuzzy import fuzz

from bib_ami.cross_ref_client import CrossRefClient


class MockCrossRefClient(CrossRefClient):
    def __init__(self, email: str):
        super().__init__(email)
        self.doi_database = {
            "attention is all you need": "10.5555/attention",
            "a study of deep learning": "10.5555/deeplearn"
        }

    def get_doi_for_entry(self, entry: Dict[str, Any]) -> Optional[str]:
        title = entry.get("title", "").lower()
        # CORRECTED: Prioritize exact matches for E2E tests
        for key, doi in self.doi_database.items():
            if fuzz.ratio(title, key) > 95:
                return doi
        # Fallback for randomized tests
        if "random paper" in title or "a study of" in title:
            return f"10.9999/{uuid.uuid4().hex[:6]}" if random.random() < 0.75 else None
        return None
