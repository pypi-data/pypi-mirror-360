#!/usr/bin/env python3
"""bib_ami: A tool to consolidate and clean BibTeX files.

This script merges .bib files from a directory, deduplicates entries,
validates DOIs, scrapes DOIs for entries without them, refreshes metadata,
and generates a summary report.
"""

import argparse
import logging
from pathlib import Path
from typing import Dict, List

import bibtexparser
import requests
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter
from fuzzywuzzy import fuzz
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def merge_bib_files(input_dir: str, output_file: str) -> None:
    """Merge all .bib files from input_dir into a single output_file.

    Args:
        input_dir (str): Directory containing .bib files.
        output_file (str): Path to the output .bib file.
    """
    input_path = Path(input_dir)
    output_path = Path(output_file)

    if not input_path.is_dir():
        logger.error(f"Input directory '{input_dir}' does not exist or is not a directory.")
        raise ValueError(f"Invalid input directory: {input_dir}")

    bib_files = list(input_path.glob("*.bib"))
    if not bib_files:
        logger.warning(f"No .bib files found in '{input_dir}'.")
        return

    logger.info(f"Found {len(bib_files)} .bib files in '{input_dir}'.")

    with output_path.open("w", encoding="utf-8") as outfile:
        for bib_file in bib_files:
            logger.info(f"Processing '{bib_file}'...")
            try:
                with bib_file.open("r", encoding="utf-8") as infile:
                    content = infile.read()
                    outfile.write(content)
                    outfile.write("\n\n")
            except Exception as e:
                logger.error(f"Failed to read '{bib_file}': {e}")
                continue

    logger.info(f"Successfully merged {len(bib_files)} files into '{output_file}'.")


def load_bib_file(input_file: str) -> BibDatabase:
    """Load a BibTeX file into a BibDatabase object.

    Args:
        input_file (str): Path to the BibTeX file.

    Returns:
        BibDatabase: Parsed BibTeX database.
    """
    try:
        with Path(input_file).open("r", encoding="utf-8") as f:
            parser = bibtexparser.bparser.BibTexParser(common_strings=True)
            parser.ignore_nonstandard_types = False
            parser.homogenise_fields = True
            return bibtexparser.load(f, parser=parser)
    except Exception as e:
        logger.error(f"Failed to parse '{input_file}': {e}")
        raise


def deduplicate_bibtex(database: BibDatabase, similarity_threshold: int = 90) -> BibDatabase:
    """Deduplicate BibTeX entries based on title and author similarity.

    Args:
        database (BibDatabase): Input BibTeX database.
        similarity_threshold (int): Fuzzy matching threshold (0-100).

    Returns:
        BibDatabase: Deduplicated database.
    """
    entries = database.entries
    dedup_entries: List[Dict] = []
    seen_keys: set = set()
    duplicates_removed = 0

    for i, entry in enumerate(entries):
        if i in seen_keys:
            continue
        dedup_entries.append(entry)
        for j, other in enumerate(entries[i + 1:], start=i + 1):
            if j in seen_keys:
                continue
            title1 = entry.get("title", "").lower()
            title2 = other.get("title", "").lower()
            author1 = entry.get("author", "").lower()
            author2 = other.get("author", "").lower()
            title_score = fuzz.ratio(title1, title2)
            author_score = fuzz.ratio(author1, author2) if author1 and author2 else 100
            if title_score > similarity_threshold and author_score > similarity_threshold:
                seen_keys.add(j)
                duplicates_removed += 1
                # Prefer entry with DOI or more fields
                if "doi" in entry and "doi" not in other:
                    continue
                elif "doi" not in entry and "doi" in other:
                    dedup_entries[-1] = other
                elif len(entry) > len(other):
                    continue
                else:
                    dedup_entries[-1] = other

    logger.info(f"Removed {duplicates_removed} duplicate entries.")
    new_database = BibDatabase()
    new_database.entries = dedup_entries
    return new_database


def validate_doi(doi: str) -> bool:
    """Validate a DOI by checking if it resolves via CrossRef.

    Args:
        doi (str): DOI to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        response = requests.get(f"https://api.crossref.org/works/{doi}", timeout=5)
        return response.status_code == 200
    except RequestException as e:
        logger.warning(f"Failed to validate DOI '{doi}': {e}")
        return False


def scrape_doi(entry, timeout=15, max_retries=3):
    """
    Scrape DOI for a given BibTeX entry using CrossRef API with retries.

    Args:
        entry (dict): BibTeX entry dictionary.
        timeout (int): Timeout for API requests in seconds.
        max_retries (int): Maximum number of retries for failed requests.

    Returns:
        str or None: DOI if found, else None.
    """
    title = entry.get("title", "")
    if not title:
        logging.warning(f"No title found for entry {entry.get('ID', 'unknown')}")
        return None

    url = f"https://api.crossref.org/works?query.bibliographic={title}"
    headers = {"User-Agent": "bib-ami/0.2.2 (mailto:your.email@example.com)"}

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            items = data.get("message", {}).get("items", [])
            if items:
                return items[0].get("DOI")
            logging.warning(f"No DOI found for '{title}'")
            return None
        except requests.exceptions.Timeout:
            logging.warning(f"Attempt {attempt + 1} timed out for '{title}'")
            if attempt + 1 == max_retries:
                logging.warning(f"Failed to scrape DOI for '{title}' after {max_retries} attempts")
                return None
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request error for '{title}': {e}")
            if attempt + 1 == max_retries:
                logging.warning(f"Failed to scrape DOI for '{title}' after {max_retries} attempts")
                return None
    return None


def refresh_metadata(entry, doi, timeout=15, max_retries=3):
    """
    Refresh BibTeX entry metadata using CrossRef API with retries.

    Args:
        entry (dict): Original BibTeX entry.
        doi (str): DOI to fetch metadata for.
        timeout (int): Timeout for API requests in seconds.
        max_retries (int): Maximum number of retries for failed requests.

    Returns:
        dict: Updated BibTeX entry with refreshed metadata.
    """
    if not doi:
        return entry

    new_entry = entry.copy()
    url = f"https://api.crossref.org/works/{doi}"
    headers = {"User-Agent": "bib-ami/0.2.2 (mailto:your.email@example.com)"}

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            data = response.json().get("message", {})

            # Handle title (list or string)
            title = data.get("title", [entry.get("title", "")])
            new_entry["title"] = title[0] if isinstance(title, list) and title else title if isinstance(title, str) else entry.get("title", "")

            # Handle authors
            authors = data.get("author", [])
            if authors:
                author_list = [
                    f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in authors
                    if a.get("given") or a.get("family")
                ]
                new_entry["author"] = " and ".join(author_list) if author_list else entry.get("author", "")

            # Handle the journal (container-title, may be a list, string, or missing)
            container_title = data.get("container-title", entry.get("journal", ""))
            if isinstance(container_title, list):
                new_entry["journal"] = container_title[0] if container_title else entry.get("journal", "")
            else:
                new_entry["journal"] = container_title if container_title else entry.get("journal", "")

            # Handle year
            published = data.get("published", {}).get("date-parts", [[None]])[0][0]
            new_entry["year"] = str(published) if published else entry.get("year", "")

            new_entry["doi"] = doi
            return new_entry
        except requests.exceptions.Timeout:
            logging.warning(f"Attempt {attempt + 1} timed out for DOI {doi}")
            if attempt + 1 == max_retries:
                logging.warning(f"Failed to refresh metadata for DOI {doi} after {max_retries} attempts")
                return entry
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request error for DOI {doi}: {e}")
            if attempt + 1 == max_retries:
                logging.warning(f"Failed to refresh metadata for DOI {doi} after {max_retries} attempts")
                return entry
    return entry


# noinspection PyUnusedLocal
def process_bibtex(input_file: str, output_file: str) -> Dict:
    """Process BibTeX file: deduplicate, validate DOIs, scrape missing DOIs, refresh metadata.

    Args:
        input_file (str): Input BibTeX file.
        output_file (str): Output BibTeX file.

    Returns:
        Dict: Summary of changes (e.g., duplicates_removed, dois_added, dois_corrected).
    """
    summary = {
        "files_merged": 0,
        "duplicates_removed": 0,
        "dois_valid": 0,
        "dois_invalid": 0,
        "dois_added": 0,
        "entries_refreshed": 0,
    }

    # Load BibTeX file
    database = load_bib_file(input_file)
    summary["files_merged"] = 1  # Single file after merging

    # Deduplicate
    database = deduplicate_bibtex(database)
    summary["duplicates_removed"] = len(database.entries) - len(database.entries)  # Updated in deduplicate_bibtex

    # Extract and validate identifiers
    identifier_counts = {"doi": 0, "isbn": 0}
    invalid_dois = []
    for entry in database.entries:
        if "doi" in entry:
            identifier_counts["doi"] += 1
            if validate_doi(entry["doi"]):
                summary["dois_valid"] += 1
            else:
                summary["dois_invalid"] += 1
                invalid_dois.append(entry["ID"])
        if "isbn" in entry:
            identifier_counts["isbn"] += 1

    # Scrape DOIs for entries without them
    for entry in database.entries:
        if "doi" not in entry:
            doi = scrape_doi(entry)
            if doi:
                entry["doi"] = doi
                summary["dois_added"] += 1
                # Refresh metadata for newly added DOI
                entry = refresh_metadata(entry, doi)
                summary["entries_refreshed"] += 1
        elif entry["ID"] in invalid_dois:
            # Try to find a correct DOI for invalid ones
            doi = scrape_doi(entry)
            if doi and doi != entry["doi"]:
                entry["doi"] = doi
                summary["dois_added"] += 1
                entry = refresh_metadata(entry, doi)
                summary["entries_refreshed"] += 1

    # Write output
    writer = BibTexWriter()
    with Path(output_file).open("w", encoding="utf-8") as f:
        bibtexparser.dump(database, f, writer=writer)

    logger.info("Processing summary:")
    for key, value in summary.items():
        logger.info(f"{key.replace('_', ' ').title()}: {value}")
    logger.info(f"Identifier counts: {identifier_counts}")

    return summary


def main():
    """Parse command-line arguments and run bib-ami."""
    parser = argparse.ArgumentParser(
        description="Merge, deduplicate, and clean BibTeX files with DOI validation and metadata refreshing."
    )
    parser.add_argument(
        "--input-dir",
        default=".",
        help="Directory containing .bib files to merge (default: current directory)."
    )
    parser.add_argument(
        "--output-file",
        default="output.bib",
        help="Output file for processed BibTeX entries (default: output.bib)."
    )
    parser.add_argument(
        "--merge-only",
        action="store_true",
        help="Only merge .bib files without further processing."
    )
    args = parser.parse_args()

    try:
        if args.merge_only:
            merge_bib_files(args.input_dir, args.output_file)
        else:
            # Merge files first
            merge_bib_files(args.input_dir, "temp.bib")
            # Process the merged file
            process_bibtex("temp.bib", args.output_file)
            # Clean up the temporary file
            Path("temp.bib").unlink(missing_ok=True)
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        raise


if __name__ == "__main__":
    main()
