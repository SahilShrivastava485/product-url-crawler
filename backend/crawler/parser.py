from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin
from crawler.config import MAX_PRODUCT_LINKS
from crawler.pattern_extractor import generate_combined_patterns
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def has_infinite_scroll(html):
    soup = BeautifulSoup(html, 'html.parser')
    load_more = soup.find(['button', 'a'], string=re.compile(r'load more', re.I))
    inf_scroll_scripts = soup.find_all('script', src=re.compile(r'infinite[-\s]?scroll', re.I))
    inline_js = soup.find_all('script', string=re.compile(r'scroll|addEventListener\(["\']scroll', re.I))
    has_infinite_scroll = load_more or inf_scroll_scripts or inline_js

    if has_infinite_scroll:
        return True
    else:
        return False

def extract_product_urls_with_selenium(url, max_scrolls=5):
    """Extract product URLs from an infinite scrolling e-commerce page using Selenium + BeautifulSoup."""
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(2) 

        for _ in range(max_scrolls):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(2)
        html = driver.page_source
    finally:
        driver.quit()
    soup = BeautifulSoup(html, "lxml")
    product_urls = set()

    for link in soup.select("a.product-link"):
        url = link.get("href")
        if url:
            product_urls.add(url)

    return product_urls

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

    next_page_url = None
    next_page_button = soup.find("a", {"class": "next"})
    if next_page_button:
        next_page_url = urljoin(base_url, next_page_button.get("href"))

    if(has_infinite_scroll(html)):
        print('has infinite scroll')
        new_urls = extract_product_urls_with_selenium(url=base_url)
        product_urls.update(new_urls)
    return product_urls, next_page_url


def extract_product_urls_from_api(json_data):
    """Extract product URLs from API response and determine next page information."""
    print("Contains Infinite Scrolling")
    products = set()
    next_url = None
    next_page_token = None
    next_offset = None

    for key in ["products", "items", "results", "data"]:
        if key in json_data and isinstance(json_data[key], list):
            for product in json_data[key]:
                product_url = product.get("url") or product.get("link") or product.get("product_url")
                if product_url:
                    products.add(product_url)

    if "next_page_token" in json_data:
        next_page_token = json_data["next_page_token"]
    elif "next" in json_data:  
        next_url = json_data["next"]
    elif "offset" in json_data:
        next_offset = json_data["offset"] + len(products)
    elif json_data.get("has_more"):  
        next_offset = json_data.get("offset", 0) + len(products)
    time.sleep(1)  
    return products, next_page_token, next_url, next_offset
