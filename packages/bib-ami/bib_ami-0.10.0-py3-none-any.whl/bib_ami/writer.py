# ==============================================================================
# File: bib_ami/writer.py
# New class responsible for writing output files.
# ==============================================================================
from pathlib import Path
from typing import Dict, Any

from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


class Writer:
    """Writes BibDatabase objects to .bib files with audit comments."""

    @staticmethod
    def _format_audit_comment(entry: Dict[str, Any]) -> str:
        audit_info = entry.get('audit_info', {})
        status = audit_info.get('status', 'Unknown')
        changes = audit_info.get('changes', [])
        comment = f"% bib-ami STATUS: {status}\n"
        comment += f"% bib-ami CHANGES: {'; '.join(changes) if changes else 'No changes made.'}\n"
        return comment

    @staticmethod
    def _clean_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = entry.copy()
        if cleaned.get('verified_doi'):
            cleaned['doi'] = cleaned['verified_doi']
        for field in ['verified_doi', 'source_file', 'audit_info']:
            if field in cleaned:
                del cleaned[field]
        return cleaned

    def write_files(self, verified_db: BibDatabase, suspect_db: BibDatabase, output_file: Path, suspect_file: Path):
        writer = BibTexWriter()
        writer.indent = '  '
        writer.add_trailing_comma = True

        def dump_with_comments(db: BibDatabase, file_handle):
            for entry in db.entries:
                comment = self._format_audit_comment(entry)
                cleaned_entry = self._clean_entry(entry)
                temp_db = BibDatabase()
                temp_db.entries = [cleaned_entry]
                file_handle.write(comment)
                file_handle.write(writer.write(temp_db))
                file_handle.write("\n")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("% bib-ami output: Verified and Accepted Entries\n\n")
            dump_with_comments(verified_db, f)
        if suspect_db.entries:
            with open(suspect_file, 'w', encoding='utf-8') as f:
                f.write("% bib-ami output: Suspect Entries Requiring Manual Review\n\n")
                dump_with_comments(suspect_db, f)
