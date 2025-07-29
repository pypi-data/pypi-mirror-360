"""
This module contains the Reconciler class, which is responsible for
deduplicating BibTeX entries and merging user-specific metadata.
"""
import logging
from typing import Dict, Any, List

from bibtexparser.bibdatabase import BibDatabase
from fuzzywuzzy import fuzz


class Reconciler:
    """
    Deduplicates entries and merges metadata into a single "golden record".

    This class implements a two-pass deduplication strategy:
    1.  **DOI-based:** It first groups and merges entries that share the same
        verified DOI. This is the most reliable method of deduplication.
    2.  **Fuzzy Matching Fallback:** For entries that could not be verified
        with a DOI, it performs a second pass using fuzzy string matching
        on titles to find and remove likely duplicates.
    """

    def __init__(self, fuzzy_threshold=95):
        """
        Initializes the Reconciler.

        Args:
            fuzzy_threshold: The similarity score (0-100) required for
                two titles to be considered a duplicate during the fuzzy
                matching phase.
        """
        self.fuzzy_threshold = fuzzy_threshold

    @staticmethod
    def _create_golden_record(group: List[Dict]) -> Dict[str, Any]:
        """
        Merges a group of duplicate entries into a single golden record.

        It selects a "winner" from the group (the one with the most fields)
        and then merges user-specific data (like 'note') from all other
        duplicates into it. It also updates the audit trail.

        Args:
            group: A list of duplicate entry dictionaries.

        Returns:
            A single, merged "golden record" dictionary.
        """
        winner = max(group, key=len)
        golden_record = winner.copy()

        # Ensure the audit trail dictionary exists before modification.
        if "audit_info" not in golden_record:
            golden_record["audit_info"] = {"changes": []}

        if len(group) > 1:
            # Merge 'note' fields from all duplicates.
            notes = {e.get("note") for e in group if e.get("note")}
            if len(notes) > 1:
                golden_record["note"] = " | ".join(sorted(list(notes)))
                golden_record["audit_info"]["changes"].append(
                    "Merged 'note' fields from duplicates."
                )

            # Record which original entries were merged into this one.
            merged_ids = [e["ID"] for e in group if e["ID"] != winner["ID"]]
            golden_record["audit_info"]["changes"].append(
                f"Merged with duplicate entries: {', '.join(merged_ids)}."
            )
        return golden_record

    def deduplicate(self, database: BibDatabase) -> (BibDatabase, int):
        """
        Executes the full two-pass deduplication process.

        Args:
            database: The BibDatabase object containing entries to process.

        Returns:
            A tuple containing:
                - The BibDatabase object with duplicates removed.
                - An integer count of the number of duplicates that were removed.
        """
        initial_count = len(database.entries)

        # --- Pass 1: Deduplicate by verified DOI ---
        logging.info("Deduplicating entries based on verified DOI...")
        doi_map: Dict[str, List[Dict]] = {}
        no_doi_entries: List[Dict] = []
        for entry in database.entries:
            doi = entry.get("verified_doi")
            if doi:
                doi_key = doi.lower()
                if doi_key not in doi_map:
                    doi_map[doi_key] = []
                doi_map[doi_key].append(entry)
            else:
                no_doi_entries.append(entry)

        # Create golden records for all DOI-based groups.
        reconciled = [
            self._create_golden_record(group) for group in doi_map.values()
        ]

        # --- Pass 2: Fuzzy Matching Fallback ---
        logging.info("Performing fuzzy matching for entries without a DOI...")
        unique_no_doi: List[Dict] = []
        for entry_to_check in no_doi_entries:
            is_duplicate = False
            for existing_entry in unique_no_doi:
                # Compare titles for similarity.
                if (
                        fuzz.ratio(
                            entry_to_check.get("title", "").lower(),
                            existing_entry.get("title", "").lower(),
                        )
                        > self.fuzzy_threshold
                ):
                    is_duplicate = True
                    # A more advanced implementation could merge these fuzzy matches.
                    # For now, we keep the first one we see.
                    break
            if not is_duplicate:
                unique_no_doi.append(entry_to_check)

        reconciled.extend(unique_no_doi)
        database.entries = reconciled

        duplicates_removed = initial_count - len(reconciled)
        logging.info(f"Removed {duplicates_removed} duplicate entries.")
        return database, duplicates_removed
