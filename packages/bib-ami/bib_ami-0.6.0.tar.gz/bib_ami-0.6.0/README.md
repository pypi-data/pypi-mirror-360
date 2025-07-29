# bib-ami

[![CircleCI](https://circleci.com/gh/hrolfrc/bib-ami.svg?style=shield)](https://circleci.com/gh/hrolfrc/bib-ami)
[![ReadTheDocs](https://readthedocs.org/projects/bib-ami/badge/?version=latest)](https://bib-ami.readthedocs.io/en/latest/)
[![Codecov](https://codecov.io/gh/hrolfrc/bib-ami/branch/master/graph/badge.svg)](https://codecov.io/gh/hrolfrc/bib-ami)
[![DOI](https://zenodo.org/badge/1012755631.svg)](https://doi.org/10.5281/zenodo.15795717)

A Python tool to merge, deduplicate, and clean BibTeX files. It consolidates `.bib` files, removes duplicates, validates DOIs, scrapes missing DOIs using CrossRef/DataCite APIs, and refreshes metadata. Version 0.6.0 includes user-configurable email for CrossRef API Polite Pool access, correctness grouping with commented feedback, and a filter for validated entries, enhancing citation integrity for LaTeX, Zotero, and JabRef workflows.

## Installation

```bash
pip install bib-ami