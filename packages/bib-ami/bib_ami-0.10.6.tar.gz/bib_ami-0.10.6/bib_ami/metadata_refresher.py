"""
This module contains the MetadataRefresher class, responsible for enriching
BibTeX entries with authoritative metadata from an external source.
"""

import logging
from bibtexparser.bibdatabase import BibDatabase
from .cross_ref_client import CrossRefClient


class MetadataRefresher:
    """
    Refreshes BibTeX entry metadata using a verified DOI.

    This class takes a database of entries that have already been validated
    (i.e., have a 'verified_doi' field) and uses an API client to fetch
    the canonical metadata for each entry, updating it in place.
    """

    def __init__(self, client: CrossRefClient):
        """
        Initializes the MetadataRefresher.

        Args:
            client: An instance of an API client (e.g., CrossRefClient)
                that has a `get_metadata_by_doi` method.
        """
        self.client = client

    def refresh_all(self, database: BibDatabase) -> BibDatabase:
        """
        Iterates through a database and refreshes metadata for entries with a DOI.

        For each entry that has a 'verified_doi', this method fetches the full
        bibliographic record from the API and updates the entry's core fields
        (title, author, year, journal) only if the new data is valid. It also
        updates the entry's audit trail to reflect the changes.

        Args:
            database: The BibDatabase object containing entries to process.

        Returns:
            The same BibDatabase object with entries updated in place.
        """
        logging.info("--- Phase 2b: Refreshing Metadata from CrossRef ---")
        refreshed_count = 0
        for entry in database.entries:
            # Only attempt to refresh entries that have a verified DOI.
            if entry.get("verified_doi"):
                metadata = self.client.get_metadata_by_doi(
                    entry["verified_doi"]
                )
                if metadata:
                    changed = False
                    # Safely update core fields only if the new data is not empty.
                    for field in ["title", "author", "year", "journal"]:
                        new_value = metadata.get(field)
                        if new_value and entry.get(field) != new_value:
                            entry[field] = new_value
                            changed = True

                    # If any field was changed, update the audit trail.
                    if changed:
                        entry["audit_info"]["changes"].append(
                            "Refreshed metadata from CrossRef."
                        )
                        refreshed_count += 1

        logging.info(f"Refreshed metadata for {refreshed_count} entries.")
        return database
