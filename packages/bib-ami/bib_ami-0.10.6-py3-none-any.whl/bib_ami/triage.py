"""
This module contains the Triage class, which is responsible for categorizing
processed BibTeX records based on their verification status.
"""

from bibtexparser.bibdatabase import BibDatabase


class Triage:
    """
    Categorizes records as Verified, Accepted, or Suspect.

    This class applies a set of rules to each processed record to determine
    its final status. This is the final classification step before the records
    are written to their respective output files.
    """

    @staticmethod
    def run_triage(
            database: BibDatabase, filter_validated: bool
    ) -> (BibDatabase, BibDatabase):
        """
        Separates a database into verified/accepted and suspect records.

        The logic is as follows:
        - Any entry with a verified DOI is always considered 'Verified'.
        - An entry without a DOI that is a book or report is considered 'Accepted'.
        - All other entries without a DOI are considered 'Suspect'.
        - If `filter_validated` is True, 'Accepted' entries are grouped with
          'Suspect' entries.

        Args:
            database: The BibDatabase object containing the processed entries.
            filter_validated: A boolean flag from the CLI that, if True,
                changes the triage logic to only allow 'Verified' entries
                in the main output file.

        Returns:
            A tuple containing two BibDatabase objects:
                - The first database contains 'Verified' and 'Accepted' records.
                - The second database contains 'Suspect' records.
        """
        verified_db, suspect_db = BibDatabase(), BibDatabase()

        for entry in database.entries:
            is_verified = bool(entry.get("verified_doi"))
            is_book_or_report = entry.get("ENTRYTYPE", "misc").lower() in [
                "book",
                "techreport",
            ]

            # Case 1: The entry has a verified DOI. It's always trustworthy.
            if is_verified:
                entry["audit_info"]["status"] = "Verified"
                verified_db.entries.append(entry)

            # Case 2: No DOI, but it's a type we accept without one (and not filtering).
            elif not filter_validated and is_book_or_report:
                entry["audit_info"]["status"] = "Accepted (No DOI)"
                verified_db.entries.append(entry)

            # Case 3: All other entries are considered suspect.
            # This includes articles without DOIs, or accepted types when filtering is on.
            else:
                entry["audit_info"]["status"] = "Suspect"
                suspect_db.entries.append(entry)

        return verified_db, suspect_db
