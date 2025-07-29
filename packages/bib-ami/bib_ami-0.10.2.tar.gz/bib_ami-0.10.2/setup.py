from setuptools import setup, find_packages

# Read README.md, with fallback if not found
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A tool to merge and clean BibTeX files."

setup(
    name="bib_ami",
    version="0.10.2",
    packages=find_packages(),
    install_requires=[
        "bibtexparser>=1.4.1",
        "requests>=2.31.0",
        "fuzzywuzzy>=0.18.0",
        "python-Levenshtein>=0.25.0",
    ],
    entry_points={
        "console_scripts": [
            # CORRECTED: Point to the main function in the __main__.py module
            # to make the package runnable as a command-line tool.
            "bib-ami = bib_ami.__main__:main",
        ],
    },
    author="Rolf Carlson",
    author_email="hrolfrc@gmail.com",
    description="A command-line tool for improving the integrity of BibTeX bibliographies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hrolfrc/bib-ami",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
