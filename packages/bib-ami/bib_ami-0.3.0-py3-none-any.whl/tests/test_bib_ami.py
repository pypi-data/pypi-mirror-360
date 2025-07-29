import tempfile
from pathlib import Path
from unittest.mock import patch

import bibtexparser
import requests

from bib_ami.bib_ami import merge_bib_files, load_bib_file, deduplicate_bibtex, validate_doi, scrape_doi, \
    refresh_metadata


# noinspection SpellCheckingInspection
def test_merge_bib_files():
    """Test merging multiple .bib files into a single output file."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        bib1 = Path(tmpdirname) / "test1.bib"
        bib2 = Path(tmpdirname) / "test2.bib"
        output = Path(tmpdirname) / "output.bib"

        with bib1.open("w", encoding="utf-8") as f:
            f.write("@article{test1, title={Test 1}}\n")
        with bib2.open("w", encoding="utf-8") as f:
            f.write("@article{test2, title={Test 2}}\n")

        merge_bib_files(tmpdirname, str(output))
        assert output.exists()
        with output.open("r", encoding="utf-8") as f:
            content = f.read()
            assert "@article{test1" in content
            assert "@article{test2" in content


# noinspection SpellCheckingInspection
def test_merge_bib_files_no_bib_files():
    """Test merge_bib_files with no .bib files in directory."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        output = Path(tmpdirname) / "output.bib"
        merge_bib_files(tmpdirname, str(output))
        assert not output.exists()


# noinspection SpellCheckingInspection,PyBroadException
def test_merge_bib_files_invalid_bib():
    """Test merge_bib_files with an invalid .bib file."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        bib1 = Path(tmpdirname) / "test1.bib"
        output = Path(tmpdirname) / "output.bib"
        with bib1.open("w", encoding="utf-8") as f:
            f.write("invalid BibTeX content")
        try:
            merge_bib_files(tmpdirname, str(output))
        except Exception:
            assert not output.exists()


# noinspection SpellCheckingInspection
def test_load_bib_file():
    """Test loading a BibTeX file into a BibDatabase."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        bib_file = Path(tmpdirname) / "test.bib"
        with bib_file.open("w", encoding="utf-8") as f:
            f.write("@article{test1, title={Test 1}, author={Smith, John}}\n")
        database = load_bib_file(str(bib_file))
        assert len(database.entries) == 1
        assert database.entries[0]["ID"] == "test1"
        assert database.entries[0]["title"] == "Test 1"


# noinspection SpellCheckingInspection
def test_load_bib_file_empty():
    """Test loading an empty BibTeX file."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        bib_file = Path(tmpdirname) / "test.bib"
        with bib_file.open("w", encoding="utf-8") as f:
            f.write("")
        database = load_bib_file(str(bib_file))
        assert len(database.entries) == 0


def test_deduplicate_bibtex():
    """Test deduplication of BibTeX entries."""
    database = bibtexparser.bibdatabase.BibDatabase()
    database.entries = [
        {"ID": "test1", "title": "Machine Learning", "author": "Smith, John", "ENTRYTYPE": "article"},
        {"ID": "test2", "title": "Machine Learning", "author": "Smith, John", "ENTRYTYPE": "article"},
        {"ID": "test3", "title": "Deep Learning", "author": "Doe, Jane", "ENTRYTYPE": "article"},
    ]
    dedup_database = deduplicate_bibtex(database, similarity_threshold=90)
    assert len(dedup_database.entries) == 2
    titles = {entry["title"] for entry in dedup_database.entries}
    assert titles == {"Machine Learning", "Deep Learning"}


@patch("bib_ami.bib_ami.requests.get")
def test_validate_doi_valid(mock_get):
    """Test validating a valid DOI."""
    mock_get.return_value.status_code = 200
    result = validate_doi("10.1000/xyz123")
    assert result is True


@patch("bib_ami.bib_ami.requests.get")
def test_validate_doi_invalid(mock_get):
    """Test validating an invalid DOI."""
    mock_get.return_value.status_code = 404
    result = validate_doi("10.1000/invalid")
    assert result is False


@patch("bib_ami.bib_ami.requests.get")
def test_validate_doi_timeout(mock_get):
    """Test DOI validation with a timeout error."""
    mock_get.side_effect = requests.exceptions.Timeout
    result = validate_doi("10.1000/xyz123")
    assert result is False


@patch("bib_ami.bib_ami.requests.get")
def test_scrape_doi_success(mock_get):
    """Test scraping a DOI from CrossRef."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "message": {"items": [{"DOI": "10.1000/xyz123"}]}
    }
    entry = {"title": "Machine Learning", "author": "Smith, John", "ID": "test1"}
    doi = scrape_doi(entry)
    assert doi == "10.1000/xyz123"


@patch("bib_ami.bib_ami.requests.get")
def test_scrape_doi_no_results(mock_get):
    """Test scraping DOI when no results are found."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"message": {"items": []}}
    entry = {"title": "Machine Learning", "author": "Smith, John", "ID": "test1"}
    doi = scrape_doi(entry)
    assert doi is None


@patch("bib_ami.bib_ami.requests.get")
def test_scrape_doi_timeout(mock_get):
    """Test scraping DOI with timeout and retries."""
    mock_get.side_effect = requests.exceptions.Timeout
    entry = {"title": "Machine Learning", "author": "Smith, John", "ID": "test1"}
    doi = scrape_doi(entry)
    assert doi is None


@patch("bib_ami.bib_ami.requests.get")
def test_refresh_metadata_success(mock_get):
    """Test refreshing metadata for an entry with a valid DOI."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "message": {
            "title": ["Updated Title"],
            "author": [{"given": "John", "family": "Smith"}],
            "container-title": ["Updated Journal"],
            "published": {"date-parts": [[2021]]},
        }
    }
    entry = {
        "ID": "test1",
        "title": "Old Title",
        "author": "Old Author",
        "journal": "Old Journal",
        "year": "2020",
        "ENTRYTYPE": "article",
    }
    updated_entry = refresh_metadata(entry, "10.1000/xyz123")
    assert updated_entry["title"] == "Updated Title"
    assert updated_entry["author"] == "John Smith"
    assert updated_entry["journal"] == "Updated Journal"
    assert updated_entry["year"] == "2021"
    assert updated_entry["doi"] == "10.1000/xyz123"


@patch("bib_ami.bib_ami.requests.get")
def test_refresh_metadata_missing_container_title(mock_get):
    """Test refreshing metadata when container-title is missing."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "message": {
            "title": ["Updated Title"],
            "author": [{"given": "John", "family": "Smith"}],
            "published": {"date-parts": [[2021]]},
        }
    }
    entry = {
        "ID": "test1",
        "title": "Old Title",
        "author": "Old Author",
        "journal": "Old Journal",
        "year": "2020",
        "ENTRYTYPE": "article",
    }
    updated_entry = refresh_metadata(entry, "10.1000/xyz123")
    assert updated_entry["title"] == "Updated Title"
    assert updated_entry["author"] == "John Smith"
    assert updated_entry["journal"] == "Old Journal"  # Fallback to an existing journal
    assert updated_entry["year"] == "2021"
    assert updated_entry["doi"] == "10.1000/xyz123"


@patch("bib_ami.bib_ami.requests.get")
def test_refresh_metadata_timeout(mock_get):
    """Test refreshing metadata with timeout and retries."""
    mock_get.side_effect = requests.exceptions.Timeout
    entry = {
        "ID": "test1",
        "title": "Old Title",
        "author": "Old Author",
        "journal": "Old Journal",
        "year": "2020",
        "ENTRYTYPE": "article",
    }
    updated_entry = refresh_metadata(entry, "10.1000/xyz123")
    assert updated_entry == entry  # Returns original entry on failure
