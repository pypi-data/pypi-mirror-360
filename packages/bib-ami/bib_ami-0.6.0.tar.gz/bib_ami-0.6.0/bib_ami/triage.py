# ==============================================================================
# File: bib_ami/triage.py
# New class responsible for classifying records.
# ==============================================================================
import logging

from bibtexparser.bibdatabase import BibDatabase


class Triage:
    """Categorizes records as Verified, Accepted, or Suspect."""

    @staticmethod
    def run_triage(database: BibDatabase, filter_validated: bool) -> (BibDatabase, BibDatabase):
        verified_db, suspect_db = BibDatabase(), BibDatabase()
        for entry in database.entries:
            if entry.get('verified_doi'):
                verified_db.entries.append(entry)
            elif entry.get('ENTRYTYPE', 'misc').lower() in ['book', 'techreport']:
                verified_db.entries.append(entry)  # Accepted
            else:
                suspect_db.entries.append(entry)  # Suspect
        return verified_db, suspect_db
