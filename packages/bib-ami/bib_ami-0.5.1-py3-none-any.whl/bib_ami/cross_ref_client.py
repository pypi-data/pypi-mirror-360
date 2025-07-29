import logging
from typing import Dict, Optional, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CrossRefClient:
    """
    A client for querying the CrossRef API to find and validate DOIs.

    This client uses a requests.Session for connection pooling and a robust
    retry strategy to handle transient network issues and API rate limits.
    """
    BASE_URL = "https://api.crossref.org/works"

    def __init__(self, email: str, timeout: int = 10, max_retries: int = 3):
        """
        Initializes the CrossRefClient.

        Args:
            email (str): Your email address, required by the CrossRef Polite Pool policy.
            timeout (int): The timeout in seconds for requests.
            max_retries (int): The maximum number of retries for failed requests.
        """
        if not email:
            raise ValueError("An email address is required for the CrossRef API's Polite Pool.")

        self.email = email
        self.timeout = timeout
        self.session = self._create_session(max_retries)

    def _create_session(self, max_retries: int) -> requests.Session:
        """Configures and returns a requests.Session with retry logic."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": f"bib-ami/1.0 (mailto:{self.email})",
            "Accept": "application/json"
        })

        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            respect_retry_after_header=True
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def get_doi_for_entry(self, entry: Dict[str, Any]) -> Optional[str]:
        """
        Queries CrossRef using metadata to find the most likely DOI for an entry.

        Args:
            entry (Dict[str, Any]): A dictionary representing a citation.

        Returns:
            Optional[str]: The found DOI or None.
        """
        title = entry.get("title")
        if not title:
            logging.warning(f"Entry with ID '{entry.get('ID', 'unknown')}' is missing a title for lookup.")
            return None

        params = {"query.title": title, "rows": 1}

        if "author" in entry and entry["author"]:
            first_author_lastname = entry["author"].split(",")[0].strip()
            params["query.author"] = first_author_lastname

        logging.info(f"Querying CrossRef for title: '{title}'")
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            items = data.get("message", {}).get("items", [])

            if items:
                doi = items[0].get("DOI")
                if doi:
                    logging.info(f"Found DOI {doi} for title: '{title}'")
                    return doi

            logging.warning(f"No DOI match found for title: '{title}'")
            return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for title '{title}': {e}")
            return None
