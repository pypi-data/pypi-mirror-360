import logging

import uuid
from typing import Dict, Any, Optional, Self

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ==============================================================================
# File: tests/fixtures/record_builder.py
# A factory for creating BibTeX record dictionaries for tests.
# ==============================================================================

class RecordBuilder:
    def __init__(self, entry_id: Optional[str] = None):
        self._record: Dict[str, Any] = {"ENTRYTYPE": "article", "ID": entry_id or f"rec_{uuid.uuid4().hex[:8]}"}

    def with_title(self, title: str) -> Self:
        self._record["title"] = title
        return self

    def with_author(self, author: str) -> Self:
        self._record["author"] = author
        return self

    def with_note(self, note: str) -> Self:
        self._record["note"] = note
        return self

    def as_book(self) -> Self:
        self._record["ENTRYTYPE"] = "book"
        return self

    def build(self) -> Dict[str, Any]:
        return self._record
