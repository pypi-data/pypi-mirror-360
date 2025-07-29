# ==============================================================================
# File: bib_ami/triage.py
# New class responsible for classifying records.
# ==============================================================================

from bibtexparser.bibdatabase import BibDatabase


# noinspection SpellCheckingInspection
class Triage:
    """Categorizes records as Verified, Accepted, or Suspect."""

    @staticmethod
    def run_triage(database: BibDatabase, filter_validated: bool) -> (BibDatabase, BibDatabase):
        verified_db, suspect_db = BibDatabase(), BibDatabase()
        for entry in database.entries:
            is_verified = bool(entry.get('verified_doi'))
            is_book_or_report = entry.get('ENTRYTYPE', 'misc').lower() in ['book', 'techreport']

            if is_verified:
                verified_db.entries.append(entry)
            elif not filter_validated and is_book_or_report:
                # Accepted entries go to the main file if not filtering
                verified_db.entries.append(entry)
            else:
                # Suspect entries (and accepted ones when filtering) go to the suspect file
                suspect_db.entries.append(entry)
        return verified_db, suspect_db
