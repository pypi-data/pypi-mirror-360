"""
This module contains the Writer class, which is responsible for writing the
processed BibTeX databases to their final output files.
"""
from pathlib import Path
from typing import Dict, Any

from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


class Writer:
    """
    Writes BibDatabase objects to .bib files with a full audit trail.

    This class handles the final "Load" phase of the workflow. It takes the
    triaged databases, formats the audit information for each entry into
    human-readable comments, cleans up internal processing fields, and writes
    the final, clean records to the appropriate output files.
    """

    @staticmethod
    def _format_audit_comment(entry: Dict[str, Any]) -> str:
        """
        Creates a formatted comment block from an entry's audit trail.

        Args:
            entry: The BibTeX entry dictionary, which is expected to contain
                an 'audit_info' dictionary.

        Returns:
            A formatted, multi-line string containing the status and changes,
            ready to be written as a comment to the .bib file.
        """
        audit_info = entry.get("audit_info", {})
        status = audit_info.get("status", "Unknown")
        changes = audit_info.get("changes", [])

        comment = f"% bib-ami STATUS: {status}\n"
        comment += (
            f"% bib-ami CHANGES: {'; '.join(changes) if changes else 'No changes made.'}\n"
        )
        return comment

    @staticmethod
    def _clean_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Removes internal processing fields from an entry before writing.

        This ensures that the final .bib file does not contain any temporary
        or internal keys (e.g., 'verified_doi', 'audit_info'). It also promotes
        the verified DOI to the final 'doi' field.

        Args:
            entry: The entry dictionary to clean.

        Returns:
            A new dictionary containing only the standard BibTeX fields.
        """
        cleaned = entry.copy()
        # Promote the verified DOI to the standard 'doi' field.
        if cleaned.get("verified_doi"):
            cleaned["doi"] = cleaned["verified_doi"]

        # Remove all fields used for internal processing.
        for field in ["verified_doi", "source_file", "audit_info"]:
            if field in cleaned:
                del cleaned[field]
        return cleaned

    def write_files(
            self,
            verified_db: BibDatabase,
            suspect_db: BibDatabase,
            output_file: Path,
            suspect_file: Path,
    ):
        """
        Writes the verified and suspect databases to their respective files.

        Args:
            verified_db: A BibDatabase containing the 'Verified' and 'Accepted' entries.
            suspect_db: A BibDatabase containing the 'Suspect' entries.
            output_file: The path to the main output file for verified records.
            suspect_file: The path to the output file for suspect records.
        """
        writer = BibTexWriter()
        writer.indent = "  "
        writer.add_trailing_comma = True

        def dump_with_comments(db: BibDatabase, file_handle):
            """A helper function to write entries with preceding audit comments."""
            for entry in db.entries:
                # Generate the audit comment block for the entry.
                comment = self._format_audit_comment(entry)
                # Clean the entry of internal fields.
                cleaned_entry = self._clean_entry(entry)

                # Use a temporary database to format and write one entry at a time.
                temp_db = BibDatabase()
                temp_db.entries = [cleaned_entry]

                file_handle.write(comment)
                file_handle.write(writer.write(temp_db))
                file_handle.write("\n")

        # Write the main output file for verified and accepted entries.
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("% bib-ami output: Verified and Accepted Entries\n\n")
            dump_with_comments(verified_db, f)

        # Write the suspect file only if there are suspect entries.
        if suspect_db.entries:
            with open(suspect_file, "w", encoding="utf-8") as f:
                f.write(
                    "% bib-ami output: Suspect Entries Requiring Manual Review\n\n"
                )
                dump_with_comments(suspect_db, f)
