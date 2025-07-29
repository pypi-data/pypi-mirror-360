# ==============================================================================
# File: bib_ami/reconciler.py
# New class responsible for deduplication and merging user data.
# ==============================================================================

# ==============================================================================
# File: bib_ami/reconciler.py
# Updated to create a detailed audit trail for each merged record.
# ==============================================================================
from typing import Dict, List

from bibtexparser.bibdatabase import BibDatabase


class Reconciler:
    """Deduplicates entries and merges metadata."""

    def __init__(self, fuzzy_threshold=95):
        self.fuzzy_threshold = fuzzy_threshold

    @staticmethod
    def deduplicate(database: BibDatabase) -> (BibDatabase, int):
        initial_count = len(database.entries)
        doi_map: Dict[str, List[Dict]] = {}
        no_doi_entries: List[Dict] = []
        for entry in database.entries:
            doi = entry.get('verified_doi')
            if doi:
                doi_key = doi.lower()
                if doi_key not in doi_map:
                    doi_map[doi_key] = []
                doi_map[doi_key].append(entry)
            else:
                no_doi_entries.append(entry)
        reconciled = []
        for group in doi_map.values():
            winner = max(group, key=len)
            notes = {e.get('note') for e in group if e.get('note')}
            if notes:
                winner['note'] = " | ".join(sorted(list(notes)))
            reconciled.append(winner)
        reconciled.extend(no_doi_entries)
        database.entries = reconciled
        duplicates_removed = initial_count - len(reconciled)
        return database, duplicates_removed
