# ==============================================================================
# File: bib_ami/validator.py
# New class responsible for using the API client to validate records.
# ==============================================================================

from bibtexparser.bibdatabase import BibDatabase

from .cross_ref_client import CrossRefClient


class Validator:
    """Validates each entry to find its canonical DOI."""

    def __init__(self, client: CrossRefClient):
        self.client = client

    def validate_all(self, database: BibDatabase) -> (BibDatabase, int):
        validated_count = 0
        for entry in database.entries:
            entry['verified_doi'] = self.client.get_doi_for_entry(entry)
            if entry['verified_doi']:
                validated_count += 1
        return database, validated_count
