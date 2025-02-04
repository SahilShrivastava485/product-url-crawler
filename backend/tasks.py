import asyncio
import json
import os
from celery import Celery
from aiohttp import ClientSession
from crawler.fetcher import fetch_html
from crawler.parser import extract_product_urls_from_html, extract_product_urls_from_api, extract_product_urls_with_selenium
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

    async with ClientSession() as session:
        while current_url:
            print(f"Fetching: {current_url}")
            html_or_json = await fetch_html(session, current_url)
            
            if isinstance(html_or_json, dict):
                products, next_page_token, next_url, next_offset = extract_product_urls_from_api(html_or_json)
                collected_urls.update(products)
                products = extract_product_urls_with_selenium(url=current_url)
                collected_urls.update(products)
                if next_page_token:
                    current_url = f"{start_url}?next_page_token={next_page_token}"
                elif next_url:
                    current_url = next_url
                elif next_offset:
                    current_url = f"{start_url}?offset={next_offset}"
                else:
                    break

            elif isinstance(html_or_json, str):
                product_urls, next_page_url = extract_product_urls_from_html(html_or_json, current_url, collected_urls)
                collected_urls.update(product_urls)
                if not next_page_url:
                    break
                current_url = next_page_url
            
            elif not html_or_json:
                break
            if len(collected_urls) >= MAX_PRODUCT_LINKS:
                break
    save_collected_urls_to_json(start_url, collected_urls)
    print(f"Collected {len(collected_urls)} product URLs.")
    return collected_urls

def save_collected_urls_to_json(start_url, collected_urls):
    """Save the collected URLs to a JSON file, updating the existing data."""
    file_path = "collected_urls.json"
    
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        data = {}

    data[start_url] = list(collected_urls)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
