# ==============================================================================
# File: bib_ami/reconciler.py
# New class responsible for deduplication and merging user data.
# ==============================================================================

# ==============================================================================
# File: bib_ami/reconciler.py
# Updated to create a detailed audit trail for each merged record.
# ==============================================================================

import logging
from typing import Dict, List

from bibtexparser.bibdatabase import BibDatabase
from fuzzywuzzy import fuzz

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Reconciler:
    """Deduplicates entries and merges metadata."""

    def __init__(self, fuzzy_threshold=95):
        self.fuzzy_threshold = fuzzy_threshold

    def deduplicate(self, database: BibDatabase) -> (BibDatabase, int):
        logging.info("--- Phase 3: Reconciling and Deduplicating Entries ---")
        initial_count = len(database.entries)

        # Pass 1: Deduplicate by verified DOI
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

        reconciled_entries: List[Dict] = []
        for group in doi_map.values():
            winner = max(group, key=len)
            notes = {e.get('note') for e in group if e.get('note')}
            if notes:
                winner['note'] = " | ".join(sorted(list(notes)))
            reconciled_entries.append(winner)

        # --- FUZZY MATCHING FALLBACK IMPLEMENTED HERE ---
        # Pass 2: Fuzzy deduplication for entries without a DOI
        unique_no_doi: List[Dict] = []
        for entry_to_check in no_doi_entries:
            is_duplicate = False
            for existing_entry in unique_no_doi:
                title_ratio = fuzz.ratio(
                    entry_to_check.get('title', '').lower(),
                    existing_entry.get('title', '').lower()
                )
                if title_ratio > self.fuzzy_threshold:
                    # Found a fuzzy duplicate. For simplicity, we discard the new one.
                    # A more advanced implementation could merge them.
                    logging.info(
                        f"Found fuzzy duplicate: '{entry_to_check.get('title')}' is similar to '{existing_entry.get('title')}'")
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_no_doi.append(entry_to_check)

        reconciled_entries.extend(unique_no_doi)

        database.entries = reconciled_entries
        duplicates_removed = initial_count - len(reconciled_entries)
        logging.info(f"Removed {duplicates_removed} duplicate entries.")
        return database, duplicates_removed
