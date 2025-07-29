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
            entry['audit_info'] = {"changes": []}
            verified_doi = self.client.get_doi_for_entry(entry)
            if verified_doi:
                original_doi = entry.get('doi', '').lower()
                if not original_doi:
                    entry['audit_info']['changes'].append(f"Added new DOI [{verified_doi}].")
                elif original_doi != verified_doi.lower():
                    entry['audit_info']['changes'].append(f"Corrected DOI from [{original_doi}] to [{verified_doi}].")
                entry['verified_doi'] = verified_doi
                validated_count += 1
            else:
                entry['verified_doi'] = None
        return database, validated_count
