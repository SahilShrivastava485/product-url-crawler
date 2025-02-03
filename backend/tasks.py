import asyncio
import json
import os
from celery import Celery
from aiohttp import ClientSession
from crawler.fetcher import fetch_html  # Import your updated fetch_html function
from crawler.parser import extract_product_urls_from_html, extract_product_urls_from_api  # Import parsing functions
from crawler.config import MAX_PRODUCT_LINKS

app = Celery('crawler', broker='redis://localhost:6379/0')

@app.task
def crawl_website(start_url):
    """Start crawling a website."""
    asyncio.run(fetch_all_pages(start_url))

async def fetch_all_pages(start_url):
    """Fetch pages and handle both pagination and infinite scroll dynamically."""
    collected_urls = set()
    current_url = start_url
    is_api_based = False

    # Create an aiohttp session for asynchronous requests
    async with ClientSession() as session:
        while current_url:
            print(f"Fetching: {current_url}")
            html_or_json = await fetch_html(session, current_url)
            
            if isinstance(html_or_json, dict):  # API-based infinite scroll
                products, next_page_token, next_url, next_offset = extract_product_urls_from_api(html_or_json)
                collected_urls.update(products)
                 # Decide next request method
                if next_page_token:
                    current_url = f"{start_url}?next_page_token={next_page_token}"
                elif next_url:
                    current_url = next_url
                elif next_offset:
                    current_url = f"{start_url}?offset={next_offset}"
                else:
                    break

            elif isinstance(html_or_json, str):  # Standard pagination (HTML)
                product_urls, next_page_url = extract_product_urls_from_html(html_or_json, current_url, collected_urls)
                collected_urls.update(product_urls)
                if not next_page_url:  # No next page link found
                    break
                # Update the URL to the next page
                current_url = next_page_url

            # Stop if we've reached the max limit of product URLs
            if len(collected_urls) >= MAX_PRODUCT_LINKS:
                break
    save_collected_urls_to_json(start_url, collected_urls)
    print(f"Collected {len(collected_urls)} product URLs.")
    return collected_urls

def save_collected_urls_to_json(start_url, collected_urls):
    """Save the collected URLs to a JSON file, updating the existing data."""
    file_path = "collected_urls.json"
    
    # Load existing data from the file, if it exists
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        data = {}

    # Update the data with the current URL and collected URLs
    data[start_url] = list(collected_urls)

    # Save the updated data back to the JSON file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
