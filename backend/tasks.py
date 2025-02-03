from celery import Celery
from aiohttp import ClientSession
import asyncio
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
                products, next_token = extract_product_urls_from_api(html_or_json)
                collected_urls.update(products)
                if not next_token:  # No more data to fetch
                    break
                # Update the API call parameters for the next page (e.g., using the next_token)
                current_url = f"{start_url}?next_token={next_token}"  # Example; adjust for your API

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

    print(f"Collected {len(collected_urls)} product URLs.")
    return collected_urls
