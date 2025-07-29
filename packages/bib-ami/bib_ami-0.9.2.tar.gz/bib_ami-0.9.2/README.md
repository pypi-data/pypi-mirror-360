# bib-ami

[![CircleCI](https://circleci.com/gh/hrolfrc/bib-ami.svg?style=shield)](https://circleci.com/gh/hrolfrc/bib-ami)
[![ReadTheDocs](https://readthedocs.org/projects/bib-ami/badge/?version=latest)](https://bib-ami.readthedocs.io/en/latest/)
[![Codecov](https://codecov.io/gh/hrolfrc/bib-ami/branch/master/graph/badge.svg)](https://codecov.io/gh/hrolfrc/bib-ami)
[![DOI](https://zenodo.org/badge/1012755631.svg)](https://doi.org/10.5281/zenodo.15795717)

bib-ami is a command-line tool designed to improve the 
integrity of BibTeX bibliographies. It automates a critical data cleaning workflow by consolidating multiple .bib files, validating every entry against the CrossRef API to establish a canonical DOI, and then deduplicating records based on this verified identifier.

The tool intelligently triages entries into 'verified' and 'suspect' categories, separating high-confidence references from those requiring manual review. With a full command-line interface for filtering and configuration, bib-ami helps researchers create a clean, reliable, and auditable bibliography for their LaTeX, Zotero, or JabRef workflows.

## Installation

```bash
pip install bib-ami