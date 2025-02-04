from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin
from crawler.config import MAX_PRODUCT_LINKS
from crawler.pattern_extractor import generate_combined_patterns
import time

def extract_product_urls_from_html(html, base_url, collected_urls):
    """Extract product URLs from HTML content while respecting the max limit."""
    print("Contains Pagination")
    if not html or len(collected_urls) >= MAX_PRODUCT_LINKS:
        return set(), None

    soup = BeautifulSoup(html, "lxml")
    product_urls = set()
    extracted_patterns = generate_combined_patterns(base_url)
    for tag in soup.find_all(["a", "button", "div", "iframe"], href=True):
        full_url = urljoin(base_url, tag.get("href") or tag.get("data-href") or tag.get("src"))
        if any(re.search(pattern, full_url) for pattern in extracted_patterns):
            product_urls.add(full_url)
    
    meta_refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
    if meta_refresh:
        match = re.search(r"url=(.+)", meta_refresh["content"])
        if match:
            full_url = urljoin(base_url, match.group(1))
            product_urls.add(full_url)


    # Check for pagination (e.g., next page button or pagination links)
    next_page_url = None
    next_page_button = soup.find("a", {"class": "next"})  # Example; adjust to actual HTML structure
    if next_page_button:
        next_page_url = urljoin(base_url, next_page_button.get("href"))

    return product_urls, next_page_url

def extract_product_urls_from_api(json_data):
    """Extract product URLs from API response and determine next page information."""
    print("Contains Infinite Scrolling")
    products = set()
    next_url = None
    next_page_token = None
    next_offset = None

    # Handle different API structures
    for key in ["products", "items", "results", "data"]:
        if key in json_data and isinstance(json_data[key], list):
            for product in json_data[key]:
                product_url = product.get("url") or product.get("link") or product.get("product_url")
                if product_url:
                    products.add(product_url)

    # Handle different pagination methods
    if "next_page_token" in json_data:
        next_page_token = json_data["next_page_token"]
    elif "next" in json_data:  
        next_url = json_data["next"]  # Full URL for next page
    elif "offset" in json_data:
        next_offset = json_data["offset"] + len(products)  # Calculate next offset
    elif json_data.get("has_more"):  
        next_offset = json_data.get("offset", 0) + len(products)  # Continue if `has_more`

    # Introduce small delay to avoid rate-limiting
    time.sleep(1)  

    return products, next_page_token, next_url, next_offset
