import requests
import re
import random
from urllib.parse import urlparse
from crawler.config import COMMON_PATTERNS, USER_AGENTS, COMMON_URLS
import xml.etree.ElementTree as ET

def infer_patterns_from_urls():
    """Infer product URL patterns dynamically from known URLs."""
    patterns = set()

    for url in COMMON_URLS:
        parsed = urlparse(url)
        segments = parsed.path.split("/")
        for segment in segments:
            if segment and (segment.isdigit() or len(segment) > 2):  # Detect slugs or IDs
                patterns.add(f"/{segment}/")

    return list(patterns)


def extract_patterns_from_robots(domain):
    """Fetch robots.txt and extract possible product path patterns."""
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    robots_url = f"{domain}/robots.txt"
    response = requests.get(robots_url,headers=headers,timeout=1000)

    if response.status_code != 200:
        return []

    patterns = set()
    for line in response.text.split("\n"):
        if line.startswith("Allow: "):
            rule = line.split(":")[1].strip()
            if re.search(r'/[a-zA-Z0-9_-]+/', rule):
                patterns.add(rule)

    return list(patterns)

def extract_patterns_from_sitemap(domain):
    """Fetch sitemap.xml and extract possible product path patterns."""
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    sitemap_url = f"{domain}/sitemap.xml"
    try:
        response = requests.get(sitemap_url,headers=headers,timeout=1000)
    except Exception:
        return []
    if response.status_code != 200:
        return []
    response.encoding = 'utf-8'
    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as e:
        print(f"Error at line {e.position[0]}, column {e.position[1]}: {e}")
        return []

    urls = [elem.text for elem in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]

    patterns = set()
    for url in urls:
        parts = url.split("/")
        for part in parts:
            if part.isdigit() or len(part) > 2:  # Detect product IDs or slugs
                patterns.add(f"/{part}/")

    return list(patterns)

def generate_combined_patterns(domain):
    """Generate product URL patterns using multiple sources."""
    patterns = set(COMMON_PATTERNS)  # Start with common patterns

    # Extract patterns dynamically
    patterns.update(infer_patterns_from_urls())
    patterns.update(extract_patterns_from_robots(domain))
    patterns.update(extract_patterns_from_sitemap(domain))
    return list(patterns)



