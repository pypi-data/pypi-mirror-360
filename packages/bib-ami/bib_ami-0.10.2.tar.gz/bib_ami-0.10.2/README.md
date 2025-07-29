#  bib-ami

[![CircleCI](https://circleci.com/gh/hrolfrc/bib-ami.svg?style=shield)](https://circleci.com/gh/hrolfrc/bib-ami)
[![ReadTheDocs](https://readthedocs.org/projects/bib-ami/badge/?version=latest)](https://bib-ami.readthedocs.io/en/latest/)
[![Codecov](https://codecov.io/gh/hrolfrc/bib-ami/branch/master/graph/badge.svg)](https://codecov.io/gh/hrolfrc/bib-ami)
[![DOI](https://zenodo.org/badge/1012755631.svg)](https://doi.org/10.5281/zenodo.15795717)

## A Bibliography Integrity Manager

**bib-ami** is a command-line tool for improving the integrity of BibTeX bibliographies. It automates a critical data cleaning and entity resolution workflow by consolidating multiple `.bib` files, validating every entry against the CrossRef API to establish a canonical DOI, and then deduplicating records based on this verified identifier.

The tool intelligently categorizes entries as 'verified' or 'suspect', enabling researchers to build a clean, reliable, and auditable bibliography for their LaTeX, Zotero, or JabRef workflows.

## Key Features

* **Merge & Consolidate:** Combines multiple `.bib` files from a directory into a single source.
* **Validate & Enrich:** Validates every entry against the CrossRef API to find and correct its canonical DOI.
* **Deduplicate with Confidence:** Uses verified DOIs as the primary key for accurate deduplication, with a fuzzy-matching fallback for entries without a DOI.
* **Intelligent Triage:** Automatically separates high-confidence, verified records from questionable ones that require manual review.
* **Audit Trail:** Provides transparent reporting on the actions taken to clean the bibliography.

## Getting Started

### 1. Installation

Ensure you have Python 3.7+ installed. You can install `bib-ami` using pip:


    pip install bib-ami

### 2. Quick Start

To process a directory of `.bib` files, run the following command. You must provide an email address for the responsible use of the CrossRef API.

    bib-ami --input-dir path/to/your/bibs --output-file cleaned.bib --suspect-file suspect.bib --email "your.email@example.com"

This will produce two files:

* `cleaned.bib`: Contains the verified and accepted entries.
* `suspect.bib`: Contains entries that could not be verified and require manual review.
