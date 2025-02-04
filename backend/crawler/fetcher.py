import aiohttp
import random
from crawler.config import USER_AGENTS, CONCURRENT_REQUESTS
from crawler.parser import extract_product_urls_from_html, extract_product_urls_from_api
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

def fetch_html_selenium(url):
    """Fetch HTML using Selenium when aiohttp fails."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        asyncio.sleep(3)  # Allow JavaScript to load
        html_content = driver.page_source
        return html_content
    except Exception as e:
        print(f"Selenium error: {e}")
        return None
    finally:
        driver.quit()

async def fetch_html(session, url, retries=3, backoff_factor=1.5):
    """Fetch HTML content from the provided URL."""
    async with semaphore:
        await asyncio.sleep(random.uniform(1, 3))  # Delay before making the request
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        for attempt in range(retries):
            try:
                async with session.get(url, headers=headers, timeout=1000) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        if "application/json" in content_type:
                            # Handle API response
                            json_data = await response.json()
                            return json_data  # return JSON data directly for API-based infinite scrolling
                        else:
                            # Handle HTML content
                            html_content = await response.text()
                            return html_content  # return HTML for standard pagination
                    elif response.status in [429, 503]:
                        wait_time = backoff_factor ** attempt
                        print(f"Rate limit on {url}, retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    elif response.status in range(400,499):
                        print("can't access")
                        return fetch_html_selenium(url)
                    else:
                        print(response.status)
                        await asyncio.sleep(0)
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                await asyncio.sleep(2)  # Delay before retry
    return None

async def fetch_all_pages(session, start_url):
    """Fetch pages and handle both pagination and infinite scroll dynamically."""
    collected_urls = set()
    current_url = start_url

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

        elif isinstance(html_or_json, str):  # Standard pagination
            product_urls, next_page_url = extract_product_urls_from_html(html_or_json, current_url, collected_urls)
            collected_urls.update(product_urls)
            if not next_page_url:  # No next page link found
                break
            # Update the URL to the next page
            current_url = next_page_url

    return collected_urls
