"""
This module contains the Validator class, responsible for verifying each
BibTeX entry against an authoritative external source.
"""
import logging
from bibtexparser.bibdatabase import BibDatabase

from .cross_ref_client import CrossRefClient


class Validator:
    """
    Validates each entry to find its canonical DOI.

    This class orchestrates the validation phase of the workflow. It uses an
    API client to query an external source for each entry and determines the
    authoritative DOI. It also initializes the audit trail for each entry.
    """

    def __init__(self, client: CrossRefClient):
        """
        Initializes the Validator.

        Args:
            client: An instance of an API client (e.g., CrossRefClient)
                that has a `get_doi_for_entry` method.
        """
        self.client = client

    def validate_all(self, database: BibDatabase) -> (BibDatabase, int):
        """
        Iterates through a database, validating each entry to find a DOI.

        For each entry, this method performs the following steps:
        1. Initializes an 'audit_info' dictionary to track changes.
        2. Queries the API client to get a verified DOI based on the entry's
           title and author.
        3. If a DOI is found, it's compared to any existing DOI. The audit
           trail is updated if a new DOI is added or an old one is corrected.
        4. A 'verified_doi' key is added to the entry, containing either the
           authoritative DOI or None if no match was found.

        Args:
            database: The BibDatabase object containing entries to process.

        Returns:
            A tuple containing:
                - The BibDatabase object with entries updated in place.
                - An integer count of the number of entries that were
                  successfully validated with a DOI.
        """
        logging.info("--- Phase 2a: Validating Entries with Authoritative Source ---")
        validated_count = 0
        for entry in database.entries:
            # Initialize the audit trail for this entry.
            entry["audit_info"] = {"changes": []}

            verified_doi = self.client.get_doi_for_entry(entry)

            if verified_doi:
                original_doi = entry.get("doi", "").lower()

                # Log changes to the audit trail.
                if not original_doi:
                    entry["audit_info"]["changes"].append(
                        f"Added new DOI [{verified_doi}]."
                    )
                elif original_doi != verified_doi.lower():
                    entry["audit_info"]["changes"].append(
                        f"Corrected DOI from [{original_doi}] to [{verified_doi}]."
                    )

                # Store the canonical DOI in a new field for internal processing.
                entry["verified_doi"] = verified_doi
                validated_count += 1
            else:
                # Mark entries that could not be verified.
                entry["verified_doi"] = None

        logging.info(f"Successfully validated {validated_count} entries with a DOI.")
        return database, validated_count
