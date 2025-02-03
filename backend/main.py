from tasks import crawl_website  # Import from the outer location

domains = [
    "https://www.amazon.in/"
]

for domain in domains:
    crawl_website.delay(domain)  # Asynchronous execution using Celery
