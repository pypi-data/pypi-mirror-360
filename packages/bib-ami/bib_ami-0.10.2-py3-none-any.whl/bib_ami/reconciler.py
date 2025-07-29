# ==============================================================================
# File: bib_ami/reconciler.py
# Updated to create a detailed audit trail for each merged record.
# ==============================================================================

from typing import Dict, Any, List

from bibtexparser.bibdatabase import BibDatabase
from fuzzywuzzy import fuzz


class Reconciler:
    """Deduplicates entries and merges metadata."""

    def __init__(self, fuzzy_threshold=95):
        self.fuzzy_threshold = fuzzy_threshold

    @staticmethod
    def _create_golden_record(group: List[Dict]) -> Dict[str, Any]:
        winner = max(group, key=len)
        golden_record = winner.copy()
        if "audit_info" not in golden_record:
            golden_record["audit_info"] = {"changes": []}
        if len(group) > 1:
            notes = {e.get("note") for e in group if e.get("note")}
            if len(notes) > 1:
                golden_record["note"] = " | ".join(sorted(list(notes)))
                golden_record["audit_info"]["changes"].append(
                    "Merged 'note' fields from duplicates."
                )
            merged_ids = [e["ID"] for e in group if e["ID"] != winner["ID"]]
            golden_record["audit_info"]["changes"].append(
                f"Merged with duplicate entries: {', '.join(merged_ids)}."
            )
        return golden_record

    def deduplicate(self, database: BibDatabase) -> (BibDatabase, int):
        initial_count = len(database.entries)
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
        reconciled = [
            self._create_golden_record(group) for group in doi_map.values()
        ]
        unique_no_doi: List[Dict] = []
        for entry_to_check in no_doi_entries:
            is_duplicate = False
            for existing_entry in unique_no_doi:
                if (
                    fuzz.ratio(
                        entry_to_check.get("title", "").lower(),
                        existing_entry.get("title", "").lower(),
                    )
                    > self.fuzzy_threshold
                ):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_no_doi.append(entry_to_check)
        reconciled.extend(unique_no_doi)
        database.entries = reconciled
        duplicates_removed = initial_count - len(reconciled)
        return database, duplicates_removed
