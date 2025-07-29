# ==============================================================================
# File: bib_ami/writer.py
# New class responsible for writing output files.
# ==============================================================================
from pathlib import Path
from typing import Dict, Any

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


class Writer:
    """Writes BibDatabase objects to .bib files."""

    @staticmethod
    def _clean_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = entry.copy()
        if cleaned.get('verified_doi'):
            cleaned['doi'] = cleaned['verified_doi']
        for field in ['verified_doi', 'source_file']:
            if field in cleaned:
                del cleaned[field]
        return cleaned

    def write_files(self, verified_db: BibDatabase, suspect_db: BibDatabase, output_file: Path, suspect_file: Path):
        writer = BibTexWriter()
        verified_db.entries = [self._clean_entry(e) for e in verified_db.entries]
        with open(output_file, 'w', encoding='utf-8') as f:
            bibtexparser.dump(verified_db, f, writer)
        if suspect_db.entries:
            suspect_db.entries = [self._clean_entry(e) for e in suspect_db.entries]
            with open(suspect_file, 'w', encoding='utf-8') as f:
                bibtexparser.dump(suspect_db, f, writer)
