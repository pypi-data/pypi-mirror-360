"""
ekho.scraper module
Provides a simple interface to the Ekho scraping service.
"""
import os
import requests

DEFAULT_ENDPOINT = os.getenv(
    "EKHO_SCRAPER_ENDPOINT", 
    "http://52.204.148.111:8000/scrape"
)
SUBPAGES_ENDPOINT = os.getenv(
    "EKHO_SUBPAGES_ENDPOINT",
    DEFAULT_ENDPOINT.replace("/scrape", "/subpages")
)

def scrape(url: str) -> dict:
    """
    Send a POST request to the Ekho scraping service with the given URL and return the JSON response.

    :param url: The URL to scrape.
    :return: Parsed JSON response from the service.
    :raises HTTPError: If the request fails with an HTTP error.
    """
    payload = {"url": url}
    response = requests.post(DEFAULT_ENDPOINT, json=payload)
    response.raise_for_status()
    return response.json()

def subpages(url: str) -> dict:
    """
    Send a POST request to the Ekho subpages service with the given URL and return the JSON response.

    :param url: The URL to extract subpages from.
    :return: Parsed JSON response from the service.
    :raises HTTPError: If the request fails with an HTTP error.
    """
    payload = {"url": url}
    response = requests.post(SUBPAGES_ENDPOINT, json=payload)
    response.raise_for_status()
    return response.json()
