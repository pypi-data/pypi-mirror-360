from bibtexparser.bibdatabase import BibDatabase


# noinspection SpellCheckingInspection
class Triage:
    """Categorizes records as Verified, Accepted, or Suspect."""

    @staticmethod
    def run_triage(
        database: BibDatabase, filter_validated: bool
    ) -> (BibDatabase, BibDatabase):
        verified_db, suspect_db = BibDatabase(), BibDatabase()
        for entry in database.entries:
            is_verified = bool(entry.get("verified_doi"))
            is_book_or_report = entry.get("ENTRYTYPE", "misc").lower() in [
                "book",
                "techreport",
            ]
            if is_verified:
                entry["audit_info"]["status"] = "Verified"
                verified_db.entries.append(entry)
            elif not filter_validated and is_book_or_report:
                entry["audit_info"]["status"] = "Accepted (No DOI)"
                verified_db.entries.append(entry)
            else:
                entry["audit_info"]["status"] = "Suspect"
                suspect_db.entries.append(entry)
        return verified_db, suspect_db
