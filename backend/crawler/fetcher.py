import random
from crawler.config import USER_AGENTS, CONCURRENT_REQUESTS
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

def fetch_html_selenium(url):
    """Fetch HTML using Selenium when http fails."""
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        asyncio.sleep(3) 
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
        await asyncio.sleep(random.uniform(1, 3))
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        for attempt in range(retries):
            try:
                async with session.get(url, headers=headers, timeout=1000) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        if "application/json" in content_type:
                            json_data = await response.json()
                            return json_data
                        else:
                            html_content = await response.text()
                            return html_content
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
                await asyncio.sleep(2)
    return None
