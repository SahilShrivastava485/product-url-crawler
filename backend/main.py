from tasks import crawl_website  # Import from the outer location
from crawler.pattern_extractor import generate_combined_patterns

domains = [
    "https://www.amazon.in/",
    "https://www.flipkart.com/",
    "https://www.myntra.com/",
    "https://www.snapdeal.com/",
    "https://store.steampowered.com/",
    "https://www.bigbasket.com/",
    "https://www.lenskart.com/",
    "https://www.nykaa.com/",
    "https://www.reliancedigital.in/",
    # "https://www.blinkit.com/"
]

for domain in domains:
    # patterns = generate_combined_patterns(domain)
    # print(f'{domain}:{patterns}')
    crawl_website.delay(domain)  # Asynchronous execution using Celery
