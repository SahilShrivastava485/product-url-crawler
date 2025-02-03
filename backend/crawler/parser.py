from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from crawler.config import PRODUCT_PATTERNS, MAX_PRODUCT_LINKS

def extract_product_urls_from_html(html, base_url, collected_urls):
    """Extract product URLs from HTML content while respecting the max limit."""
    if not html or len(collected_urls) >= MAX_PRODUCT_LINKS:
        return set(), None

    soup = BeautifulSoup(html, "lxml")
    product_urls = set()

    for link in soup.find_all("a", href=True):
        full_url = urljoin(base_url, link["href"])
        if any(re.search(pattern, full_url) for pattern in PRODUCT_PATTERNS):
            product_urls.add(full_url)
            if len(collected_urls) + len(product_urls) >= MAX_PRODUCT_LINKS:
                return product_urls, None  # Stop early if max limit is reached

    # Check for pagination (e.g., next page button or pagination links)
    next_page_url = None
    next_page_button = soup.find("a", {"class": "next"})  # Example; adjust to actual HTML structure
    if next_page_button:
        next_page_url = urljoin(base_url, next_page_button.get("href"))

    return product_urls, next_page_url


def extract_product_urls_from_api(json_data):
    """Extract product URLs from API response (JSON) and return the next page token if available."""
    products = set()
    next_token = None

    # Extract product data from the API response (adjust as per your API structure)
    for product in json_data.get("products", []):
        product_url = product.get("url")
        if product_url:
            products.add(product_url)

    # Check if there's a next token for the next API request (adjust as per your API response)
    next_token = json_data.get("next_page_token", None)

    return products, next_token
