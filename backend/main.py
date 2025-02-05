from tasks import crawl_website  # Import from the outer location
from crawler.pattern_extractor import generate_combined_patterns

domains = [
    "https://www.amazon.in/",
    "https://www.flipkart.com/",
    "https://www.snapdeal.com/",
    "https://store.steampowered.com/",
    "https://www.bigbasket.com/",
    "https://www.lenskart.com/",
    "https://www.reliancedigital.in/",
    "https://www.ajio.com/",
    "https://www.titan.co.in/",
    "https://www.ujam.com/",
]

for domain in domains:
    crawl_website.delay(domain)
